import datetime
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def basic_kb_builder(
    text: str | list,
    rows: list = [],
    input_field_placeholder: str | None = None
):
    builder = ReplyKeyboardBuilder()

    if isinstance(text, str):
        text = [text]

    if len(rows) > 0:
        start_row_index = 0
        for row in rows:
            end_row_index = start_row_index + row
            builder.row(*[KeyboardButton(text=item)
                        for item in text[start_row_index:end_row_index]])
            start_row_index = end_row_index
    else:
        [builder.button(text=txt) for txt in text]
    result_kb = builder.as_markup()
    result_kb.resize_keyboard = True
    result_kb.input_field_placeholder = input_field_placeholder
    result_kb.one_time_keyboard = True
    return result_kb
