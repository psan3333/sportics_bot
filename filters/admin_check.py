from aiogram.filters import BaseFilter
from aiogram.types import Message

from config_reader import config


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message):
        return (
            True
            if message.from_user.id == int(config.ADMIN_ID.get_secret_value())
            else False
        )
