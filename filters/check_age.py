from aiogram.filters import BaseFilter
from aiogram.types import Message

from bot_data.constants import MIN_USER_AGE, MAX_USER_AGE


class CheckAge(BaseFilter):
    async def __call__(self, message: Message):
        user_input = message.text

        if (
            not user_input.isnumeric()
            or user_input.count(".") > 1
            or int(user_input) > MAX_USER_AGE
        ):
            await message.answer(
                f"Пожалуйста, введите количество полных лет одним числом.\nДопустимый возраст - от {MIN_USER_AGE} до {MAX_USER_AGE} лет."
            )
            return False

        # check for acceptable age
        if int(user_input) < MIN_USER_AGE:
            await message.answer(
                "Пользователям вашего возраста запрещено использовать данного бота, сорян)))))"
            )
            # TODO: Заблочить данного пользователя! Отправить в черный список id этого пользователя.
            return False
        return True
