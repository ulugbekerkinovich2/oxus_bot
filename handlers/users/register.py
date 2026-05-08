from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command,Text
import aiohttp
from utils import send_req
from utils.send_group import send_group
from loader import dp, bot
from states.personalData import PersonalData, EducationData
from states.personalData import ManualPersonalInfo
from aiogram.utils.exceptions import Throttled
from aiogram.types import ContentType
from data.config import throttling_time, domain_name
from pprint import pprint
from datetime import datetime
from handlers.users import collect_data, upload
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton,ReplyKeyboardRemove
import os
import aiofiles.os
from icecream import ic
import json


def _mask(s):
    if not s:
        return s
    s = str(s)
    if len(s) <= 8:
        return '***'
    return f"{s[:4]}...{s[-4:]}"
from keyboards.default.registerKeyBoardButton import yes_no,update_education_info
from keyboards.default.registerKeyBoardButton import enter_button, menu,register, menu_full
from data.config import username as USERNAME
from data.config import password as PASSWORD
from data.config import university_id as UNIVERSITY_ID
from data.config import BOT_TOKEN
from utils.converter_files import convert_heic_to_jpg

saved_message = "✅ <b>Ma'lumot saqlandi!</b>"
error_message_birthday = "🔴 Tug'ilgan kun noto'g'ri kiritildi. Sana formati: yyyy-oo-kk\nTug'ilgan kunni qayta kiriting"
error_date = "🔴 Tug'ilgan kun noto'g'ri kiritildi. Kiritilgan sana namunadagidek emas.\nTug'ilgan kunni qayta kiriting"
example_birthday = "Tug\'ilgan kuningingizni kiriting quyidagi formatda\nyyyy-oo-kk\n\nNamuna: 2005-03-21"
example_phone = "☎️ <b>Telefon raqamingizni yuboring</b>\n<i>Namuna: 998991234567</i>"
example_extra_phone = 'Siz bilan aloqaga chiqish uchun qo\'shimcha telefon raqam kiriting\n\nNamuna: +998991234567'
example_transkript_message = "✅ *Transkript nusxasini yuboring* \n(_Hajmi 5 MB dan katta bo'lmagan, .png, .jpg, .jpeg, .pdf faylni yuklang_"
example_diploma_message = "✅ *Diplom, shahodatnoma yoki ma’lumotnoma nusxasini yuboring* \n(_Hajmi 5 MB dan katta bo'lmagan, .png, .jpg, .jpeg, .pdf faylni yuklang_"
example_certification_message = "✅ *Chet tili sertifikat nusxasini yuboring* \n(_Hajmi 5 MB dan katta bo'lmagan, .png, .jpg, .jpeg, .pdf faylni yuklang_"
accepted_phone = "🟢 <b>Telefon raqamingiz qabul qilindi.</b> Telefon raqamingizga yuborilgan kodni kiriting"
accepted_birthday_saved_data = '🟢Tu\'gilgan kuningiz qabul qilindi. Ma\'lumotlaringiz muvaffaqiyatli saqlandi.'
error_message_phone = "🔴Telefon raqam no\'to\'g\'ri kiritildi, Namunadagidek raqam kiriting!"
accepted_phone_simple = "🟢Telefon raqamingiz qabul qilindi."
accepted_document = "🟢Passport seriyasi qabul qilindi"
example_document = "Passport seriyangizni yuboring\nNamuna: AB1234567"
error_document = "🔴Passport seriya noto'g'ri kiritildi"
error_secret_code = "🔴Tasdiqlash kodi noto'g'ri kiritildi"
error_type_edu_name = 'Talim dargoh nomini kiriting, bu majburiy.\nNamuna: Toshkent davlat iqtisodiyot universiteti'
error_document = "Passport seriyasi 2 ta harfdan  va 7 raqamdan iborat bo'lishi kerak.\nQayta passport seriyangizni kiriting"
select_region = "Ta'lim dargohi joylashgan shahar yoki viloyatni tanlang:"
select_degree = "<b>*Daraja tanlang:</b>"
select_direction = "Yo'nalish yoki mutaxassislikni tanlang:"
select_edu_type = "Ta'lim shaklini tanlang:"
select_edu_language = "Ta'lim tilini tanlang:"
select_type_certificate = "Sertifikat turini tanlang:"
select_country = "Ta’lim dargohi joylashgan davlatni tanlang:"
type_your_edu_name = "Avvalgi bitirgan yoki hozirgi ta'lim dargohi nomini kiriting:\nNamuna: Toshkent davlat iqtisodiyot universiteti"
wait_file_is_loading = "<b>Kuting, fayl yuklanmoqda.</b>"
retype_secret_code = "Tasdiqlash kodini qayta kiriting"
application_submited = 'Ariza muvaffaqiyatli topshirildi'
server_error = '🔴Ma\'lumotlaringizni markaziy ma\'lumotlar omboridan topolmadim\nMa\'lumotlaringizni kiritishingiz mumkin.'
error_pin = "🔴 JSHSHR 14 raqamdan iborat bolishi kerak"
error_number = "🔴 Telefon nomer 9ta raqamdan iborat bo'lishi kerak, Iltimos namunadagidek raqam kiriting"
error_birthplace = "🔴 Tug'ilgan joy noto'g'ri kiritildi"
search_university = "Mamlakat qisqa nomi yoki to'liq nomini kiriting: Namuna Amerika"
not_found_country = "🔴 Ma'lumot topilmadi, Iltimos qaytadan urinib ko'ring"
select_one = "Quyidagi mamlakatdan birini tanlang:"

@dp.message_handler(text="🇺🇿O'zbek tili")
async def uz_lang(message: types.Message, state: FSMContext):
    await state.update_data(language_uz=True, language_ru=False) 
    await message.answer("2025-2026-o'quv yili uchun ariza topshirish", reply_markup=register)


@dp.message_handler(text="🔄O'qishni ko'chirish")
async def transfer_edu(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    ic('uzb tanlandi')

    all_data_state = await state.get_data() 
    token = all_data_state.get('token', None)
    ic('token72', _mask(token))
    if token is None:
        button_phone = types.KeyboardButton(text='📲 Telefon raqamni yuborish', request_contact=True)
        keyboard.add(button_phone)
        await message.answer(example_phone, parse_mode="HTML",reply_markup=keyboard)
        await state.update_data(register_user=False, transfer_user=True)
        await PersonalData.phone.set()
    elif token is not None:
        check_token = await send_req.application_forms_me(token)
        check_exam = await send_req.my_applications(token)
        exam_status = check_exam.get('status')
        status_code = check_token.get('status_code')
        if status_code  == 200 and exam_status != 'came-exam':
            await message.answer("🏠Asosiy sahifa", reply_markup=menu)
        elif status_code  == 200 and exam_status == 'came-exam':
            await message.answer("🏠Asosiy sahifa", reply_markup=menu_full)
        elif status_code != 200:
            refreshToken = all_data_state.get('refresh_token')
            if refreshToken is not None:
                new_token = await send_req.return_token_use_refresh(refreshToken)
                ic(new_token)


@dp.message_handler(Text(equals="🧾Abiturient"))
async def my_application(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    ic('uzb tanlandi')

    all_data_state = await state.get_data() 
    token = all_data_state.get('token', None)
    ic('token72', _mask(token))
    if token is None:
        button_phone = types.KeyboardButton(text='📲 Telefon raqamni yuborish', request_contact=True)
        keyboard.add(button_phone)
        await message.answer(example_phone, parse_mode="HTML",reply_markup=keyboard)
        await state.update_data(register_user=True, transfer_user=False)
        await PersonalData.phone.set()
    elif token is not None:
        check_token = await send_req.application_forms_me(token)
        status_code = check_token.get('status_code')
        check_exam = await send_req.my_applications(token)
        exam_status = check_exam.get('status')
        if status_code  == 200 and exam_status != 'came-exam':
            await message.answer("🏠Asosiy sahifa", reply_markup=menu)
        elif status_code  == 200 and exam_status == 'came-exam':
            await message.answer("🏠Asosiy sahifa", reply_markup=menu_full)
        elif status_code != 200:
            refreshToken = all_data_state.get('refresh_token')
            if refreshToken is not None:
                new_token = await send_req.return_token_use_refresh(refreshToken)
                ic(new_token)

@dp.message_handler(state=PersonalData.phone, content_types=types.ContentTypes.CONTACT | types.ContentTypes.TEXT)
async def phone_contact_received(message: types.Message, state: FSMContext):
    # await message.answer(message.json())
    # ic(message)
    # ic(message.text)
    try:
        contact = message.contact
        phone_num = contact.phone_number
        ic('auto:', phone_num)
    except AttributeError:
        phone_num = None
        contact = None
    ic('next')
    try:
        custom_writened_phone = message.text
        ic(custom_writened_phone)
    except AttributeError:
        custom_writened_phone = None
    ic("custom_writened_phone", custom_writened_phone)
    # if contact is not None and phone_num is not None:
    ic(phone_num)
    ic('nomer keldi')
    if phone_num is not None:

        ic(phone_num, 100)
        ic(len(phone_num), 101)

        if str(phone_num)[0] != '+':
            phone_num = f"+{phone_num}"
            ic('plus qoshdi')
            if len(phone_num) == 13:
                custom_phone = phone_num
                ic(custom_phone, 102)
                check_user = await send_req.check_number(custom_phone)
                ic('check_user_new', check_user)
                ic(check_user)
                if check_user == 'true':
                    ic('check_user_for_true',check_user)
                    await state.update_data(phone=custom_phone)


                    user_login = await send_req.user_login(custom_phone)
                    
                    ic('user_login: ',user_login)
                    ic('user_login status: ',user_login.get('status_code'))
                    user_login_status = user_login.get('status_code')

                    if user_login_status == 200:
                        ic('user_login status',user_login_status)
                        remove_keyboard = types.ReplyKeyboardRemove()
                        await message.answer(accepted_phone, parse_mode='HTML', reply_markup=remove_keyboard)
                        await PersonalData.secret_code.set()
                    else:
                        await message.answer("Severda xatolik xatolik yuz berdi")
                # ic(check_user)
                elif check_user == 'false':
                    try:
                        ic('check_user_for_false', check_user)
                        await state.update_data(phone=custom_phone)
                        user_register = await send_req.user_register(custom_phone)
                        remove_keyboard = types.ReplyKeyboardRemove()
                        ic('user_register: ',user_register.status_code)
                        if user_register.status_code == 201:
                            await message.answer(accepted_phone, reply_markup=remove_keyboard)
                            await PersonalData.secret_code.set()
                    except:
                        ic('check_user_for_false', check_user)
                        await state.update_data(phone=custom_phone)
                        user_register = await send_req.user_register(custom_phone)
                        remove_keyboard = types.ReplyKeyboardRemove()
                        ic('user_register: ',user_register['status'])
                        if user_register['status'] == 200:
                            await message.answer(accepted_phone, reply_markup=remove_keyboard)
                            await PersonalData.secret_code.set()    

        elif len(phone_num) == 13:
            ic('plus bilan keldi')
            custom_phone = phone_num
            ic(custom_phone, 140)
            check_user = await send_req.check_number(custom_phone)
            ic('check_user_new', check_user)
            ic(check_user)
            if check_user == 'true':
                ic('check_user_for_true',check_user)
                await state.update_data(phone=custom_phone)


                user_login = await send_req.user_login(custom_phone)
                
                ic('user_login: ',user_login)
                ic('user_login status: ',user_login.get('status_code'))
                user_login_status = user_login.get('status_code')

                if user_login_status == 200:
                    ic('user_login status',user_login_status)
                    remove_keyboard = types.ReplyKeyboardRemove()
                    await message.answer(accepted_phone, parse_mode='HTML', reply_markup=remove_keyboard)
                    await PersonalData.secret_code.set()
                else:
                    await message.answer("severda xatolik yuz berdi")
            # ic(check_user)
            elif check_user == 'false':
                ic('check_user_for_false', check_user)
                await state.update_data(phone=custom_phone)
                user_register = await send_req.user_register(custom_phone)
                remove_keyboard = types.ReplyKeyboardRemove()
                ic('user_register: ',user_register)
                ic('data registeer', user_register['status'])
                # ic('user_register: ',user_register.status_code)
                try:
                    if user_register.status_code == 201:
                        await message.answer(accepted_phone, reply_markup=remove_keyboard)
                        await PersonalData.secret_code.set()
                except:
                    if user_register['status'] == 200:
                        await message.answer(accepted_phone, reply_markup=remove_keyboard)
                        await PersonalData.secret_code.set()



    elif custom_writened_phone is not None:
        custom_writened_phone = custom_writened_phone.strip()
        ic('custom_writened_phone: ',custom_writened_phone)
        status_while = True
        while status_while:
            ic('while ishladi')
            phone_num = custom_writened_phone.strip()
            if len(phone_num) != 12 or not phone_num.isdigit():
                await message.answer(error_message_phone)
                response_msg = await dp.bot.send_message(message.chat.id, "Iltimos, to'g'ri formatda telefon raqamni kiriting.")
                response = await dp.bot.wait_for("message")
                custom_writened_phone = message.text.strip() if response.text else None
                if custom_writened_phone:
                    phone_num = custom_writened_phone
                else:
                    break

            elif len(phone_num) == 12:
                ic('phone_num: 12talik',phone_num)
                status_while = False
                custom_phone = f'+{phone_num}'
                check_user = await send_req.check_number(custom_phone)
                ic('check_user', check_user)
                if str(check_user) == 'true':
                    await state.update_data(phone=custom_phone)
                    user_login = await send_req.user_login(custom_phone)
                    ic('user_login', user_login)
                    if user_login.get('status_code') == 200:
                        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
                        reset_pass_button = types.KeyboardButton(text='Kodni qayta yuborish')
                        keyboard.add(reset_pass_button)
                        await message.answer(accepted_phone_simple, reply_markup=ReplyKeyboardRemove())
                        await message.answer(" Telefon raqamingizga yuborilgan kodni yuboring", reply_markup=reset_pass_button)
                        await PersonalData.secret_code.set()
                    else:
                        await message.answer("935920479","severda xatolik 107")
                        await message.answer("Siz Ro'yhatdan o'tishingiz kerak")

                elif str(check_user) == 'false':
                    await state.update_data(phone=custom_phone)
                    user_register = await send_req.user_register(custom_phone)
                    ic('user_register', user_register)
                    if user_register.get('status') == 200:
                        await message.answer(accepted_phone, reply_markup=ReplyKeyboardRemove())
                        # await message.answer("Telefon raqamingizga yuborilgan kodni yuboring")
                        await PersonalData.secret_code.set()
                else:
                    await message.answer("severda xatolik yuz berdi 120")


@dp.message_handler(state=PersonalData.secret_code)
async def secret_code(message: types.Message, state: FSMContext):
    secret_code = message.text
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if len(secret_code) == 6 and secret_code.isdigit():
        data = await state.get_data()
        phone_number = f"{data.get('phone')}"
        # ic("phone->", phone_number)
        response_ = await send_req.user_verify(int(secret_code), phone_number)
        await state.update_data(user_verify=response_)
        res_status_code = response_.get('status_code')
        ic('response1111', response_)
        if response_.get('status_code') == 200:
            ic('kirdik333')
            # data_res = response_

            await state.update_data(token=response_.get('token'), refreshToken=response_.get('refreshToken'))
            data = await state.get_data()
            new_token_ = data.get('token')
            in_data = response_['data']
            # data_me_ = send_req.application_forms_me(new_token_)
            # data_me = data_me_.json()
            haveApplicationForm = in_data.get('haveApplicationForm')
            haveApplied = in_data.get('haveApplied')
            haveEducation = in_data.get('haveEducation')
            havePreviousEducation = in_data.get('havePreviousEducation')
            # ic(in_data)
            ic(haveApplicationForm)
            ic(haveApplied)
            ic(haveEducation)
            ic(havePreviousEducation)
            # ic(response_)
            ic(response_.get('status_code'))

            get_token = in_data.get('token')
            
            ic(get_token)
            # try:
            await state.update_data(token=get_token)
            get_djtoken = await send_req.djtoken(username=USERNAME, password=PASSWORD)
            access = get_djtoken.get('access')
            ic(access)
            await state.update_data(access=access)
            user_chat_id = message.from_user.id
            # ic(user_chat_id)
            date = message.date.strftime("%Y-%m-%d %H:%M:%S")
            # ic(date)
            username = message.from_user.username or message.from_user.full_name
            # ic(username)
            try:
                phone_number = await state.get_data('phone')
                ic(phone_number['phone'], '<----------------->\n<----------------->\n<----------------->')
                save_chat_id = send_req.create_user_profile(token=access, chat_id=user_chat_id, 
                                                                    first_name=message.from_user.first_name,
                                                                    last_name=message.from_user.last_name, 
                                                                    pin=1,date=date, username=username,
                                                                    university_name=int(UNIVERSITY_ID))
                # ic(save_chat_id)

                data = send_req.update_user_profile(university_id=UNIVERSITY_ID, 
                                            chat_id=user_chat_id,
                                            phone=phone_number, 
                                            pin=1,
                                            first_name=message.from_user.first_name,
                                            last_name=message.from_user.last_name,
                                            date=date,
                                            username=username)

            except Exception as err:
                ic(err)

            get_this_user =await send_req.get_user_profile(chat_id=user_chat_id, university_id=UNIVERSITY_ID)
            
            if haveApplicationForm is False and (haveEducation is False and  havePreviousEducation is False) and haveApplied is False:
                ic(338, 'keldi 1 chi if ga')
                await message.answer(example_document, reply_markup=ReplyKeyboardRemove())
                await state.update_data(haveApplicationForm=True,haveEducation=False,havePreviousEducation=False,haveApplied=False)
                await PersonalData.document.set()

            elif haveApplicationForm is True and (haveEducation is False and havePreviousEducation is False) and haveApplied is False:
                ic(344, 'keldi 2 chi if ga')
                await message.answer("<i>-✅Siz ro'yhatdan o'tgansiz.\n🔴Ta'lim ma'lumotlarini to'ldirishingiz kerak</i>",reply_markup=enter_button)
                await state.update_data(haveApplicationForm=True,haveEducation=False,havePreviousEducation=False,haveApplied=False)
                ic('002')
                await EducationData.education_id.set()

            elif haveApplicationForm is True and (haveEducation is True and havePreviousEducation is False) and haveApplied is False:
                ic(351, 'keldi 3 chi if ga')
                await message.answer("<i>- ✅ Siz ro'yhatdan o'tkansiz.\n- ✅ Ta'lim ma'lumotlaringiz ham to'ldirilgan.\n\nUniversitetga ariza topshirishingiz mumkin</i>", reply_markup=enter_button)
                await state.update_data(haveApplicationForm=True,haveEducation=True,havePreviousEducation=False,haveApplied=False)
                ic('keldi 003')
                await EducationData.degree_id.set()

            elif haveApplicationForm is True and (haveEducation is False and havePreviousEducation is True) and haveApplied is False:
                ic(358, 'keldi 4 chi if ga')
                await message.answer("<i>- ✅ Siz ro'yhatdan o'tkansiz.\n- ✅ Ta'lim ma'lumotlaringiz ham to'ldirilgan .\n\nUniversitetga ariza topshirishingiz mumkin</i>", reply_markup=enter_button)
                await state.update_data(haveApplicationForm=True,haveEducation=False,havePreviousEducation=True,haveApplied=False)
                ic('keldi 003')
                await EducationData.degree_id.set()

            elif haveApplicationForm is True and (haveEducation is True or havePreviousEducation is True) and haveApplied is True:
                ic(365, 'keldi 4 chi if ga')
                check_exam = await send_req.my_applications(token=get_token)
                exam = check_exam.get('exam')
                check_result = None
                exam_status = check_exam.get('status')
                if exam != {}:
                    ic(exam)
                    check_result = exam['exam_result']
                    # if check_result is not None:
                    
                    if exam_status == "came-exam" or check_result is not None :

                        await message.answer("<i>-✅Siz ro'yhatdan o'tkansiz\n-✅Ta'lim ma'lumotlaringiz ham to'ldirilgan,\n-✅Universitetga ham ariza topshirgansiz.</i>", reply_markup=menu_full)
                        ic('keldi 004')
                        await state.update_data(haveApplicationForm=True,haveEducation=False,havePreviousEducation=True,haveApplied=False)
                        ic('keldi 005')
                        await EducationData.menu.set()
                    else:
                        await message.answer("<i>-✅Siz ro'yhatdan o'tkansiz\n-✅Ta'lim ma'lumotlaringiz ham to'ldirilgan,\n-✅Universitetga ham ariza topshirgansiz.</i>", reply_markup=menu)
                        ic('keldi 0015')
                        await state.update_data(haveApplicationForm=True,haveEducation=False,havePreviousEducation=True,haveApplied=False)
                        ic('keldi 0016')
                        await EducationData.menu.set()
                elif exam == {}:
                    if exam_status != "came-exam":
                        await message.answer("<i>-✅Siz ro'yhatdan o'tkansiz\n-✅Ta'lim ma'lumotlaringiz ham to'ldirilgan,\n-✅Universitetga ham ariza topshirgansiz.</i>", reply_markup=menu)
                        ic('keldi 006')
                        await state.update_data(haveApplicationForm=True,haveEducation=False,havePreviousEducation=True,haveApplied=False)
                        ic('keldi 007')
                        await EducationData.menu.set()



        
        elif res_status_code == 404 or res_status_code == 400 or res_status_code == 410:
            ic('\nres666',res_status_code, '\n')
            await message.answer(error_secret_code)
            await dp.bot.send_message(message.chat.id, retype_secret_code)
            await dp.bot.wait_for("message")
            # ic(response.text)
    else:
        await message.answer(error_secret_code)

    # remove_keyboard_ = types.ReplyKeyboardRemove()
    await state.update_data(secret_code=secret_code)



@dp.message_handler(state=PersonalData.document)
async def document(message: types.Message, state: FSMContext):
    document = message.text.strip().upper()
    document_serial = document[:2]
    document_number = document[2:]

    while True:
        # Check if the serial and number parts are valid
        if len(document_serial) == 2 and document_serial.isalpha() and len(document_number) == 7 and document_number.isdigit():
            formatted_document = f'{document_serial}{document_number}'
            await state.update_data(document=formatted_document)
            break  # Exit loop if the document is valid
        
        # Handle invalid input
        await message.answer(error_document)
        
        # Wait for a new user message as a response
        new_document = await message.answer("Passport seriyasini namunadagidek kiriting\nNamuna: AB1234567:")
        document = (await dp.bot.wait_for("message")).text.strip().upper()
        document_serial = document[:2]
        document_number = document[2:]

    # After validation loop
    await message.answer(accepted_document)
    await message.answer(example_birthday)
    await PersonalData.birth_date.set()


@dp.message_handler(state=PersonalData.birth_date)
async def birth_date(message: types.Message, state: FSMContext):
    import logging,asyncio
    ic('birth date')
    birth_date = message.text.strip()
    await state.update_data(birth_date=birth_date)
    # Check if the birth date format is valid
    birth_date_parts = birth_date.split('-') if birth_date else None
    # print('birth_date', birth_date_parts)
    if not birth_date_parts or len(birth_date_parts) != 3:
        await message.answer(error_message_birthday)
        return

    check_year, check_month, check_day = birth_date_parts
    if not (check_day.isdigit() and check_month.isdigit() and check_year.isdigit()):
        await message.answer(error_message_birthday)
        return

    year, month, day = map(int, birth_date_parts)
    ic(day, month, year)
    if not ((1 <= day <= 31) and (1 <= month <= 12) and (2010 > year > 1800)):
        await message.answer(error_date)
        return
    

    data_state = await state.get_data()
    token = data_state.get('token')
    document = data_state.get('document')
    birth_date = data_state.get('birth_date')

    logging.info(f'birth_date: {birth_date}')
    logging.info(f'document: {document}')
    await state.update_data(birth_date_new=birth_date)
    await state.update_data(document_new=document)

    # Inform the user that the bot is processing their request
    await message.answer("<b>Ma'lumotlaringizni ma'lumotlar omboridan izlamoqdaman 90 soniyagacha vaqt olishi mumkin.</b>", parse_mode="HTML")
    msg = await message.reply("Iltimos kuting...")

    # Perform the data check concurrently with the timer
    check_is_not_duplicate_future = asyncio.create_task(send_req.application_form_info(birth_date, document, token))

    # Start 90-second timer
    for i in range(90, 0, -1):
        await asyncio.sleep(1)
        
        # Check if the data check is complete and its status code
        if check_is_not_duplicate_future.done():
            check_is_not_duplicate = await check_is_not_duplicate_future
            if check_is_not_duplicate.get('status_code') == 200:
                await bot.edit_message_text("Ma'lumotlar topildi!", chat_id=msg.chat.id, message_id=msg.message_id, parse_mode="HTML")
                break
            elif check_is_not_duplicate.get('status_code') == 409:
                ress_mess = check_is_not_duplicate['data']
                ic(ress_mess)
                await bot.edit_message_text(ress_mess, chat_id=msg.chat.id, message_id=msg.message_id, parse_mode="HTML")
                break
            elif check_is_not_duplicate.get('status_code') in [500, 404, 400, 406, 408]:
                await bot.edit_message_text("Xatolik yuz berdi, iltimos qayta urinib ko'ring.", chat_id=msg.chat.id, message_id=msg.message_id, parse_mode="HTML")
                break

        # Update the message with the remaining time
        try:
            await bot.edit_message_text(f"<i>Qoldi vaqt: {i} sekund</i>", chat_id=msg.chat.id, message_id=msg.message_id, parse_mode="HTML")
        except Exception as e:
            logging.error(f"Xatolik yuz berdi: {e}")

    # Notify user when timer is done
    await bot.edit_message_text("Vaqt tugadi!", chat_id=msg.chat.id, message_id=msg.message_id)


    # Retrieve the result of the data check if not already done
    if not check_is_not_duplicate_future.done():
        check_is_not_duplicate = await check_is_not_duplicate_future

    
    
    ic(check_is_not_duplicate)

    ic(check_is_not_duplicate.get('status_code'), type(check_is_not_duplicate.get('status_code')))
    status_code_ = check_is_not_duplicate.get('status_code')
    ic(473)
    if status_code_ in [500,404,400,504]:
        await message.answer(server_error, reply_markup=enter_button)
        await ManualPersonalInfo.personal_info.set()
    elif status_code_ == 409:
        error_mes = check_is_not_duplicate.get('data')
        ic(error_mes)
        start_button = KeyboardButton('/start')  # The text on the button
        start_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(start_button)
        
        await message.answer(f"🔴 {error_mes.get('message')}",reply_markup=start_keyboard)
        await state.finish()

    # data_res = check_is_not_duplicate['data']
    # ic(check_is_not_duplicate)
    # if check_is_not_duplicate.get('status_code') == 409 or check_is_not_duplicate.get('status_code') == 401 or check_is_not_duplicate.get('status_code') == 400:
    #     # error_mes = data_res.get('message')
    #     await message.answer(f"🔴 {error_mes}")
    #     await state.finish()
    elif check_is_not_duplicate.get('status_code') == 200:
        await state.update_data(birth_date=birth_date)
        await message.answer(accepted_birthday_saved_data)
        formatted_birth_date = f'{year}-{month}-{day}'
        await state.update_data(formatted_birth_date=formatted_birth_date)
        await message.answer(example_extra_phone, reply_markup=ReplyKeyboardRemove())
        await PersonalData.info.set()

   


@dp.message_handler(state=PersonalData.info)
async def info(message: types.Message, state: FSMContext):
    extra_phone = message.text.strip()
    # ic('extra_phone', extra_phone)
    data = await state.get_data()
    ic('state ga saqlanganlar-->', data)
    formatted_birth_date = data.get('formatted_birth_date')
    document = data.get('document')
    new_token = data.get('new_token')
    token = data.get('token')
    ic('new_token', _mask(new_token))
    ic('token', _mask(token))
    # first_name = data.get('first_name')
    # last_name = data.get('last_name')
    phone = data.get('phone')
    ic(formatted_birth_date)
    date_obj = datetime.strptime(formatted_birth_date, "%Y-%m-%d")
    formatted_date_str = date_obj.strftime("%Y-%m-%d")

    ic('-->',formatted_date_str,document)
    response = await send_req.application_form_info(formatted_date_str,document,token)
    await state.update_data(application_form_info=response)
    data = response['data']
    ic(response)
    ic(data)
    # if response.get('status_code') == 409:
    #     await message.answer(response.get('message'))
    #     await state.finish()
    # else:
    data_res = data.get('passport', {})
    first_name = data_res.get('first_name', '')
    last_name = data_res.get('last_name', '')
    application_id = data_res.get('applicant_id', '')  # Note the key is 'applicant_id' based on your response
    third_name = data_res.get('third_name', '')
    document = data_res.get('document') if isinstance(data_res.get('document'), dict) else {}


    birth_country = data_res.get('birth_country', '')
    birth_country_id = data_res.get('birth_country_id', 0)
    birth_date = data_res.get('birth_date', '')
    birth_place = data_res.get('birth_place', '')
    citizenship = data_res.get('citizenship', '')
    gender = data_res.get('gender', '')
    photo = data_res.get('photo', '')
    pin = data_res.get('pin', [None])[0]
    await state.update_data(
        birth_date=birth_date,
        document=document,
    )
    
    docgiveplace = document.get('docgiveplace', '')
    docgiveplaceid = document.get('docgiveplaceid', 0)
    datebegin = document.get('datebegin', '')
    dateend = document.get('dateend', '')
    passort_serial = document.get('document')
    src = 'manually'
    user_datas = {
        "application_id": application_id,
        "birth_country": birth_country,
        "birth_country_id": birth_country_id,
        "birth_date": birth_date,
        "birth_place": birth_place,
        "citizenship": citizenship,
        "gender": gender,
        "photo": photo,
        "pin": pin,
        "document": document,
        "docgiveplace": docgiveplace,
        "docgiveplaceid": docgiveplaceid,
        "datebegin": datebegin,
        "dateend": dateend,
        "first_name": first_name,
        "last_name": last_name,
        "third_name": third_name,
        "src": src
    }
    ic(user_datas)
    await state.update_data(**user_datas)

    print('shu doc info', passort_serial)

    "def application_form(token, src, district_id, education_id, file_vs_format, institution_name, region_id):"

    response_application_form = send_req.application_form(token,
                                                        birth_date,
                                                        birth_place,
                                                        citizenship,
                                                        extra_phone,
                                                        first_name,
                                                        gender,
                                                        last_name,
                                                        phone,
                                                        photo,
                                                        pin,
                                                        passort_serial,
                                                        src,
                                                        third_name
                                                        )
    # ic(response_application_form.json())
    ic('keldi2022')
    data_me = await collect_data.collect_me_data(token, field_name=None)
    # ic(data_me)
    if response_application_form.status_code == 201:
        ic('keldi app formdan', response_application_form.status_code)
        application_data_res = response_application_form.json()
        application_id = application_data_res.get('applicant_id', '')
        application_src = application_data_res.get('application_src', '')
        user_education_src = application_data_res.get('user_education_src', '')
        which_level_need = application_data_res.get('which_level_need', '')
        country_id = application_data_res.get('country_id', '')
        country_name_uz = application_data_res.get('country_name_uz', '')
        country_name_ru = application_data_res.get('country_name_ru', '')
        country_name_en = application_data_res.get('country_name_ru', '')
        region_id = application_data_res.get('region_id', '')
        region_name_uz = application_data_res.get('region_name_uz', '')
        region_name_ru = application_data_res.get('region_name_ru', '')
        region_name_en = application_data_res.get('region_name_en', '')
        district_id = application_data_res.get('district_id', '')
        district_name_uz = application_data_res.get('district_name_uz', '')
        district_name_ru = application_data_res.get('district_name_ru', '')
        district_name_en = application_data_res.get('district_name_en', '')
        address = application_data_res.get('address','')
        father_name = application_data_res.get('father_name', '')
        father_phone = application_data_res.get('father_phone', '')
        mother_name = application_data_res.get('mother_name', '')
        pinfl_birth_country = application_data_res.get('pinfl_birth_country', '')
        pinfl_birth_country_id = application_data_res.get('pinfl_birth_country_id', '')
        created_at = application_data_res.get('created_at', '')
        pinfl_user_education = application_data_res.get('pinfl_user_education', '')
        user_education = application_data_res.get('user_education', '')
        certifications = application_data_res.get('certifications', [])
        data_obj_applications = {
            'application_src': application_src,
            'which_level_need': which_level_need,
            'user_education_src': user_education_src,
            'country_id': country_id,
            'country_name_uz': country_name_uz,
            'country_name_ru': country_name_ru,
            'country_name_en': country_name_en,
            'region_id': region_id,
            'region_name_uz': region_name_uz,
            'region_name_ru': region_name_ru,
            'region_name_en': region_name_en,
            'district_id': district_id,
            'district_name_uz': district_name_uz,
            'district_name_ru': district_name_ru,
            'district_name_en': district_name_en,
            'address': address,
            'father_name': father_name,
            'father_phone': father_phone,
            'mother_name': mother_name,
            'pinfl_birth_country': pinfl_birth_country,
            'pinfl_birth_country_id': pinfl_birth_country_id,
            'created_at': created_at,
            'pinfl_user_education': pinfl_user_education,
            'user_education': user_education,
            'certifications': certifications,
        }
        date_now= datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await state.update_data(**data_obj_applications)
        # await message.answer("Ta'lim malumotlarini kiriting")

        await message.answer("Ta'lim ma'lumotlarini saqlash uchun davom etish tugmasini bosing", reply_markup=enter_button)
        ic('davom etish bosildi', 540)
        get_current_user =await send_req.get_user_profile(chat_id=message.chat.id, university_id=UNIVERSITY_ID)
        chat_id_user = get_current_user['chat_id_user']
        id_user = get_current_user['id']
        await state.update_data(chat_id_user=chat_id_user, id_user=id_user)
        data = await state.get_data()
        phone = data['phone']
        ic('django')
        ic(id_user, phone, chat_id_user,first_name, last_name)
        try:
            update_user_profile_response = await send_req.update_user_profile(university_id=UNIVERSITY_ID, 
                                                                        chat_id=chat_id_user, 
                                                                        phone=phone, 
                                                                        first_name=first_name, 
                                                                        username=message.from_user.username,
                                                                        last_name=last_name, 
                                                                        pin=pin,date=date_now)
            ic(update_user_profile_response)
        except Exception as e:
            ic(490,'my_dj_error', e)
        ic('education ga keldik', 598)

    data = await state.get_data()
    token = data.get('token')
    register_user = data.get('register_user')
    transfer_user = data.get('transfer_user')
    ic('register_user', register_user, 'transfer_user', transfer_user)

    if register_user:
        educations_response = send_req.educations(token)
        educations = educations_response.json()
        
        buttons = [[InlineKeyboardButton(text=item['name_uz'], callback_data=f"edu_{item['id']}")]
                    for item in educations]
        educationMenu = InlineKeyboardMarkup(inline_keyboard=buttons)
        await message.answer("<b>Universitetga hujjat topshrish uchun ta'lim ma'lumotlaringizni kiritishingiz zarur.</b>", parse_mode='HTML',
                            reply_markup=ReplyKeyboardRemove())
        await message.answer("<b>Bitirgan yoki tahsil olayotgan ta'lim dargohi turini tanlang:</b>", reply_markup=educationMenu, parse_mode='HTML')
            
        await EducationData.education_id.set()
    await EducationData.education_id.set()
    


@dp.message_handler(state=EducationData.education_id)
async def education_id_handler(message: types.Message, state: FSMContext, page: int = 0):
    ic('education ga keldi')
    data = await state.get_data()
    token = data.get('token')
    register_user = data.get('register_user')
    transfer_user = data.get('transfer_user')
    ic('register_user', register_user, 'transfer_user', transfer_user)

    if register_user:
        educations_response = send_req.educations(token)
        educations = educations_response.json()
        
        buttons = [[InlineKeyboardButton(text=item['name_uz'], callback_data=f"edu_{item['id']}")]
                   for item in educations]
        educationMenu = InlineKeyboardMarkup(inline_keyboard=buttons)
        await message.answer("<b>Universitetga hujjat topshrish uchun ta'lim ma'lumotlaringizni kiritishingiz zarur.</b>", parse_mode='HTML')
        await message.answer("<b>Bitirgan yoki tahsil olayotgan ta'lim dargohi turini tanlang:</b>", reply_markup=educationMenu, parse_mode='HTML')
    elif transfer_user:
        # Ask user to input the search query for countries
        await EducationData.country_search.set()  # Assuming country_search is a state for inputting country search
        await message.answer(search_university, reply_markup=ReplyKeyboardRemove())

# Handle the country search input
@dp.message_handler(state=EducationData.country_search)
async def process_country_search(message: types.Message, state: FSMContext):
    user_query = message.text.lower()
    # ic(user_query, 8800)
    variants = {'zbekiston', 'zbekistan', 'uzbekistan', 'uzbekiston', 'o\'zbekistan', 'o\'zbekiston'}

    if any(variant.lower() in user_query.lower() for variant in variants):
        user_query = 'o`zbekiston'
    # ic(user_query, 'result')
    token = (await state.get_data()).get('token')
    all_countries = await send_req.countries(token)  # Ensure this is an async call to your backend/API
    # ic('all_countries', all_countries)
    matching_countries = [country for country in all_countries if user_query in country['name_uz'].lower()]
    ic(matching_countries)
    if not matching_countries:
        await message.answer(not_found_country)
        return

    buttons = [
        [InlineKeyboardButton(text=country['name_uz'], callback_data=f"country_{country['id']}")]
        for country in matching_countries
    ]
    country_menu = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(select_one, reply_markup=country_menu)
    await EducationData.country_search.set()
    # await state.finish()

@dp.callback_query_handler(lambda c: c.data.startswith('country_'), state=EducationData.country_search)
async def handle_country_selection(callback_query: types.CallbackQuery,state: FSMContext):
    await callback_query.answer()  
    ic('callback_query', callback_query.data)
    selected_country_id = callback_query.data.split('_')[1]
    # selected_country_name = callback_query.data.split('_')[2]
    ic('selected_country_id',selected_country_id)
    await state.update_data(country_id=selected_country_id)
    # await callback_query.message.answer(selected_country_name)
    await callback_query.message.answer(saved_message)
    await callback_query.message.answer("Ta'lim dargohi nomini kiriting: ", reply_markup=ReplyKeyboardRemove())
    await EducationData.transfer_education_name.set()
    
@dp.message_handler(state=EducationData.transfer_education_name)
async def transfer_education_name_handler(message: types.Message, state: FSMContext):
    transfer_edu_name = message.text.strip()
    ic(transfer_edu_name)
    await state.update_data(transfer_education_name=transfer_edu_name)
    await message.answer("Ta'lim yo'nalishi nomini kiriting: ", reply_markup=ReplyKeyboardRemove())
    await EducationData.transfer_direction_name.set()


@dp.message_handler(state=EducationData.transfer_direction_name)
async def transfer_direction_name_handler(message: types.Message, state: FSMContext):
    ic(message)
    transfer_direction_name = message.text.strip()
    ic(transfer_direction_name)
    # await message.answer("Ayni vaqtdagi kursingizni tanlang: ")
    inline_buttons = [
        [
            InlineKeyboardButton(text='1-kursda o\'qiyman', callback_data=1)
        ],
        [
            InlineKeyboardButton(text='2-kursda o\'qiyman', callback_data=2)
        ]
    ]
    inline_kb = InlineKeyboardMarkup(inline_keyboard=inline_buttons)
    await message.answer("Ayni vaqtdagi kursingizni tanlang: ", reply_markup=inline_kb)
    await state.update_data(transfer_direction_name=transfer_direction_name)

@dp.callback_query_handler(lambda c: c.data.isdigit(), state=EducationData.transfer_direction_name)
async def handle_callback_query_dir(callback_query: types.CallbackQuery, state: FSMContext):
    selected_course = callback_query.data
    ic(selected_course)
    await callback_query.answer()
    await state.update_data(selected_course=selected_course)
    await callback_query.message.answer(example_transkript_message, reply_markup=ReplyKeyboardRemove())
    await EducationData.file_diploma_transkript.set()
    # await callback_query.message.answer()


@dp.message_handler(content_types=[types.ContentType.PHOTO, types.ContentType.DOCUMENT], state=EducationData.file_diploma_transkript)
async def upload_file1(message: types.Message, state: FSMContext):
    from aiogram import Bot, Dispatcher
    from data.config import BOT_TOKEN
    import aiofiles
    import os
    
    bot = Bot(token=BOT_TOKEN)
    ic(820, message)
    if message.photo:
        try:
            largest_photo = message.photo[-1]  # Get the largest resolution of the photo
            ic(largest_photo)
            file_id = largest_photo.file_id
            file_info = await bot.get_file(file_id)
            file_path = file_info.file_path
            ic(file_path)
            file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
            # await message.answer(file_url)
            
            local_file_path = os.path.join(download_dir, file_path) 
            await bot.download_file(file_path, local_file_path)
            try:
                res_file = upload.upload_new_file(token=token_, filename=local_file_path)
                data1 = res_file.json()
                ic(data1)
                await state.update_data(image=data1['path'])
            except Exception as e:
                ic(e)
                await message.reply(f"Xatolik yuz berdi: {str(e)}")
        except Exception as e:
            await message.reply("Rasmni qayta yuboring.")
    if message.document:
        document = message.document
        file_id = document.file_id
        file_name = document.file_name
        ic(900, file_name, file_id)
    elif message.photo:
        photo = message.photo[-1]
        file_id = photo.file_id
        file_name = f"{file_id}.jpg"
        ic(file_name, photo)
    
    ic(file_name)
    
    data = await state.get_data()
    ic(data)
    token_id = data['token']
    ic(token_id)
    
    token_ = data.get('token')
    
    file_path = await bot.get_file(file_id)
    file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path.file_path}"
    ic(file_url)

    download_dir = 'transcript_files'
    os.makedirs(download_dir, exist_ok=True)

    local_file_path = os.path.join(download_dir, file_name)
    await send_req.download_file(file_url, local_file_path)
    await message.answer("Please wait while the file is being uploaded...", parse_mode='HTML')
    
    res_file = upload.upload_new_file_transcript(token=token_, filename=local_file_path)
    
    try:
        file_size = os.path.getsize(local_file_path)
        file_size_kb = file_size / 1024
        file_size_mb = file_size_kb / 1024
        ic(f'size: {file_size_mb:.2f}')
    except Exception as e:
        ic(e)
        await message.answer("File not found")
        return

    await state.update_data(file_size=file_size)
    await message.answer("File has been uploaded successfully.")

    try:
        data1 = res_file.json()
        path = data1['path']
        ic(path)
        data = await state.get_data()
        file_diploma_transkript = path
        country_id = data.get('country_id')
        selected_course = data.get('selected_course')
        transfer_direction_name = data.get('transfer_direction_name')
        transfer_education_name = data.get('transfer_education_name')

        res_data = await send_req.application_forms_transfer(
            token_,
            int(country_id),
            transfer_direction_name,
            transfer_education_name,
            file_diploma_transkript,
            int(selected_course)
        )
        ic(res_data)
        await message.answer("Data has been saved successfully.", reply_markup=enter_button)
        await state.update_data(file_diploma_transkript=path)
        
    except Exception as e:
        ic(e)
        await message.answer(f"An error occurred: {e}")
        return
    
    src_ = 'src' 
    src_res = await collect_data.collect_me_data(token=token_, field_name=src_)
    if src_res is not None and src_res is not False:
        await state.update_data(src=src_res)
    await EducationData.degree_id.set()
    
@dp.message_handler(content_types=types.ContentType.PHOTO, state=EducationData.file_diploma_transkript)
async def upload_file2(message: types.Message, state: FSMContext):
    from aiogram import Bot
    from data.config import BOT_TOKEN
    import aiofiles
    import os
    
    bot = Bot(token=BOT_TOKEN)
    ic(903, message)
    if message.photo:
        try:
            largest_photo = message.photo[-1]  # Get the largest resolution of the photo
            ic(largest_photo)
            file_id = largest_photo.file_id
            file_info = await bot.get_file(file_id)
            file_path = file_info.file_path
            ic(file_path)
            file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
            # await message.answer(file_url)
            
            local_file_path = os.path.join(download_dir, file_path) 
            await bot.download_file(file_path, local_file_path)
            try:
                res_file = upload.upload_new_file(token=token_, filename=local_file_path)
                data1 = res_file.json()
                ic(data1)
                await state.update_data(image=data1['path'])
            except Exception as e:
                ic(e)
                await message.reply(f"Xatolik yuz berdi: {str(e)}")
        except Exception as e:
            await message.reply("Rasmni qayta yuboring.")
    if message.document:
        document = message.document
        file_id = document.file_id
        file_name = document.file_name
        ic(900, file_name, file_id)
    elif message.photo:
        photo = message.photo[-1]
        file_id = photo.file_id
        file_name = f"{file_id}.jpg"
        ic(927, file_name, photo)
    
    ic(file_name)
    
    data = await state.get_data()
    ic(data)
    token_id = data['token']
    ic(token_id)
    
    token_ = data.get('token')
    
    file_path = await bot.get_file(file_id)
    file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path.file_path}"
    ic(file_url)

    download_dir = 'transcript_files'
    os.makedirs(download_dir, exist_ok=True)

    local_file_path = os.path.join(download_dir, file_name)
    await send_req.download_file(file_url, local_file_path)
    await message.answer("Please wait while the file is being uploaded...", parse_mode='HTML')
    
    res_file = upload.upload_new_file_transcript(token=token_, filename=local_file_path)
    
    try:
        file_size = os.path.getsize(local_file_path)
        file_size_kb = file_size / 1024
        file_size_mb = file_size_kb / 1024
        ic(f'size: {file_size_mb:.2f}')
    except Exception as e:
        ic(e)
        await message.answer("File not found")
        return

    await state.update_data(file_size=file_size)
    await message.answer("File has been uploaded successfully.")

    try:
        data1 = res_file.json()
        path = data1['path']
        ic(path)
        data = await state.get_data()
        file_diploma_transkript = path
        country_id = data.get('country_id')
        selected_course = data.get('selected_course')
        transfer_direction_name = data.get('transfer_direction_name')
        transfer_education_name = data.get('transfer_education_name')

        res_data = await send_req.application_forms_transfer(
            token_,
            int(country_id),
            transfer_direction_name,
            transfer_education_name,
            file_diploma_transkript,
            int(selected_course)
        )
        ic(res_data)
        await message.answer("Data has been saved successfully.", reply_markup=enter_button)
        await state.update_data(file_diploma_transkript=path)
        
    except Exception as e:
        ic(e)
        await message.answer(f"An error occurred: {e}")
        return
    
    src_ = 'src' 
    src_res = await collect_data.collect_me_data(token=token_, field_name=src_)
    if src_res is not None and src_res is not False:
        await state.update_data(src=src_res)
    await EducationData.degree_id.set()

@dp.message_handler(content_types=['document', 'photo'], state=EducationData.file_diploma_transkript)
async def upload_file3(message: types.Message, state: FSMContext):
    ic(986, message)
    ic(message.document.file_name)
    from aiogram import Bot, Dispatcher
    from data.config import BOT_TOKEN

    data = await state.get_data()
    ic(data)
    token_id = data['token']
    ic(token_id)
    if message.photo:
        try:
            largest_photo = message.photo[-1]  # Get the largest resolution of the photo
            ic(largest_photo)
            file_id = largest_photo.file_id
            file_info = await bot.get_file(file_id)
            file_path = file_info.file_path
            ic(file_path)
            file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
            # await message.answer(file_url)
            
            local_file_path = os.path.join(download_dir, file_path) 
            await bot.download_file(file_path, local_file_path)
            try:
                res_file = upload.upload_new_file(token=token_, filename=local_file_path)
                data1 = res_file.json()
                ic(data1)
                await state.update_data(image=data1['path'])
            except Exception as e:
                ic(e)
                await message.reply(f"Xatolik yuz berdi: {str(e)}")
        except Exception as e:
            await message.reply("Rasmni qayta yuboring.")
    token_ = data.get('token') if data.get('token') else None

    document = message.document
    file_path = await bot.get_file(document.file_id)
    file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path.file_path}"
    ic(file_url)
    # await message.answer(file_url)
    download_dir = 'transcript_files'
    await aiofiles.os.makedirs(download_dir, exist_ok=True)

    local_file_path = os.path.join(download_dir, document.file_name)
    # print(local_file_path)
    await send_req.download_file(file_url, local_file_path)
    await message.answer(wait_file_is_loading, parse_mode='HTML')
    # ic(local_file_path)

    res_file = upload.upload_new_file_transcript(token=token_, filename=local_file_path)
    # if file_size != 'File not found':
    try:
        file_size = os.path.getsize(local_file_path)
        file_size_kb = file_size / 1024
        file_size_mb = file_size_kb / 1024
        ic(f'size: {file_size_mb:.2f}')
    except: 
        return 'Fayl topilmadi'
    await state.update_data(file_size=file_size)
    await message.answer("Fayl yuklandi.")
    
    # ic(all_state)
    # print(res_file.status_code)
    # print(res_file)
    try:
        data1 = res_file.json()
        path = data1['path']
        ic(path)
        data = await state.get_data()
        file_diploma_transkript = path
        country_id = data.get('country_id')
        selected_course = data.get('selected_course')
        transfer_direction_name = data.get('transfer_direction_name')
        transfer_education_name = data.get('transfer_education_name')
        res_data = await send_req.application_forms_transfer(
            token_,
            int(country_id),
            transfer_direction_name,
            transfer_education_name,
            file_diploma_transkript,
            int(selected_course)
        )
        ic(res_data)
        await message.answer(saved_message, reply_markup=enter_button)
        await state.update_data(file_diploma_transkript=path)
        
    except Exception as e:
        ic(e)
        await message.answer(e)
        return e
    
    
    src_ = 'src' 
    src_res = await collect_data.collect_me_data(token=token_, field_name=src_)
    if src_res is not None or src_res is not False:
        await state.update_data(src=src_res)
    await EducationData.degree_id.set()





@dp.callback_query_handler(lambda c: c.data.startswith('edu_'), state=EducationData.education_id)
async def education_selection_handler(callback_query: types.CallbackQuery, state: FSMContext):
    from aiogram import Bot, Dispatcher, types
    from data.config import BOT_TOKEN
    education_id = callback_query.data.split('edu_')[1]
    await state.update_data(education_id=education_id)
    await callback_query.answer()
    await EducationData.region_id.set() 
    await bot.send_message(callback_query.from_user.id, saved_message, parse_mode="HTML", reply_markup=ReplyKeyboardRemove())
    data = await state.get_data()
    token = data['token']  # Corrected data access
    region_response = send_req.regions(token)  # Ensure it's awaited
    regions = region_response.json()  # Async call should be awaited
    
    buttons = [[InlineKeyboardButton(text=item['name_uz'], callback_data=f"reg_{item['id']}")] for item in regions]
    regionMenu = InlineKeyboardMarkup(inline_keyboard=buttons)

    await bot.send_message(callback_query.from_user.id,select_region, reply_markup=regionMenu)

@dp.callback_query_handler(lambda c: c.data.startswith('reg_'), state=EducationData.region_id)
async def region_selection_handler(callback_query: types.CallbackQuery, state: FSMContext):
    region_id = callback_query.data.split('reg_')[1]
    ic(callback_query.data)
    await state.update_data(region_id=region_id)
    await callback_query.answer()
    await EducationData.district_id.set()
    
    await callback_query.message.answer(saved_message, parse_mode="HTML", reply_markup=ReplyKeyboardRemove())

    data = await state.get_data()
    token = data['token']
    region_id = data['region_id']
    district_id_response = send_req.districts(token, int(region_id))
    districts = district_id_response.json()
    # pprint(districts)
    buttons = [[InlineKeyboardButton(text=item['name_uz'], callback_data=f"dist_{item['id']}")] for item in districts]
    districtsMenu = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback_query.message.answer("Tumanni tanlang:", reply_markup=districtsMenu)




@dp.callback_query_handler(lambda c: c.data.startswith('dist_'), state=EducationData.district_id)
async def district_selection_handler(callback_query: types.CallbackQuery, state: FSMContext):
    district_id = callback_query.data.split('dist_')[1]
    ic(callback_query.data)
    await state.update_data(district_id=district_id)
    await callback_query.answer()
    await EducationData.institution_name.set()  # Prepare for the next step
    from aiogram import Bot, Dispatcher, types
    from data.config import BOT_TOKEN
    await bot.send_message(callback_query.from_user.id, type_your_edu_name)

@dp.message_handler(state=EducationData.institution_name)
async def type_institution_name_handler(message: types.Message, state: FSMContext):
    from aiogram import Bot, Dispatcher
    from data.config import BOT_TOKEN
    institution_name = message.text.strip()

    if institution_name.lower() != 'davom etish':
        await state.update_data(institution_name=institution_name)
        await message.answer('Ma\'lumotlar muvaffaqiyatli qabul qilindi.', reply_markup=ReplyKeyboardRemove())
        # Proceed to conclude the process or transition to the next state here
        # Example to conclude:
        data = await state.get_data()
        institution_name = data.get('institution_name', 'Not specified')
        await bot.send_photo(chat_id=message.chat.id,
                             photo='https://user-images.githubusercontent.com/529864/106505688-67e04880-64a7-11eb-96e1-683d95d19929.png', 
                             caption=example_diploma_message, 
                             parse_mode="Markdown")
        await EducationData.file_diploma.set() 
    else:
        # If the user sends 'Davom etish', prompt them again for the institution name.
        await message.answer(error_type_edu_name, reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Davom etish')))

@dp.message_handler(content_types=['document', 'photo'], state=EducationData.file_diploma)
async def upload_file4(message: types.Message, state: FSMContext):
    from aiogram import Bot, Dispatcher
    from data.config import BOT_TOKEN
    if message.photo:
        try:
            data = await state.get_data()
            token_ = data['token'] if data['token'] else None
            largest_photo = message.photo[-1] 
            ic(largest_photo)
            file_id = largest_photo.file_id
            file_info = await bot.get_file(file_id)
            file_path = file_info.file_path
            ic(file_path)
            file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
            # await message.answer(file_url)
            download_dir = 'diploma_files'
            local_file_path = os.path.join(download_dir, file_path) 
            await bot.download_file(file_path, local_file_path)
            try:
                res_file = upload.upload_new_file(token=token_, filename=local_file_path)
                data1 = res_file.json()
                ic(1290, data1)
                await state.update_data(file_diploma=data1['path'])
            except Exception as e:
                ic(e)
                await message.reply(f"Xatolik yuz berdi: {str(e)}")
            await message.reply("Rasm qabul qilindi")
            src_ = 'src' 
            src_res = await collect_data.collect_me_data(token=token_, field_name=src_)
            if src_res is not None or src_res is not False:
                await state.update_data(src=src_res)
        except Exception as e:
            await message.reply("Rasmni qaytadan yuboring")
    if not message.photo:
        data = await state.get_data()
        token_ = data['token'] if data['token'] else None

        document = message.document
        file_path = await bot.get_file(document.file_id)
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path.file_path}"
        # ic(file_url)
        # await message.answer(file_url)
        download_dir = 'diploma_files'
        await aiofiles.os.makedirs(download_dir, exist_ok=True)

        local_file_path = os.path.join(download_dir, document.file_name)
        # print(local_file_path)
        await send_req.download_file(file_url, local_file_path)
        await message.answer(wait_file_is_loading, parse_mode='HTML')
        # ic(local_file_path)

        res_file = upload.upload_new_file(token=token_, filename=local_file_path)
        # if file_size != 'File not found':
        try:
            file_size = os.path.getsize(local_file_path)
            file_size_kb = file_size / 1024
            file_size_mb = file_size_kb / 1024
            # print(f'size: {file_size_mb:.2f}')
        except: 
            return 'Fayl topilmadi'
        await state.update_data(file_size=file_size)
        await message.answer("Fayl yuklandi.")
    
    # ic(all_state)
    # print(res_file.status_code)
    # print(res_file)
        try:
            data1 = res_file.json()
            ic(data1['path'])
            await state.update_data(file_diploma=data1['path'])
        except Exception as e:
            return e
    

        src_ = 'src' 
        src_res = await collect_data.collect_me_data(token=token_, field_name=src_)
        if src_res is not None or src_res is not False:
            await state.update_data(src=src_res)
    


    all_state = await state.get_data()
    ic(all_state)
    # print(data1['path'])
    district_id = int(all_state['district_id']) if all_state['district_id'] else 0
    education_id = int(all_state['education_id']) if all_state['education_id'] else 0
    file_ = all_state['file_diploma'] if all_state['file_diploma'] else None
    institution_name = all_state['institution_name'] if all_state['institution_name'] else None
    region_id = int(all_state['region_id']) if all_state['region_id'] else None
    src = all_state['src'] if all_state['src'] else 'manually'

    res_data_app_forms_for_edu = send_req.application_forms_for_edu(token_,
                                                    district_id,
                                                    education_id,
                                                    file_,
                                                    institution_name,
                                                    region_id,
                                                    src
                                                    )
    await state.update_data(me_data=res_data_app_forms_for_edu.json())
    await message.answer("<b>Sizda chet tili sertifikati mavjudmi?</b>", parse_mode='HTML', reply_markup=yes_no)
    ic(res_data_app_forms_for_edu.json())

    await EducationData.has_sertificate.set()

@dp.message_handler(state=EducationData.has_sertificate)
async def has_sertificate(message: types.Message, state: FSMContext):
    text = message.text
    if text == "Ha, mavjud":
        cert_types = [
            {'id': 1, 'type': 'IELTS'},
            {'id': 2, 'type': 'TOEFL'},
            {'id': 3, 'type': 'CEFR'},
            {'id': 4, 'type': 'SAT'},
            {'id': 5, 'type': 'GMAT'},
            {'id': 6, 'type': 'GRE'},
            {'id': 7, 'type': 'Boshqa'}
        ] 
        buttons = [[InlineKeyboardButton(text=item['type'], 
                                        callback_data=f"type_{item['id']}") for item in cert_types]]
        certTypeMenu = InlineKeyboardMarkup(inline_keyboard=buttons)

        await message.answer(select_type_certificate, reply_markup=certTypeMenu)
        await EducationData.certificate_type.set()


    elif text == "Yo'q, mavjud emas":
        await message.answer("Ariza topshirishni istasangiz davom etish tugmasini bosing", reply_markup=enter_button)

        await EducationData.degree_id.set()
    elif text == "Bekor qilish":
        await message.answer("Fayl yuklash bekor qilindi.", reply_markup=ReplyKeyboardRemove())
        await message.answer("Ariza topshirishni davom etishni istasangiz davom etish tugmasini bosing:", reply_markup=enter_button)
        await EducationData.degree_id.set()
        
# @dp.message_handler(Text(equals="Bekor qilish"), state="*")
# async def cancel_upload(message: types.Message, state: FSMContext):
#     # Remove the current keyboard
#     await message.answer("Fayl yuklash bekor qilindi.", reply_markup=ReplyKeyboardRemove())
    
#     # Send a new message with the new keyboard
#     await message.answer("Ariza topshirishni istasangiz davom etish tugmasini bosing:", reply_markup=enter_button)
    
#     # Set the state to get_certificate
#     await EducationData.get_certificate.set()

@dp.callback_query_handler(lambda c: c.data.startswith('type_'), state=EducationData.certificate_type)
async def region_selection_handler(callback_query: types.CallbackQuery, state: FSMContext):
    certificate_type = callback_query.data.split('type_')[1]
    cert_types = [
            {'id': 1, 'type': 'IELTS'},
            {'id': 2, 'type': 'TOEFL'},
            {'id': 3, 'type': 'CEFR'},
            {'id': 4, 'type': 'SAT'},
            {'id': 5, 'type': 'GMAT'},
            {'id': 6, 'type': 'GRE'},
            {'id': 7, 'type': 'Boshqa'}
        ]
    cert_types = [item['type'] for item in cert_types if item['id'] == int(certificate_type)]
    ic(cert_types)
    if certificate_type and len(cert_types) > 0:
        certificate_type = str(cert_types[0]).lower()
        ic(certificate_type)
    await state.update_data(certificate_type=certificate_type)
    await callback_query.answer()
    await EducationData.get_certificate.set()  # Proceed to the next state
    # await message.answer(c)
    await callback_query.message.answer(saved_message, parse_mode="HTML")
    await bot.send_photo(chat_id=callback_query.message.chat.id,
                            photo='https://user-images.githubusercontent.com/529864/106505688-67e04880-64a7-11eb-96e1-683d95d19929.png', 
                            caption=example_certification_message, 
                            parse_mode="Markdown",
                            reply_markup=ReplyKeyboardRemove())
    


    
@dp.message_handler(content_types=['document', 'photo'], state=EducationData.get_certificate)
async def get_sertificate(message: types.Message, state: FSMContext):
    if message.photo:
        try:
            data = await state.get_data()
            token_ = data['token'] if data['token'] else None
            largest_photo = message.photo[-1] 
            ic(largest_photo)
            file_id = largest_photo.file_id
            file_info = await bot.get_file(file_id)
            file_path = file_info.file_path
            ic(file_path)
            file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
            # await message.answer(file_url)
            # download_dir = 'diploma_files'
            # local_file_path = os.path.join(download_dir, file_path) 
            # await bot.download_file(file_path, local_file_path)
            download_dir = 'diploma_files'
            os.makedirs(download_dir, exist_ok=True)
            
            file_name = os.path.basename(file_path)
            local_file_path = os.path.join(download_dir, file_name)

            # Rasmni yuklab olish
            async with aiohttp.ClientSession() as session:
                async with session.get(file_url) as resp:
                    if resp.status == 200:
                        f = await aiofiles.open(local_file_path, mode='wb')
                        await f.write(await resp.read())
                        await f.close()

            ext = os.path.splitext(local_file_path)[-1].lower()
            if ext == '.heic':
                local_file_path = convert_heic_to_jpg(local_file_path)
            try:
                res_file = upload.upload_new_file(token=token_, filename=local_file_path)
                data1 = res_file.json()
                ic(1290, data1)
                await state.update_data(file_size_sertificate=data1['path'])
            except Exception as e:
                ic(e)
                await message.reply(f"Xatolik yuz berdi: {str(e)}")
            await message.reply("Rasm qabul qilindi")
            src_ = 'src' 
            src_res = await collect_data.collect_me_data(token=token_, field_name=src_)
            if src_res is not None or src_res is not False:
                await state.update_data(src=src_res)
        except Exception as e:
            await message.reply("Rasmni qaytadan yuboring")
    if not message.photo:
        
        data = await state.get_data()
        token_ = data['token'] if data['token'] else None

        document = message.document
        file_path = await bot.get_file(document.file_id)
        ic(file_path)
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path.file_path}"
        # download_dir = 'sertificate_files'
        # # await message.answer(file_url)
        # await aiofiles.os.makedirs(download_dir, exist_ok=True)

        # local_file_path = os.path.join(download_dir, document.file_name)
        # ic(local_file_path)
        # await send_req.download_file(file_url, local_file_path)

        download_dir = 'sertificate_files'
        os.makedirs(download_dir, exist_ok=True)
        file_name = os.path.basename(document.file_name)
        local_file_path = os.path.join(download_dir, file_name)

        async with aiohttp.ClientSession() as session:
            async with session.get(file_url) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(local_file_path, mode='wb')
                    await f.write(await resp.read())
                    await f.close()

        ext = os.path.splitext(local_file_path)[-1].lower()
        if ext == '.heic':
            local_file_path = convert_heic_to_jpg(local_file_path)
        await message.answer(wait_file_is_loading, parse_mode='HTML', reply_markup=ReplyKeyboardRemove())
        # ic(local_file_path)

        res_file = upload.upload_new_file_sertificate(token=token_, filename=local_file_path)
        ic(731, res_file)
        try:
            file_size = os.path.getsize(local_file_path)
            file_size_kb = file_size / 1024
            file_size_mb = file_size_kb / 1024
            ic(f'size: {file_size_mb:.2f}')
        except:
            return 'File not found'
        await state.update_data(file_size_sertificate=file_size)
        # await message.answer("Fayl yuklandi.", reply_markup=ReplyKeyboardRemove())
        # await EducationData.has_application.set()
        # ic(all_state)
        ic(res_file.status_code)
        ic(res_file)
        data_user = await state.get_data()
        certificate_type = data_user['certificate_type']
        ic(certificate_type)
        data1 = res_file.json()
        ic(747, data1)
        await state.update_data(file_sertificate=data1['path'])
        ic(token_)
        ic(data1['path'])
        try:
            res = send_req.upload_sertificate(token=token_, filename=data1['path'], f_type=certificate_type)
            ic(751, res)
        except Exception as e:
            await message.answer(f"Xatolik: {e}")
            return

        await message.answer("Fayl yuklandi.")
    ic('boshlandi1')
    await EducationData.degree_id.set()
    ic('yakunlandi')
    await message.answer("<b>Universitetga ariza topshirish</b>", parse_mode="HTML")
    ic('started')
    my_degree = {1: 'Bakalavr',2: 'Magistratura',3: 'Doktorantura'}
    data = await state.get_data()
    token = data['token']
    directions_response = await send_req.directions(token)
    directions = directions_response
    if not isinstance(directions, list):
        ic('directions returned non-list', directions)
        await message.answer("Server bilan bog'lanishda xatolik. Iltimos, qayta urinib ko'ring.")
        return
    unique_degrees = []
    ic('ok')
    for obj in directions:
        degree_id = obj['degree_id']
        if not any(d['id'] == degree_id for d in unique_degrees):
            unique_degrees.append({
                'id': degree_id,
                'type_degree': my_degree[degree_id]})
    ic(unique_degrees)
    buttons = [[InlineKeyboardButton(text=item['type_degree'],
                                     callback_data=f"degree_{item['id']}") for item in unique_degrees]]
    degreeMenu = InlineKeyboardMarkup(inline_keyboard=buttons)
    ic('keldi')
    await message.answer(select_degree, parse_mode='HTML', reply_markup=degreeMenu)


@dp.message_handler(state=EducationData.degree_id)
async def has_application_start(message: types.Message, state: FSMContext):
    await message.answer("<b>Universitetga ariza topshirish</b>", parse_mode="HTML")
    ic('started')
    my_degree = {1: 'Bakalavr',2: 'Magistratura',3: 'Doktorantura'}
    data = await state.get_data()
    token = data['token']
    directions_response = await send_req.directions(token)
    ic(directions_response)
    directions = directions_response
    if not isinstance(directions, list):
        ic('directions returned non-list', directions)
        await message.answer("Server bilan bog'lanishda xatolik. Iltimos, qayta urinib ko'ring.")
        return
    unique_degrees = []
    ic('ok')
    for obj in directions:
        degree_id = obj['degree_id']
        if not any(d['id'] == degree_id for d in unique_degrees):
            unique_degrees.append({
                'id': degree_id,
                'type_degree': my_degree[degree_id]})
    ic(unique_degrees)
    buttons = [[InlineKeyboardButton(text=item['type_degree'],
                                     callback_data=f"degree_{item['id']}degree_{item['type_degree']}") for item in unique_degrees]]
    degreeMenu = InlineKeyboardMarkup(inline_keyboard=buttons)
    ic('keldi')
    await message.answer(select_degree, parse_mode='HTML', reply_markup=degreeMenu)
    



@dp.callback_query_handler(lambda c: c.data.startswith('degree_'), state=EducationData.degree_id)
async def has_application(callback_query: types.CallbackQuery, state: FSMContext):
    degree_id = None
    ic(9002, callback_query.data, callback_query.data.split('degree_'))
    if not len(callback_query.data.split('degree_')) < 3:
        _, degree_id , degree_name = callback_query.data.split('degree_')
    elif len(callback_query.data.split('degree_')) == 2:
        _ , degree_id = callback_query.data.split('degree_')
        degree_name = None
        
        ic(1641, degree_id)
        if degree_id == '1':
            degree_name = 'Bakalavr'
        elif degree_id == '2':
            degree_name = 'Magistratura'
    ic(1635, callback_query.data)
    ic(degree_id)
    ic(1644, degree_name)
    await state.update_data(degree_id=int(degree_id), degree_name=degree_name)
    select_mess = f"Tanlangan {degree_name}"
    ic(select_mess)
    await bot.send_message(callback_query.from_user.id, saved_message+"\n"+select_mess, reply_markup=ReplyKeyboardRemove(),
                           parse_mode="HTML")
    data = await state.get_data()
    token = data['token']
    direction_response = await send_req.directions(token)
    if isinstance(direction_response, dict):
        direction_response = direction_response.get('entities', []) if 'entities' in direction_response else []
    if not isinstance(direction_response, list):
        ic('directions returned non-list', direction_response)
        await callback_query.answer()
        await bot.send_message(callback_query.from_user.id,
                               "Server bilan bog'lanishda xatolik. Iltimos, qayta urinib ko'ring.")
        return
    await state.update_data(directions=direction_response)
    ic('directions count', len(direction_response))
    if direction_response:
        ic('first direction keys', list(direction_response[0].keys()))
    selected_degree_id = data['degree_id']
    ic(degree_id)

    def _direction_id(item):
        return item.get('id') or item.get('direction_id')

    def _direction_name(item):
        return (item.get('direction_name_uz')
                or item.get('name_uz')
                or item.get('name_ru')
                or item.get('name_en')
                or f"Yo'nalish #{_direction_id(item)}")

    try:
        selected_degree_id_int = int(selected_degree_id)
    except (TypeError, ValueError):
        selected_degree_id_int = None

    buttons = []
    for item in direction_response:
        if not isinstance(item, dict):
            continue
        try:
            item_degree_id = int(item.get('degree_id')) if item.get('degree_id') is not None else None
        except (TypeError, ValueError):
            item_degree_id = None
        if item_degree_id != selected_degree_id_int:
            continue
        adm = (item.get('admission_status') or '').lower()
        lms = (item.get('lms_status') or '').lower()
        if adm and adm != 'active':
            continue
        if lms and lms != 'active':
            continue
        did = _direction_id(item)
        if did is None:
            continue
        buttons.append([InlineKeyboardButton(
            text=_direction_name(item),
            callback_data=f"direction_{did}",
        )])
    ic('buttons built', len(buttons))
    if not buttons:
        await callback_query.answer()
        await bot.send_message(callback_query.from_user.id, "Yo'nalish topilmadi.")
        return
    directionMenu = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback_query.answer()
    await bot.send_message(callback_query.from_user.id, select_direction, reply_markup=directionMenu)
    await EducationData.direction_id.set()

@dp.callback_query_handler(lambda c: c.data.startswith('direction_'), state=EducationData.direction_id)
async def region_selection_handler(callback_query: types.CallbackQuery, state: FSMContext):
    data_state = await state.get_data()
    directions = data_state.get('directions') or []
    if not isinstance(directions, list):
        directions = directions.get('entities', []) if isinstance(directions, dict) else []
    ic(callback_query.data, 'shu keldi')
    try:
        direction_id = int(callback_query.data.split('direction_', 1)[1])
    except (IndexError, ValueError):
        await callback_query.answer("Noto'g'ri tanlov", show_alert=True)
        return

    def _did(item):
        return item.get('id') or item.get('direction_id')

    def _dname(item):
        return (item.get('direction_name_uz')
                or item.get('name_uz')
                or item.get('name_ru')
                or item.get('name_en')
                or f"Yo'nalish #{_did(item)}")

    matched = next((item for item in directions
                    if isinstance(item, dict) and _did(item) == direction_id), None)
    if matched is None:
        ic('direction not found in state', direction_id)
        await callback_query.answer("Yo'nalish topilmadi", show_alert=True)
        return
    direction_name = _dname(matched)
    ic(callback_query.data, 'yana shu keldi')
    await state.update_data(direction_id=direction_id)
    await callback_query.answer()
    await EducationData.education_type.set()  # Proceed to the next state
    selected_mess = f"Tanlangan {direction_name}"
    await callback_query.message.answer(saved_message+'\n'+selected_mess, parse_mode="HTML")
    data = await state.get_data()
    token = data['token']
    ic(data['direction_id'], type(data['direction_id']))
    selected_degree_id = int(data['degree_id'])
    selected_direction_id = int(data['direction_id'])
    ic(selected_degree_id)
    ic(selected_direction_id)
    await state.update_data(direction_id=selected_direction_id)
    edu_types_resp = await send_req.education_types(
        token,
        direction_id=selected_direction_id,
        degree_id=selected_degree_id,
    )
    if isinstance(edu_types_resp, dict) and edu_types_resp.get('error'):
        ic('education_types error', edu_types_resp.get('status_code'), edu_types_resp.get('detail'))
        await callback_query.message.answer(
            "Ma'lumotlarni olishda xatolik yuz berdi. Iltimos, keyinroq qayta urinib ko'ring."
        )
        return
    edu_types = edu_types_resp if isinstance(edu_types_resp, list) else []
    ic('edu_types count', len(edu_types), 'selected_dir', selected_direction_id, 'selected_deg', selected_degree_id)

    uniq_edu_types = []
    seen_ids = set()
    for it in edu_types:
        if not isinstance(it, dict):
            continue
        et_id = it.get('id') or it.get('education_type_id')
        if et_id is None or et_id in seen_ids:
            continue
        et_name = (it.get('name_uz')
                   or it.get('education_type_name_uz')
                   or it.get('name_ru')
                   or it.get('name_en')
                   or it.get('name'))
        if not et_name:
            continue
        seen_ids.add(et_id)
        uniq_edu_types.append({'id': et_id, 'name': et_name})
    ic('uniq_edu_types count', len(uniq_edu_types))

    if not uniq_edu_types:
        if edu_types and isinstance(edu_types[0], dict):
            ic('edu_types[0] keys', list(edu_types[0].keys()))
        await callback_query.message.answer("Bu yo'nalish bo'yicha ta'lim shakli topilmadi.")
        return

    buttons = [[InlineKeyboardButton(text=item['name'], callback_data=f"e_t_{item['id']}e_t_{item['name']}")] for item in uniq_edu_types]
    eduTypesMenu = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback_query.message.answer(select_edu_type, reply_markup=eduTypesMenu)

        
 


@dp.callback_query_handler(lambda c: c.data.startswith('e_t_'), state=EducationData.education_type)
async def region_selection_handler(callback_query: types.CallbackQuery, state: FSMContext):
    edu_type_id_ = callback_query.data.split('e_t_')[1]
    edu_type_name = callback_query.data.split('e_t_')[2]
    ic(callback_query.data)
    await state.update_data(education_type=edu_type_id_)
    selected_mess = f"Tanlangan {edu_type_name}"
    data = await state.get_data()
    token = data['token']
    education_type_id_selected = int(data['education_type'])
    direction_id_selected = int(data['direction_id'])
    degree_id_selected = int(data['degree_id'])
    ic(edu_type_id_, type(edu_type_id_))
    ic(degree_id_selected, type(degree_id_selected))
    await state.update_data(education_type=education_type_id_selected)

    if int(direction_id_selected) == 3 and int(edu_type_id_) == 2:
        ic('keldi 1571')
        await callback_query.answer()
        await callback_query.message.answer(saved_message+'\n'+selected_mess, parse_mode="HTML")
        
        await callback_query.message.answer("<a href='https://mehnat.uz/oz'>Mehnatuz</a> saytidan olingan ish tajribasi haqidagi ma’lumotnomani yuklang FAYL KO'RINISHIDA!:", reply_markup=ReplyKeyboardRemove(), parse_mode="HTML")
        await EducationData.work_experience.set()
    else:
        ic('keldi 1579')
        await callback_query.answer()
        await callback_query.message.answer(saved_message+'\n'+selected_mess, parse_mode="HTML")
        # await process_education_languages(callback_query, token, direction_id_selected, degree_id_selected, education_type_id_selected)
        await EducationData.education_lang_id.set()
        await process_education_languages(callback_query, token, direction_id_selected, degree_id_selected, education_type_id_selected)

async def process_education_languages(callback_query, token, direction_id_selected, degree_id_selected, education_type_id_selected):
    edu_languages = await _fetch_education_sources(token)
    edu_langs = _build_edu_langs(edu_languages, direction_id_selected, degree_id_selected, education_type_id_selected)
    ic('edu_langs count', len(edu_langs))
    if not edu_langs:
        await callback_query.message.answer("Bu yo'nalish bo'yicha ta'lim tili topilmadi.")
        return
    buttons = [[InlineKeyboardButton(text=item['name'], callback_data=f"_{item['id']}_{item['tuition_fee']}")] for item in edu_langs]
    languageMenu = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback_query.message.answer(select_edu_language, reply_markup=languageMenu)


async def _fetch_education_sources(token):
    sources = []
    edu = await send_req.educations_async(token)
    if isinstance(edu, dict):
        edu = edu.get('entities', []) if 'entities' in edu else []
    if isinstance(edu, list):
        sources.extend(x for x in edu if isinstance(x, dict))
    direc = await send_req.directions(token)
    if isinstance(direc, dict):
        direc = direc.get('entities', []) if 'entities' in direc else []
    if isinstance(direc, list):
        sources.extend(x for x in direc if isinstance(x, dict))
    return sources


def _build_uniq_edu_types(sources, selected_direction_id, selected_degree_id):
    def name_for(et_id, source):
        for k in source.get('education_types') or []:
            if isinstance(k, dict) and k.get('education_type_id') == et_id:
                return (k.get('education_type_name_uz')
                        or k.get('name_uz') or k.get('name'))
        return None

    uniq = []
    for obj in sources:
        if _direction_id_of(obj) != selected_direction_id:
            continue
        try:
            degree_id = int(obj.get('degree_id')) if obj.get('degree_id') is not None else None
        except (TypeError, ValueError):
            degree_id = None
        if degree_id != selected_degree_id:
            continue
        for k in obj.get('tuition_fees') or []:
            if not isinstance(k, dict):
                continue
            et_id = k.get('education_type_id')
            if et_id is None:
                continue
            et_name = name_for(et_id, obj) or _lookup_edu_type_name(sources, et_id)
            if et_name:
                item_obj = {'id': et_id, 'name': et_name}
                if item_obj not in uniq:
                    uniq.append(item_obj)
    return uniq


def _lookup_edu_type_name(sources, et_id):
    for source in sources:
        for k in source.get('education_types') or []:
            if isinstance(k, dict) and k.get('education_type_id') == et_id:
                return (k.get('education_type_name_uz')
                        or k.get('name_uz') or k.get('name'))
    return None


def _direction_id_of(obj):
    val = obj.get('direction_id') if isinstance(obj, dict) else None
    if val is None and isinstance(obj, dict):
        val = obj.get('id')
    try:
        return int(val) if val is not None else None
    except (TypeError, ValueError):
        return None


def _build_edu_langs(edu_languages, direction_id_selected, degree_id_selected, education_type_id_selected):
    edu_langs = []

    def return_language_name(language_id):
        for obj in edu_languages:
            if not isinstance(obj, dict):
                continue
            for lang in obj.get('education_languages') or []:
                if not isinstance(lang, dict):
                    continue
                try:
                    eid = int(lang.get('education_language_id'))
                except (TypeError, ValueError):
                    continue
                if eid == language_id:
                    return (lang.get('education_language_name_uz')
                            or lang.get('name_uz') or lang.get('name'))
        return None

    for obj in edu_languages:
        if not isinstance(obj, dict):
            continue
        direction_id = _direction_id_of(obj)
        try:
            degree_id = int(obj.get('degree_id')) if obj.get('degree_id') is not None else None
        except (TypeError, ValueError):
            degree_id = None
        if direction_id != direction_id_selected or degree_id != degree_id_selected:
            continue
        for t in obj.get('tuition_fees') or []:
            if not isinstance(t, dict):
                continue
            try:
                education_language_id = int(t.get('education_language_id'))
                education_type_id = int(t.get('education_type_id'))
            except (TypeError, ValueError):
                continue
            if education_type_id != education_type_id_selected:
                continue
            get_lang_name = return_language_name(education_language_id)
            if get_lang_name:
                lang_obj = {
                    'name': get_lang_name,
                    'id': education_language_id,
                    'tuition_fee': t.get('tuition_fee'),
                }
                if lang_obj not in edu_langs:
                    edu_langs.append(lang_obj)
    ic('edu_langs count', len(edu_langs))
    return edu_langs

@dp.message_handler(content_types=['document'], state=EducationData.work_experience)
async def get_work_experience_certificate(message: types.Message, state: FSMContext):
    from aiogram import Bot, Dispatcher
    from data.config import BOT_TOKEN
    import aiofiles
    import os
    
    bot = Bot(token=BOT_TOKEN)
    ic('keldi ++++++++++++++++++++++++++\n++++++++++++++++++++++++++\n++++++++++++++++++++++++++')
    data = await state.get_data()
    token_ = data['token'] if 'token' in data else None

    document = message.document
    file_path = await bot.get_file(document.file_id)
    file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path.file_path}"
    download_dir = 'work_experience'
    
    await aiofiles.os.makedirs(download_dir, exist_ok=True)

    local_file_path = os.path.join(download_dir, document.file_name)
    await send_req.download_file(file_url, local_file_path)
    await message.answer(wait_file_is_loading, parse_mode='HTML', reply_markup=ReplyKeyboardRemove())

    res_file = upload.work_experince_file_upload(token=token_, filename=local_file_path)

    try:
        file_size = os.path.getsize(local_file_path)
        file_size_kb = file_size / 1024
        file_size_mb = file_size_kb / 1024
    except:
        return 'Fayl topilmadi'
    
    await state.update_data(file_size_certificate=file_size)

    data_user = await state.get_data()
    certificate_type = "work_experience"
    data1 = res_file.json()
    ic(data1['path'])
    await state.update_data(file_certificate=data1['path'])

    try:
        res = send_req.upload_sertificate(token=token_, filename=data1['path'], f_type=certificate_type)
    except Exception as e:
        await message.answer(f"Xatolik: {e}")
        return

    await message.answer("Fayl yuklandi.")
    await EducationData.education_lang_id.set()
    edu_languages = await _fetch_education_sources(token_)
    data = await state.get_data()
    token = data['token']
    education_type_id_selected = int(data['education_type'])
    direction_id_selected = int(data['direction_id'])
    degree_id_selected = int(data['degree_id'])
    edu_langs = _build_edu_langs(edu_languages, direction_id_selected, degree_id_selected, education_type_id_selected)
    if not edu_langs:
        await message.answer("Bu yo'nalish bo'yicha ta'lim tili topilmadi.")
        return
    buttons = [[InlineKeyboardButton(text=item['name'], callback_data=f"_{item['id']}_{item['tuition_fee']}")] for item in edu_langs]
    ic(buttons)
    languageMenu = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(select_edu_language, reply_markup=languageMenu)
    
@dp.callback_query_handler(lambda c: c.data.startswith('_'), state=EducationData.education_lang_id)
async def after_select_lang(callback_query: types.CallbackQuery, state: FSMContext):
    # Parse callback data
    parts = callback_query.data.split('_')
    ic(parts)
    ic(callback_query.data)
    if len(parts) < 2:
        await callback_query.message.answer("Xatolik.qaytadan tanlang")
        return

    _, education_lang_id, education_tuition_fee = parts
    ic(education_lang_id, education_tuition_fee)
    data_state = await state.get_data()
    directions = data_state.get('directions')
    def get_education_language_name(directions, direction_id, education_lang_id):
        if not isinstance(directions, list):
            return None
        for obj in directions:
            if not isinstance(obj, dict):
                continue
            if _direction_id_of(obj) != direction_id:
                continue
            for lang in obj.get('education_languages') or []:
                if not isinstance(lang, dict):
                    continue
                try:
                    if int(lang.get('education_language_id')) != int(education_lang_id):
                        continue
                except (TypeError, ValueError):
                    continue
                for tu in obj.get('tuition_fees') or []:
                    if not isinstance(tu, dict):
                        continue
                    try:
                        if int(tu.get('education_language_id')) == int(education_lang_id):
                            return (lang.get('education_language_name_uz')
                                    or lang.get('name_uz') or lang.get('name'))
                    except (TypeError, ValueError):
                        continue
        return None

    education_language_name = get_education_language_name(directions, int(data_state.get('direction_id')), int(education_lang_id))

    await state.update_data(education_lang_id=education_lang_id, tuition_fee=education_tuition_fee, edu_lang_name=education_language_name)

    # Fetch state data
    ic(1924)
    all_state_data = await state.get_data()
    token_ = all_state_data.get('token')
    degree_id = int(all_state_data.get('degree_id'))
    direction_id = int(all_state_data.get('direction_id'))
    education_type_id = int(all_state_data.get('education_type'))
    transfer_user = all_state_data.get('transfer_user')
    chat_id_user = str(callback_query.message.chat.id)
    file_work_experience = all_state_data.get('file_certificate', None)
    phone = all_state_data.get('phone')
    user_verify = all_state_data.get('user_verify')
    birth_date = all_state_data.get('birth_date')
    document_obj = all_state_data.get('document')
    ic(document_obj, birth_date)

 
    birth_date_new = all_state_data.get('birth_date_new')
    document_new = all_state_data.get('document_new')
    ic(birth_date_new, document_new)
    # application_form_info = await send_req.application_form_info(birth_date_new,document_new,token_)

    refresh_token = all_state_data.get('refresh_token')
    purpose = None
    if transfer_user:
        purpose = "abiturient"
    else:
        purpose = "o'qishni ko'chirish"
    new_obj = {
        "purposeOfApplication": purpose,
        "user_pinfl": {"birth_date_new": birth_date_new, "document_new": document_new},
        "refreshToken": refresh_token,
        "isRegister": True,
        "user_phone": phone,
        "user": user_verify,
        "token": token_,
        "degree_id": degree_id,
        "direction_id": direction_id,
        "education_type_id": education_type_id,
    }
    await send_group(new_obj)
    selected_mess = f"Tanlangan {education_language_name}"
    
    await callback_query.answer()
    await EducationData.menu.set()
    await callback_query.message.answer(saved_message+'\n'+selected_mess, parse_mode="HTML")
    await callback_query.message.answer(
        f"✅ <b>Tanlangan Yo'nalish Narxi</b>\n"
        f"--------------------------------\n"
        f"💵 <i>Narxi:</i> <b>{education_tuition_fee}</b> so'm\n",
        parse_mode='HTML'
    )


    applicant_status = await send_applicant_data(token_, transfer_user, chat_id_user, degree_id, direction_id, education_lang_id, education_type_id, file_work_experience)
    ic(applicant_status)

    if applicant_status == 201:
        await callback_query.message.answer(application_submited, reply_markup=menu)
        await EducationData.menu.set()
    else:
        await callback_query.message.answer(
            "Ariza topshirishda xatolik yuz berdi, admin ogohlantirildi keyinroq urinib ko'ring, botni qayta ishga tushirib ariza topshiring.",
            reply_markup=menu
        )

async def send_applicant_data(token, transfer_user, chat_id_user, degree_id, direction_id, education_lang_id, education_type_id, file_work_experience=None):
    if education_type_id == 2:
        return await send_req.applicants(
            token, transfer_user, chat_id_user, degree_id, direction_id, education_lang_id, education_type_id, file_work_experience
        )
    else:
        return await send_req.applicants(
            token, transfer_user, chat_id_user, degree_id, direction_id, education_lang_id, education_type_id
        )
