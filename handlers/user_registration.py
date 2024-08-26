import os

from aiogram import Router, F, Bot
from aiogram.types import Message, BufferedInputFile
from aiogram.fsm.context import FSMContext

from bot_states import UserRegistrationForm, BotMode
from bot_data.constants import main_kb_button_names
from keyboards.reply import get_location_kb, sex_kb, main_bot_keyboard
from keyboards.builders import basic_kb_builder
from filters import CheckAge
from database_actions import Database
from handlers.main_kb_handlers.user_profile_repr import UserProfile

router = Router()


# UserForm.name field setup
@router.message(UserRegistrationForm.name, ~F.text)
async def wrong_user_form_name_input(message: Message, state: FSMContext):
    await message.answer(
        'Введите ваше имя текстом. ⌨️',
        reply_markup=basic_kb_builder(message.from_user.first_name)
    )


@router.message(UserRegistrationForm.name, F.text)
async def set_user_form_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(UserRegistrationForm.age)
    await message.answer(
        'Дальше введите ваш возраст.\nСколько вам полных лет?'
    )


# UserForm.age field setup
@router.message(UserRegistrationForm.age, ~F.text)
async def wrong_type_user_form_age_input(message: Message, state: FSMContext):
    await message.answer("Пожалуйста, введите ваш возраст одним числом - количество ваших полных лет. ⌨️")


@router.message(UserRegistrationForm.age, CheckAge())
async def set_user_form_age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await state.set_state(UserRegistrationForm.sex)
    await message.answer(
        "Дальше выберите ваш пол. Для выбора есть кноки около панели ввода.\n♀️ или ♂️",
        reply_markup=sex_kb
    )


# UserForm.sex field setup
@router.message(UserRegistrationForm.sex, F.text.in_(["Парень ♂️", "Девушка ♀️"]))
async def set_user_form_sex(message: Message, state: FSMContext):
    await state.update_data(sex=message.text)
    await state.set_state(UserRegistrationForm.location)
    await message.answer(
        'Отлично! Дальше, чтобы вам было легче найти себе компанию для тренировок, мы предлагаем использовать вашу геолокацию.📍\nДругие пользователи не будут видеть отправленные вами данные геолокации.\n\nРаботает только для телефонов. 📱',
        reply_markup=get_location_kb
    )


@router.message(UserRegistrationForm.sex)
async def wrong_user_form_sex_input(message: Message, state: FSMContext):
    await message.answer(
        "Пожалуйтса, выберите пол, нажав на одну из кнопок на клавиатуре около панели ввода. ⌨️",
        reply_markup=sex_kb
    )


# UserForm.location field setup
@router.message(UserRegistrationForm.location, F.location)
async def set_user_form_location(message: Message, state: FSMContext):
    user_location = {
        "latitude": message.location.latitude,
        "longitude": message.location.longitude
    }
    await state.update_data(location=user_location)
    await state.set_state(UserRegistrationForm.about)
    await message.answer(
        f'Отлично! 🔥\nДальше немного расскажите о себе и ваших предпочтениях. ℹ️'
    )


# UserForm.about field setup
@router.message(UserRegistrationForm.about, F.text)
async def set_user_form_about(message: Message, state: FSMContext):
    await state.update_data(about=message.text)
    await state.set_state(UserRegistrationForm.photo)
    example_photo_filename = os.path.join(
        os.getcwd(), './bot_data/profile_photo_example.png')
    example_photo_file = open(example_photo_filename, 'rb')
    example_photo = BufferedInputFile(
        example_photo_file.read(),
        "profile_photo_example.png"
    )
    await message.answer(
        "Остался последний шаг для того, чтобы вас зарегистрировать - фотография пользователя. 📷",
    )
    await message.answer_photo(
        photo=example_photo,
        caption=f'\nВаше имя, возраст, пол.\nО себе:\nДальше будет ваше описание, которое вы ввели.',
    )
    await message.answer(
        'Это шаблон того, как будет выглядить ваш конечный профиль.\nВы можете использовать фото своего профиля (кнопка снизу) или загрузить свою фотографию.',
        reply_markup=basic_kb_builder("Фото профиля")
    )


@router.message(UserRegistrationForm.about, ~F.text)
async def wrong_user_form_about_input(message: Message, state: FSMContext):
    await message.answer(
        "Пожалуйста, используйте строку ввода для того, чтобы делать свое описание."
    )


# UserForm.photo field setup
async def view_final_user_profile(message: Message, state: FSMContext, photo: str):
    await state.update_data(photo=photo)
    data = await state.get_data()
    await message.answer("Так будет выглядет ваш профиль.")
    await message.answer_photo(
        data['photo'],
        caption=UserProfile.get_profile_string(data),
        reply_markup=basic_kb_builder(["Создать"])
    )


@router.message(UserRegistrationForm.photo, F.photo)
async def set_user_form_photo(message: Message, state: FSMContext):
    photo = message.photo[-1].file_id
    await view_final_user_profile(message, state, photo)


@router.message(UserRegistrationForm.photo, F.text == "Фото профиля")
async def set_user_form_photo_profile(message: Message, state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    profiles_photos = await bot.get_user_profile_photos(user_id=user_id, limit=1)
    photo = profiles_photos.photos[0][-1].file_id
    await view_final_user_profile(message, state, photo)


@router.message(UserRegistrationForm.photo, F.text == "Создать")
async def upload_to_database_user_form_info(message: Message, state: FSMContext, _db: Database, bot: Bot):
    user_data = await state.get_data()
    user_data['user_id'] = message.from_user.id
    user_data['username'] = message.from_user.username
    user_data['checked_by_admin'] = False
    result = await _db.insert_user(user_data, bot)
    # print(result)
    await state.clear()
    await state.set_state(BotMode.MainKeyboardMode)
    await message.answer(
        "🔥Регистрация прошла успешно!🔥\nТеперь вы можете находить себе компанию для тренировок.🔎"
    )
    await message.answer(
        f"Изначальные фильтры: любой пол и поиск в радиусе 5 километров. \nЧтобы поменять фильтры, нажмите на кнопку '{main_kb_button_names[1]}'.",
        reply_markup=main_bot_keyboard()
    )


@router.message(UserRegistrationForm.photo, ~F.photo)
async def wrong_user_form_photo_input(message: Message, state: FSMContext):
    await message.answer(
        "Пожалуйста, используйте фотография для вашего профиля",
        reply_markup=basic_kb_builder("Фото профиля")
    )
