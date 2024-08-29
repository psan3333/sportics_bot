from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext

from keyboards.reply import create_user_card_kb, start_bot_kb, main_bot_keyboard
from keyboards.builders import basic_reply_kb_builder
from bot_states import BotByStartLaunch, BotMode, Admin
from database_actions import Database
from filters import IsAdmin

router = Router()
bot_start_initiated = False


@router.message(CommandStart(), IsAdmin())
async def start_admin_session(message: Message, state: FSMContext):
    global bot_start_initiated
    bot_start_initiated = True
    await state.set_state(Admin.IsIn)
    await message.answer(
        "Выбрать действие:",
        reply_markup=basic_reply_kb_builder(["Проверить пользователей", "/exit"]),
    )


@router.message(CommandStart())
async def start(message: Message, state: FSMContext, _db: Database):
    # Сделать проверку на регистрация пользователя, чтобы не было коллизиц в базе данных
    global bot_start_initiated
    if bot_start_initiated:
        await message.answer(
            "Бот уже запущен. Можете продолжать его использование.\nЕсли нужна помощь в использовании бота, напишите или нажмите на /help"
        )
        return
    bot_start_initiated = True
    check_user = await _db.get_user_by_id(message.from_user.id)
    if check_user is not None:
        await state.set_state(BotMode.MainKeyboardMode)
        await message.answer(
            f"Здравствуйте, {message.from_user.first_name}!✋\n🔥Рады снова вас приветствовать!🔥\nЕсли нужна помощь в использовании бота, используйте команду /help 🆘",
            reply_markup=main_bot_keyboard(),
        )
        return
    await state.set_state(BotByStartLaunch.Running)
    await message.answer(
        "🔥Добро пожаловать в Sportics Bot - бот для поиска компании для тренировок и новых знакомств!🔥"
    )
    await message.answer(
        "Видно, что вы не пользовались данным ботом.\nДавайте тогда зарегестрируем вас, чтобы и вы могли пользоваться ботом, и пользователи могли вас видеть 🔎.\nНажмите 'Продолжить', чтобы начать регистрацию.",
        reply_markup=create_user_card_kb,
    )


@router.message(CommandStart())
async def start(message: Message, state: FSMContext, _db: Database):
    # Сделать проверку на регистрация пользователя, чтобы не было коллизиц в базе данных
    global bot_start_initiated
    if bot_start_initiated:
        await message.answer(
            "Бот уже запущен. Можете продолжать его использование.\nЕсли нужна помощь в использовании бота, напишите или нажмите на /help"
        )
        return
    bot_start_initiated = True
    check_user = await _db.get_user_by_id(message.from_user.id)
    if check_user is not None:
        await state.set_state(BotMode.MainKeyboardMode)
        await message.answer(
            f"Здравствуйте, {message.from_user.first_name}!✋\n🔥Рады снова вас приветствовать!🔥\nЕсли нужна помощь в использовании бота, используйте команду /help 🆘",
            reply_markup=main_bot_keyboard(),
        )
        return
    await state.set_state(BotByStartLaunch.Running)
    await message.answer(
        "🔥Добро пожаловать в Sportics Bot - бот для поиска компании для тренировок и новых знакомств!🔥"
    )
    await message.answer(
        "Видно, что вы не пользовались данным ботом.\nДавайте тогда зарегестрируем вас, чтобы и вы могли пользоваться ботом, и пользователи могли вас видеть 🔎.\nНажмите 'Продолжить', чтобы начать регистрацию.",
        reply_markup=create_user_card_kb,
    )


@router.message(Command("help"))
async def on_help_handler(message: Message):
    help_message_file = "./bot_data/on_help_data/on_help_text.txt"
    file = open(help_message_file, encoding="utf-8")
    help_text = file.read()
    await message.answer(help_text)


@router.message(BotMode.MainKeyboardMode, Command("exit"))
async def on_exit_handler(message: Message, state: FSMContext):
    global bot_start_initiated
    await state.clear()
    bot_start_initiated = False
    await message.answer(
        "Вы отлючились от бота.📴\nЧтобы снова использовать бота, используйте команду /start или нажмите на одноименную кнопку.🔘",
        reply_markup=start_bot_kb,
    )


@router.message(BotMode.MainKeyboardMode, Command("delete_profile"))
async def on_delete_profile(message: Message, state: FSMContext, _db: Database):
    await state.set_state(BotMode.DeleteProfileState)
    await message.answer(
        "Вы уверены, что хотите удалить профиль?",
        reply_markup=basic_reply_kb_builder(["Да", "Нет"]),
    )


@router.message(BotMode.DeleteProfileState, F.text.in_(["Да", "Нет"]))
async def on_delete_profile(message: Message, state: FSMContext, _db: Database):
    global bot_start_initiated
    if message.text == "Да":
        await _db.delete_user(message.from_user.id)
        await state.clear()
        bot_start_initiated = False
        await message.answer(
            "Ваш профиль был удален!\nДля того, чтобы снова использовать бота, введите или нажмите на команду /start",
            reply_markup=start_bot_kb,
        )
    else:
        await state.set_state(BotMode.MainKeyboardMode)
        await message.answer(
            "Хорошо. Тогда приятного вам пользования!", reply_markup=main_bot_keyboard()
        )


@router.message(StateFilter(None))
async def unknown_command_handler(message: Message):
    global bot_start_initiated
    if bot_start_initiated:
        await message.answer(
            "Неизвестная команда.\nЕсли нужна помощь в пользовании ботом, напишите /help"
        )
    else:
        await message.answer(
            "Неизвестная команда. Для того, чтобы запустить бота, нажмите на кнопку или введите команду /start.\nЧтобы узнать, как пользоваться ботом, напишите /help",
            reply_markup=start_bot_kb,
        )
