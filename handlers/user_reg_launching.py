from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards.builders import basic_kb_builder
from keyboards.reply import create_user_card_kb
from bot_states import UserRegistrationForm, BotByStartLaunch

router = Router()


@router.message(BotByStartLaunch.Running, F.text == "Продолжить")
async def fill_profile_form(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(UserRegistrationForm.name)
    await message.answer(
        "Для начала введите ваше имя.",
        reply_markup=basic_kb_builder(message.from_user.first_name),
    )


@router.message(BotByStartLaunch.Running)
async def start_bot_handler(message: Message, state: FSMContext):
    await message.answer(
        "Нажмите, пожалуйста, на кнопку 'Продолжить', чтобы начать работу с ботом.",
        reply_markup=create_user_card_kb
    )
