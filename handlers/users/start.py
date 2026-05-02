from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart, Text
from aiogram.types import ReplyKeyboardRemove
from loader import dp
from keyboards.default import registerKeyBoardButton
from utils import send_req
from data.config import username as USERNAME, password as PASSWORD, university_id as UNIVERSITY_ID
from data.config import university_name_uz, university_name_ru


@dp.message_handler(CommandStart(), state='*')
async def bot_start(message: types.Message, state: FSMContext):
    all_data = await state.get_data()
    token = all_data.get('token')
    start_count = all_data.get('start_count', 0) + 1
    date = message.date.strftime("%Y-%m-%d %H:%M:%S")
    username = message.from_user.username or message.from_user.full_name
    await state.update_data(start_count=start_count)
    language_uz = all_data.get('language_uz', False)

    if (1 < start_count < 3 or start_count > 8) and language_uz:
        await message.answer(f"@{username} start tugmasini qayta qayta bosish shart emas😅")
        return

    if token:
        user_info = await send_req.application_forms_me(token=token)
        have_application_form = user_info.get('haveApplicationForm', False)
        have_applied = user_info.get('haveApplied', False)
        have_education = user_info.get('haveEducation', False)
        have_previous_education = user_info.get('havePreviousEducation', False)

        if have_application_form and have_applied and (have_education or have_previous_education):
            await _handle_authenticated_user(message, state, token, date, username)
            return

    await _handle_new_user(message, state, date, username)


async def _handle_authenticated_user(message, state, token, date, username):
    get_djtoken = await send_req.djtoken(username=USERNAME, password=PASSWORD)
    access = get_djtoken.get('access')
    await state.update_data(access=access)
    user_chat_id = message.from_user.id

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
    except Exception:
        pass

    exam_info = await send_req.my_applications(token=token)
    exam = exam_info.get('exam', {})
    check_result = exam.get('exam_result')

    data = await state.get_data()
    language_uz = data.get('language_uz')
    language_ru = data.get('language_ru')

    if language_uz:
        kb = registerKeyBoardButton.menu if check_result is None else registerKeyBoardButton.menu_full
        await message.answer("🏠Asosiy sahifa", reply_markup=kb)
    elif language_ru:
        await message.answer("🏠Меню", reply_markup=registerKeyBoardButton.menu_ru)


async def _handle_new_user(message, state, date, username):
    await state.finish()
    get_djtoken = await send_req.djtoken(username=USERNAME, password=PASSWORD)
    access = get_djtoken.get('access')
    await state.update_data(access=access)
    user_chat_id = message.from_user.id

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
