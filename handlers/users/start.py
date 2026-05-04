import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart, Text
from aiogram.types import ReplyKeyboardRemove
from loader import dp
from keyboards.default import registerKeyBoardButton
from utils import send_req
from data.config import username as USERNAME, password as PASSWORD, university_id as UNIVERSITY_ID
from data.config import university_name_uz, university_name_ru

log = logging.getLogger("oxus_bot.start")


@dp.message_handler(CommandStart(), state='*')
async def bot_start(message: types.Message, state: FSMContext):
    chat_id = message.from_user.id
    log.info("[/start] chat_id=%s username=%s", chat_id, message.from_user.username)
    all_data = await state.get_data()
    token = all_data.get('token')
    start_count = all_data.get('start_count', 0) + 1
    date = message.date.strftime("%Y-%m-%d %H:%M:%S")
    username = message.from_user.username or message.from_user.full_name
    await state.update_data(start_count=start_count)
    language_uz = all_data.get('language_uz', False)
    log.info("[/start] step=state_loaded token=%s start_count=%s lang_uz=%s",
             bool(token), start_count, language_uz)

    if (1 < start_count < 3 or start_count > 8) and language_uz:
        log.info("[/start] step=spam_guard chat_id=%s", chat_id)
        await message.answer(f"@{username} start tugmasini qayta qayta bosish shart emas😅")
        return

    if token:
        log.info("[/start] step=fetching_application_forms_me chat_id=%s", chat_id)
        user_info = await send_req.application_forms_me(token=token)
        log.info("[/start] step=application_forms_me_got chat_id=%s status=%s",
                 chat_id, user_info.get('status_code'))
        have_application_form = user_info.get('haveApplicationForm', False)
        have_applied = user_info.get('haveApplied', False)
        have_education = user_info.get('haveEducation', False)
        have_previous_education = user_info.get('havePreviousEducation', False)

        if have_application_form and have_applied and (have_education or have_previous_education):
            log.info("[/start] step=route=authenticated chat_id=%s", chat_id)
            await _handle_authenticated_user(message, state, token, date, username)
            return

    log.info("[/start] step=route=new_user chat_id=%s", chat_id)
    await _handle_new_user(message, state, date, username)


async def _handle_authenticated_user(message, state, token, date, username):
    chat_id = message.from_user.id
    access = None
    log.info("[auth_user] step=djtoken_request chat_id=%s", chat_id)
    try:
        get_djtoken = await send_req.djtoken(username=USERNAME, password=PASSWORD)
        access = get_djtoken.get('access')
        log.info("[auth_user] step=djtoken_got chat_id=%s has_access=%s", chat_id, bool(access))
    except Exception as e:
        log.warning("[auth_user] step=djtoken_failed chat_id=%s err=%s", chat_id, e)
    await state.update_data(access=access)
    user_chat_id = message.from_user.id

    if access:
        try:
            log.info("[auth_user] step=create_user_profile chat_id=%s", chat_id)
            send_req.create_user_profile(
                token=access,
                chat_id=user_chat_id,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                pin=1,
                date=date,
                username=username,
                university_name=int(UNIVERSITY_ID),
            )
            log.info("[auth_user] step=create_user_profile_done chat_id=%s", chat_id)
        except Exception as e:
            log.warning("[auth_user] step=create_user_profile_failed chat_id=%s err=%s", chat_id, e)
    else:
        log.info("[auth_user] step=skipping_create_user_profile (no access token) chat_id=%s", chat_id)

    log.info("[auth_user] step=my_applications_request chat_id=%s", chat_id)
    exam_info = await send_req.my_applications(token=token)
    exam = exam_info.get('exam', {})
    check_result = exam.get('exam_result')
    log.info("[auth_user] step=my_applications_got chat_id=%s exam_result=%s",
             chat_id, check_result)

    data = await state.get_data()
    language_uz = data.get('language_uz')
    language_ru = data.get('language_ru')

    if language_uz:
        kb = registerKeyBoardButton.menu if check_result is None else registerKeyBoardButton.menu_full
        await message.answer("🏠Asosiy sahifa", reply_markup=kb)
    elif language_ru:
        await message.answer("🏠Меню", reply_markup=registerKeyBoardButton.menu_ru)
    log.info("[auth_user] step=done chat_id=%s", chat_id)


async def _handle_new_user(message, state, date, username):
    chat_id = message.from_user.id
    log.info("[new_user] step=state_finish chat_id=%s", chat_id)
    await state.finish()

    access = None
    log.info("[new_user] step=djtoken_request chat_id=%s", chat_id)
    try:
        get_djtoken = await send_req.djtoken(username=USERNAME, password=PASSWORD)
        access = get_djtoken.get('access')
        log.info("[new_user] step=djtoken_got chat_id=%s has_access=%s", chat_id, bool(access))
    except Exception as e:
        log.warning("[new_user] step=djtoken_failed chat_id=%s err=%s", chat_id, e)
    await state.update_data(access=access)
    user_chat_id = message.from_user.id

    if access:
        log.info("[new_user] step=create_user_profile chat_id=%s", chat_id)
        try:
            send_req.create_user_profile(
                token=access,
                chat_id=user_chat_id,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                pin=1,
                date=date,
                username=username,
                university_name=int(UNIVERSITY_ID),
            )
            log.info("[new_user] step=create_user_profile_done chat_id=%s", chat_id)
        except Exception as e:
            log.warning("[new_user] step=create_user_profile_failed chat_id=%s err=%s", chat_id, e)
    else:
        log.info("[new_user] step=skipping_create_user_profile (no access token) chat_id=%s", chat_id)

    log.info("[new_user] step=sending_language_prompt chat_id=%s", chat_id)
    await message.answer(
        f"🇺🇿 <b>Assalomu aleykum, {message.from_user.full_name.capitalize()}!</b>\n"
        f"Bu <i>{university_name_uz}</i> qabul boti. Tilni tanlang.\n\n"
        f"🇷🇺 <b>Здравствуйте, {message.from_user.full_name.capitalize()}!</b>\n"
        f"Это бот приемной комиссии <i>{university_name_ru}</i>. Выберите язык.",
        parse_mode='HTML',
        reply_markup=registerKeyBoardButton.language,
    )


@dp.message_handler(Text(equals='/restart'), state='*')
async def bot_restart(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Bot qayta ishga tushdi", reply_markup=ReplyKeyboardRemove())


@dp.message_handler(Text(equals='/admin'), state='*')
async def admin_command(message: types.Message):
    await message.answer(
        "Assalomu alaykum,\n\n"
        "Qo'llab-quvvatlash xizmati boti orqali texnik yordam va hujjat topshirishda yordam olishingiz mumkin. "
        "Qo'shimcha ma'lumot uchun administratorga murojaat qiling: "
        "<a href='https://t.me/universittet_qabul_admin_bot'>Admin</a>",
        parse_mode='HTML',
    )
