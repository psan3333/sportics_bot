from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from pydantic.types import ClassVar


# TODO: локализовать пользователей для просмотра для каждого отдельного пользователя бота - идея создания контейнера в контексте бота,
# TODO: который будет получать пользователя через метод контейнера и в нем будет уже менять отдельного пользователя
class UsersContainer:
    def __init__(self, users=[]):
        self.__users = users

    def set_users(self, users):
        self.users = users

    @property
    def users(self, index):
        return self.__users[index]


class UserProfileCheck(CallbackData, prefix="check"):
    action: str
    user_idx: int


class DeleteUserLink(CallbackData, prefix="link"):
    action: str


def user_profile_check_kb(users, user_idx=0):
    """
    Inline keyboard for bot users' profile checking
    """
    builder = InlineKeyboardBuilder()
    UsersContainer.users = users
    builder.row(
        InlineKeyboardButton(
            text="◀ Предыдущий",
            callback_data=UserProfileCheck(action="prev", user_idx=user_idx).pack(),
        ),
        InlineKeyboardButton(
            text="Следующий ▶",
            callback_data=UserProfileCheck(action="next", user_idx=user_idx).pack(),
        ),
        width=2,
    )
    builder.row(
        InlineKeyboardButton(
            text="Написать",
            callback_data=UserProfileCheck(action="check", user_idx=user_idx).pack(),
        ),
        InlineKeyboardButton(
            text="Выйти из режима",
            callback_data=UserProfileCheck(action="exit", user_idx=user_idx).pack(),
        ),
        width=2,
    )
    return builder.as_markup()


def url_btn_markup(text: str, url: str, cancel_text):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=text, url=url),
                InlineKeyboardButton(
                    text=cancel_text,
                    callback_data=DeleteUserLink(action="delete_user_link").pack(),
                ),
            ]
        ]
    )


def not_bot_kb(user_idx):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Я не бот!",
                    callback_data=UserProfileCheck(
                        action="not_bot", user_idx=user_idx
                    ).pack(),
                )
            ]
        ]
    )
    return kb


def admin_check(users, user_idx=0):
    """
    Inline keyboard for admin to check users' profiles
    """
    builder = InlineKeyboardBuilder()
    UsersContainer.users = users
    builder.row(
        InlineKeyboardButton(
            text="◀ Предыдущий",
            callback_data=UserProfileCheck(action="prev", user_idx=user_idx).pack(),
        ),
        InlineKeyboardButton(
            text="Следующий ▶",
            callback_data=UserProfileCheck(action="next", user_idx=user_idx).pack(),
        ),
        width=2,
    )
    builder.row(
        InlineKeyboardButton(
            text="Удалить",
            callback_data=UserProfileCheck(
                action="delete_user", user_idx=user_idx
            ).pack(),
        ),
        width=2,
    )
    return builder.as_markup()
