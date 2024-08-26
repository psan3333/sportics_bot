from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove
)

from bot_data.constants import main_kb_button_names
from keyboards.builders import basic_kb_builder

# keyboard used to start bot execution
start_bot_kb = basic_kb_builder(["/start", "/help"])

# two keyboards used for user registration
create_user_card_kb = basic_kb_builder("Продолжить")
sex_kb = basic_kb_builder(
    ["Парень ♂️", "Девушка ♀️"], input_field_placeholder="Пол")

get_location_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="Разрешить", request_location=True)
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="Геолокация",
    selective=True
)

sex_filters_kb = basic_kb_builder(
    ["Парни", "Девушки", "Неважно"], rows=[2, 1])

remove_keyboard_kb = ReplyKeyboardRemove()


def main_bot_keyboard():
    """Main keyboard layout. Contains four buttons:
    "Смотреть профили" - кнопка для просмотра профилей других пользователей
    "Фильтры просмотра" - кнопка для того, чтобы поставить фильтры для показа пользовательских карточек (радиус поиска и пол)
    "Посмотреть мой профиль" - кнопка для того, чтобы посмотреть свой профиль с возможностью его редактирования
    "На развитие бота) - кнопка для донатов))ы
    """
    return basic_kb_builder(main_kb_button_names, rows=[2, 2], input_field_placeholder="Действие")
