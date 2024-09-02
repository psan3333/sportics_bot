import aiofiles

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


async def unknown_command_message(message: Message):
    await message.answer(
        "Неизвестная команда.\nЧтобы узнать, как пользоваться ботом, напишите /help",
    )


@router.message(CommandStart(), IsAdmin())
async def start_admin_session(message: Message, state: FSMContext):
    await state.set_state(Admin.IsIn)
    await message.answer(
        "Выбрать действие:",
        reply_markup=basic_reply_kb_builder(["Проверить пользователей", "/exit"]),
    )


@router.message(CommandStart())
async def start(message: Message, state: FSMContext, _db: Database):
    # Сделать проверку на регистрация пользователя, чтобы не было коллизиц в базе данных
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
        "Видно, что вы не пользовались данным ботом.\nДавайте тогда зарегистрируем вас, чтобы и вы могли пользоваться ботом, и пользователи могли вас видеть 🔎.\nПеред тем, как продолжить, прочитайте ползовательское соглашение.\nЕго вы можете увидеть, нажав на /user_agreement",
        reply_markup=create_user_card_kb,
    )


async def print_text_file_into_bot(message: Message, filename: str):
    async with aiofiles.open(filename, encoding="utf-8") as f:
        file_text = await f.read()
        await message.answer(file_text)


@router.message(Command("user_agreement"))
async def show_user_agreement(message: Message):
    user_aggrement_file = "./bot_data/on_help_data/user_aggrement.txt"
    await print_text_file_into_bot(message, user_aggrement_file)


@router.message(Command("about_author"))
async def show_user_agreement(message: Message):
    about_author_file = "./bot_data/on_help_data/about_author.txt"
    await print_text_file_into_bot(message, about_author_file)


@router.message(Command("help"))
async def on_help_handler(message: Message):
    help_message_file = "./bot_data/on_help_data/on_help_text.txt"
    await print_text_file_into_bot(message, help_message_file)


@router.message(BotMode.MainKeyboardMode, Command("delete_profile"))
async def on_delete_profile(message: Message, state: FSMContext, _db: Database):
    await state.set_state(BotMode.DeleteProfileState)
    await message.answer(
        "Вы уверены, что хотите удалить профиль?",
        reply_markup=basic_reply_kb_builder(["Да", "Нет"]),
    )


@router.message(BotMode.DeleteProfileState, F.text.in_(["Да", "Нет"]))
async def on_delete_profile(message: Message, state: FSMContext, _db: Database):
    if message.text == "Да":
        await _db.delete_user(message.from_user.id)
        await state.clear()
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
    await unknown_command_message(message)
