import os
import datetime
import aiofiles.os
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, ParseMode
)
from loader import dp
from utils import send_req
from states.personalData import ManualPersonalInfo, EducationData
from data.config import university_id as UNIVERSITY_ID, BOT_TOKEN
from handlers.users import collect_data, upload
from keyboards.default.registerKeyBoardButton import enter_button, enter_button_ru
from handlers.users.register import (
    error_message_birthday, error_date, error_document, accepted_document,
    error_pin, error_number, error_birthplace, wait_file_is_loading,
)
from texts.messages import t


def _lang(data: dict) -> str:
    return 'uz' if data.get('language_uz') else 'ru'


def _enter_button(lang: str):
    return enter_button if lang == 'uz' else enter_button_ru


@dp.message_handler(state=ManualPersonalInfo.personal_info)
async def send_welcome(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = _lang(data)
    photo_url = (
        "https://api.mentalaba.uz/logo/fca2fbf9-2511-4ac6-af41-305f29c8c577.jpg"
        if lang == 'uz'
        else "https://api.mentalaba.uz/logo/40765367-0927-4e4a-9ce2-d9ef417a071e.webp"
    )
    await message.bot.send_photo(
        chat_id=message.chat.id,
        photo=photo_url,
        caption=t('photo_request', lang),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=ReplyKeyboardRemove(),
    )
    await ManualPersonalInfo.image.set()


@dp.message_handler(
    state=ManualPersonalInfo.image,
    content_types=[types.ContentType.PHOTO, types.ContentType.DOCUMENT],
)
async def get_image(message: types.Message, state: FSMContext):
    from aiogram import Bot
    bot = Bot(token=BOT_TOKEN)

    data = await state.get_data()
    lang = _lang(data)
    token_ = data.get('token')
    download_dir = 'profile_images'

    if message.photo:
        try:
            file_id = message.photo[-1].file_id
            file_info = await bot.get_file(file_id)
            file_path = file_info.file_path
            local_file_path = os.path.join(download_dir, file_path)
            await bot.download_file(file_path, local_file_path)
            try:
                res_file = upload.upload_new_file(token=token_, filename=local_file_path)
                await state.update_data(image=res_file.json()['path'])
            except Exception as e:
                await message.reply(t('general_error', lang).format(error=str(e)))
            await message.reply(t('image_accepted', lang))
            await message.answer(t('enter_lastname', lang))
            await ManualPersonalInfo.lastname.set()
        except Exception:
            await message.reply(t('image_error', lang))

    else:
        try:
            document = message.document
            file_info = await bot.get_file(document.file_id)
            file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"
            await aiofiles.os.makedirs(download_dir, exist_ok=True)
            local_file_path = os.path.join(download_dir, document.file_name)
            await send_req.download_file(file_url, local_file_path)
            await message.answer(wait_file_is_loading, parse_mode='HTML', reply_markup=ReplyKeyboardRemove())
            try:
                res_file = upload.upload_new_file(token=token_, filename=local_file_path)
                await state.update_data(image=res_file.json()['path'])
            except Exception as e:
                await message.reply(t('file_processing_error', lang).format(error=str(e)))
        except Exception:
            await message.reply(t('image_error_doc', lang))
        await message.reply(t('image_accepted', lang))
        await message.answer(t('enter_lastname', lang))
        await ManualPersonalInfo.lastname.set()


@dp.message_handler(state=ManualPersonalInfo.lastname)
async def get_lastname(message: types.Message, state: FSMContext):
    lang = _lang(await state.get_data())
    await state.update_data(lastname=message.text.strip())
    await message.answer(t('enter_firstname', lang))
    await ManualPersonalInfo.firstname.set()


@dp.message_handler(state=ManualPersonalInfo.firstname)
async def get_firstname(message: types.Message, state: FSMContext):
    lang = _lang(await state.get_data())
    await state.update_data(firstname=message.text.strip())
    await message.answer(t('enter_thirdname', lang))
    await ManualPersonalInfo.thirdname.set()


@dp.message_handler(state=ManualPersonalInfo.thirdname)
async def get_thirdname(message: types.Message, state: FSMContext):
    lang = _lang(await state.get_data())
    await state.update_data(thirdname=message.text.strip())
    await message.answer(t('enter_document', lang))
    await ManualPersonalInfo.document.set()


@dp.message_handler(state=ManualPersonalInfo.document)
async def get_document(message: types.Message, state: FSMContext):
    lang = _lang(await state.get_data())
    document = message.text.strip().upper()
    serial, number = document[:2], document[2:]

    if not (len(serial) == 2 and serial.isalpha() and len(number) == 7 and number.isdigit()):
        await message.answer(error_document)
        await message.answer(t('enter_document_retry', lang))
        return

    await state.update_data(document=f'{serial}{number}')
    await message.answer(accepted_document)
    await message.answer(t('enter_birthdate', lang))
    await ManualPersonalInfo.birthdate.set()


@dp.message_handler(state=ManualPersonalInfo.birthdate)
async def get_birthdate(message: types.Message, state: FSMContext):
    lang = _lang(await state.get_data())
    birth_date = message.text.strip()
    parts = birth_date.split('-') if birth_date else None

    if not parts or len(parts) != 3:
        await message.answer(error_message_birthday)
        return

    y, m, d = parts
    if not (y.isdigit() and m.isdigit() and d.isdigit()):
        await message.answer(error_message_birthday)
        return

    year, month, day = int(y), int(m), int(d)
    if not (1 <= day <= 31 and 1 <= month <= 12 and 1800 < year < 2014):
        await message.answer(error_date)
        return

    await state.update_data(birthdate=birth_date)
    await message.answer(t('enter_pin', lang))
    await ManualPersonalInfo.pin.set()


@dp.message_handler(state=ManualPersonalInfo.pin)
async def get_pin(message: types.Message, state: FSMContext):
    lang = _lang(await state.get_data())
    pinfl = message.text.strip()
    if len(pinfl) != 14 or not pinfl.isdigit():
        await message.answer(error_pin)
        return
    await state.update_data(pin=pinfl)

    data = await state.get_data()
    lang = _lang(data)
    male = t('gender_male', lang)
    female = t('gender_female', lang)
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(KeyboardButton(male), KeyboardButton(female))
    await message.answer(t('select_gender', lang), reply_markup=keyboard)
    await ManualPersonalInfo.gender.set()


@dp.message_handler(
    lambda msg: msg.text not in ["Erkak", "Ayol", "Мужской", "Женский"],
    state=ManualPersonalInfo.gender,
)
async def gender_invalid(message: types.Message, state: FSMContext):
    lang = _lang(await state.get_data())
    await message.reply(t('gender_invalid', lang))


@dp.message_handler(
    lambda msg: msg.text in ["Erkak", "Ayol", "Мужской", "Женский"],
    state=ManualPersonalInfo.gender,
)
async def get_gender(message: types.Message, state: FSMContext):
    lang = _lang(await state.get_data())
    gender = "male" if message.text in ("Erkak", "Мужской") else "female"
    await state.update_data(gender=gender)
    await message.answer(t('enter_birthplace', lang), reply_markup=ReplyKeyboardRemove())
    await ManualPersonalInfo.birthplace.set()


@dp.message_handler(state=ManualPersonalInfo.birthplace)
async def get_birthplace(message: types.Message, state: FSMContext):
    lang = _lang(await state.get_data())
    birth_place = message.text.strip()
    if not birth_place:
        await message.answer(error_birthplace)
        return
    await state.update_data(birthplace=birth_place)
    await message.answer(t('enter_extranumber', lang))
    await ManualPersonalInfo.extranumber.set()


@dp.message_handler(state=ManualPersonalInfo.extranumber)
async def get_extranumber(message: types.Message, state: FSMContext):
    lang = _lang(await state.get_data())
    extra_num = message.text.strip()
    if not extra_num.isdigit() or len(extra_num) != 9:
        await message.answer(error_number)
        return
    await state.update_data(extranumber=f"+998{extra_num}")
    await message.answer(t('enter_email', lang))
    await ManualPersonalInfo.email.set()


@dp.message_handler(state=ManualPersonalInfo.email)
async def get_email(message: types.Message, state: FSMContext):
    email = message.text.strip().lower()
    data_obj = await state.get_data()
    lang = _lang(data_obj)

    if "@gmail.com" not in email:
        await message.answer(t('email_invalid', lang))
        return

    await state.update_data(email=email)
    data_obj = await state.get_data()

    token = data_obj.get('token')
    lastname = data_obj.get('lastname')
    firstname = data_obj.get('firstname')
    thirdname = data_obj.get('thirdname')
    document = data_obj.get('document')
    birthdate = data_obj.get('birthdate')
    pinfl = data_obj.get('pin')
    gender = data_obj.get('gender')
    birthplace = data_obj.get('birthplace')
    extranumber = data_obj.get('extranumber')
    image = data_obj.get('image')
    phone = data_obj.get('phone')

    get_current_user = await send_req.get_user_profile(
        chat_id=message.chat.id, university_id=UNIVERSITY_ID
    )
    chat_id_user = get_current_user['chat_id_user']

    await state.update_data(chat_id_user=chat_id_user, id_user=get_current_user['id'])

    date_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    await send_req.update_user_profile(
        university_id=UNIVERSITY_ID,
        chat_id=chat_id_user,
        phone=phone,
        first_name=firstname,
        last_name=lastname,
        pin=pinfl,
        username=message.from_user.username,
        date=date_now,
    )

    res_app_forms = send_req.application_form_manual(
        token, birthdate, birthplace, email, extranumber, firstname,
        gender, lastname, phone, image, pinfl, document, "manually", thirdname,
    )

    if res_app_forms.get('status_code') == 201:
        await message.answer(t('data_saved', lang), reply_markup=_enter_button(lang))
        res_me = await send_req.application_forms_me_new(token)
        if res_me.get('status_code') == 200:
            user_education_src = res_me['data'].get('user_education_src')
            if user_education_src is None:
                await EducationData.education_id.set()
            else:
                await EducationData.degree_id.set()
    else:
        await message.answer(t('data_not_saved', lang))
