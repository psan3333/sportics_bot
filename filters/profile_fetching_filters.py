from aiogram import Bot, Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards.builders import basic_reply_kb_builder
from keyboards.reply import sex_filters_kb, main_bot_keyboard
from bot_states import BotMode

router = Router()


@router.message(
    BotMode.profiles_search_filters, F.text.in_(["Парни", "Девушки", "Неважно"])
)
async def set_filters_sex(message: Message, state: FSMContext):
    filters = {"sex": message.text}
    await state.update_data(profiles_search_filters=filters)
    await message.answer(
        "Дальше предлагаем ввести радиус поиска\nИзначально бот ищет в радиусе 5 километров.",
        reply_markup=basic_reply_kb_builder(["1км", "3км", "5км"]),
    )


@router.message(BotMode.profiles_search_filters, F.text.in_(["1км", "3км", "5км"]))
async def set_filters_radius_from_button(message: Message, state: FSMContext):
    filters = await state.get_data()
    filters["profiles_search_filters"]["search_radius"] = int(message.text[0])
    await state.update_data(profiles_search_filters=filters["profiles_search_filters"])
    await state.set_state(BotMode.MainKeyboardMode)
    await message.answer("Фильтры установлены!", reply_markup=main_bot_keyboard())


@router.message(BotMode.profiles_search_filters, F.text.isdigit())
async def set_filters_radius(message: Message, state: FSMContext):
    if int(message.text) > 50:
        await message.answer(
            "Очень большое расстояние для просмотра. Введите радиус поиска пользователей от 1 до 30 в киллометрах.",
            basic_reply_kb_builder(["1км", "3км", "5км"]),
        )
        return
    elif int(message.text) <= 0:
        await message.answer(
            "Расстояние не может быть меньше нуля или равное нулю. Введите радиус поиска от 1 до 30 в киллометрах.",
            basic_reply_kb_builder(["1км", "3км", "5км"]),
        )
        return

    filters = await state.get_data()
    filters["profiles_search_filters"]["search_radius"] = int(message.text)
    await state.update_data(profiles_search_filters=filters["profiles_search_filters"])
    await state.set_state(BotMode.MainKeyboardMode)
    await message.answer("Фильтры установлены!", reply_markup=main_bot_keyboard())


@router.message(BotMode.profiles_search_filters, F.text)
async def wrong_filters_input(message: Message, state: FSMContext):
    await message.answer(
        "Неправильное значение. Для того, чтобы фильтровать по полу пользователя, нажмите на одну из кнопок, где написано, как фильтровать по полу. Для того, чтобы фильтровать по радиусу поиска, введите радиус поиска в километрах или нажмите на появившиеся после выбора пола клавиши.\nПридется заново выбрать подходящие вам фильтры. Это займет 30 секунд или меньше.",
        reply_markup=sex_filters_kb,
    )
