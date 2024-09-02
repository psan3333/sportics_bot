from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards.reply import remove_keyboard_kb, sex_filters_kb, main_bot_keyboard
from keyboards.fabric import user_profile_check_kb, url_btn_markup, UsersContainer

from handlers.main_kb_handlers.user_profile_repr import UserProfile
from bot_data.constants import main_kb_button_names
from bot_states import BotMode
from database_actions import Database
from config_reader import config

router = Router()


@router.message(BotMode.MainKeyboardMode, F.text.in_(main_kb_button_names))
async def main_keyboard_handler(
    message: Message, state: FSMContext, _db: Database, _users_to_check: UsersContainer
):
    if message.text == main_kb_button_names[0]:
        users_to_check = await _db.get_closest_users(
            user_id=message.from_user.id, bot_state=state
        )
        if len(users_to_check) == 0:
            await message.answer(
                "С данными фильтрами не нашлось ни одного пользователя(\nПопробуйте изменить свои параметры поиска."
            )
            return
        _users_to_check.set_users(users_to_check)
        await state.set_state(BotMode.CheckProfilesMode)
        user_data = await _db.get_user_by_id(
            users_to_check[0]["user_id"], users_to_check[0]["distance_to_user"]
        )
        await message.answer(
            "Вы выбрали просмотр других пользователей бота.",
            reply_markup=remove_keyboard_kb,
        )
        profile_message_id = await UserProfile.show_user_profile(
            user_data,
            message=message,
            _db=_db,
            reply_markup=user_profile_check_kb(),
        )
        await state.update_data(CheckProfiles=profile_message_id)
    # profiles_query_filters
    elif message.text == main_kb_button_names[1]:
        await state.set_state(BotMode.profiles_search_filters)
        await message.answer(
            "Давайте настроим фильтры поиска других пользователей.\nВсего есть два фильтра поиска:\n1. Пол пользователя.\n2. Радиус поиска.",
            reply_markup=sex_filters_kb,
        )
    elif message.text == main_kb_button_names[2]:
        user_data = await _db.get_user_by_id(message.from_user.id)
        await message.answer("Так выглядит ваш профиль на данный момент.")
        await UserProfile.show_user_profile(
            user_data, message=message, _db=_db, reply_markup=main_bot_keyboard()
        )
    elif message.text == main_kb_button_names[3]:
        await message.answer(
            text="Поддержка проекта происходит через сервис CloudTips. Ниже будет ссылка на пожертвования для проекта! Большое вам спасибо!",
            reply_markup=url_btn_markup(
                text="Ссылка",
                url=config.DONATIONS_URL.get_secret_value(),
                cancel_text="Убрать ссылку",
            ),
        )
