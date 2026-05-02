TEXTS = {
    'uz': {
        # Rasm yuklash
        'photo_request': "Rasmingizni yuboring 3x4 formatda. jpg, png formatda",
        'image_accepted': "Rasm qabul qilindi",
        'image_error': "Iltimos, rasm yuboring. Rasmlar 3x4 formatda bo'lishi kerak.",
        'image_error_doc': "Iltimos, rasm yuboring. Rasmlar 3x4 formatda bo'lishi kerak.\nSiz yuborilgan fayl qabul qilinmadi",
        'file_processing_error': "Faylni qayta ishlashda xatolik yuz berdi: {error}",
        'general_error': "Xatolik yuz berdi: {error}",

        # Shaxsiy ma'lumotlar
        'enter_lastname': "Familiyangizni kiriting\nNamuna: Abdullayev",
        'enter_firstname': "Ismingizni kiriting Namuna: Alisher",
        'enter_thirdname': "Otangizni ismini kiriting\nNamuna: Najmiddin",
        'enter_document': "Passport seriyasini kiriting\nNamuna: AB1234567",
        'enter_document_retry': "Iltimos, passport seriyasini namunadagidek kiriting\nNamuna: AB1234567:",
        'enter_birthdate': "Tug'ilgan sanasini kiriting\nNamuna: yyyy-oo-kk, 2002-03-21",
        'enter_pin': "JSHSHR ni kiriting\nNamuna: 12345678901234",
        'select_gender': "Jinsni tanlang",
        'gender_male': "Erkak",
        'gender_female': "Ayol",
        'gender_invalid': "Iltimos, jinsingizni 'Erkak' yoki 'Ayol' dan birini tanlang.",
        'enter_birthplace': "Tug'ilgan joyingizi kiriting Namuna: Toshkent shahri",
        'enter_extranumber': "Qo'shimcha telefon raqamingizni kiriting Namuna: 901234567",
        'enter_email': "Emailingizni kiriting\n Namuna: yigitaliyeva@gmail.com",
        'email_invalid': "Email yaroqli emas. Iltimos yaroqli email kiriting. Email kichik harflardan tashkil topgan bo'lishi kerak.",

        # Natijalar
        'data_saved': "Ma'lumotlaringiz saqlandi",
        'data_not_saved': "Ma'lumotlaringiz saqlanmadi, qayta email kiriting.",
    },
    'ru': {
        # Rasm yuklash
        'photo_request': "Присылайте свою фотографию в формате 3х4. в формате jpg,png",
        'image_accepted': "Изображение принято",
        'image_error': "Пожалуйста, пришлите фотографию. Картинки должны быть в формате 3х4.",
        'image_error_doc': "Пожалуйста, пришлите фотографию. Изображения должны быть в формате 3x4.\nОтправленный вами файл не принят.",
        'file_processing_error': "Ошибка обработки файла: {error}",
        'general_error': "Произошла ошибка: {error}",

        # Shaxsiy ma'lumotlar
        'enter_lastname': "Введите свою фамилию\nПример: Абдуллаев",
        'enter_firstname': "Введите свое имя Пример: Алишер",
        'enter_thirdname': "Введите имя вашего отца\nПример: Наджмиддин",
        'enter_document': "Введите серию паспорта\nОбразец: AB1234567",
        'enter_document_retry': "Пожалуйста, введите серию паспорта, как показано в образце.\nОбразец: AB1234567:",
        'enter_birthdate': "Введите дату рождения\nПример: гггг-мм-дд, 2002-04-21",
        'enter_pin': "Введите ПИНФЛ\nПример: 12345678901234",
        'select_gender': "Выберите пол",
        'gender_male': "Мужской",
        'gender_female': "Женский",
        'gender_invalid': "Пожалуйста, выберите свой пол: «Мужской» или «Женский».",
        'enter_birthplace': "Введите место рождения Пример: город Ташкент",
        'enter_extranumber': "Введите дополнительный номер телефона. Пример: 901234567.",
        'enter_email': "Введите свой адрес электронной почты\n Пример: yigitaliyeva@gmail.com",
        'email_invalid': "Email не является допустимым. Введите, пожалуйста, действительный адрес электронной почты. Электронная почта должна быть написана строчными буквами.",

        # Natijalar
        'data_saved': "Ваша информация сохранена",
        'data_not_saved': "Ваши данные не были сохранены",
    }
}


def t(key: str, lang: str) -> str:
    return TEXTS.get(lang, TEXTS['uz']).get(key, key)
