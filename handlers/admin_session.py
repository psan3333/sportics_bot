from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot_states import Admin
from database_actions import Database
from filters import IsAdmin
from keyboards.reply import remove_keyboard_kb
from keyboards.fabric import admin_check, UserProfileCheck, UsersContainer
from handlers.main_kb_handlers.user_profile_repr import UserProfile

router = Router()


@router.message(Admin.IsIn, F.text == "Проверить пользователей")
async def start_users_filtereing(
    message: Message, state: FSMContext, _db: Database, _users_to_check: UsersContainer
):
    await state.update_data(IsIn="Admin")
    users_to_check = await _db.get_all_users(message=message)
    if len(users_to_check) == 0:
        await message.answer(
            "С данными фильтрами не нашлось ни одного пользователя(\nПопробуйте изменить свои параметры поиска."
        )
        return
    _users_to_check.set_users(users_to_check)
    user_data = await _db.get_user_by_id(users_to_check[0]["user_id"])
    await message.answer(
        "Вы выбрали просмотр других пользователей бота.",
        reply_markup=remove_keyboard_kb,
    )
    await state.set_state(Admin.FilterUsers)
    profile_message_id = await UserProfile.show_user_profile(
        user_data, message=message, _db=_db, reply_markup=admin_check()
    )
    await state.update_data(CheckProfiles=profile_message_id)


@router.callback_query(
    Admin.FilterUsers,
    UserProfileCheck.filter(F.action.in_(["prev", "next", "delete_user"])),
)
async def switch_user_handler(
    call: CallbackQuery,
    callback_data: UserProfileCheck,
    state: FSMContext,
    _db: Database,
    bot: Bot,
    _users_to_check: UsersContainer,
):
    user_idx = int(callback_data.user_idx)

    if callback_data.action == "prev":
        user_idx = user_idx - 1 if user_idx - 1 >= 0 else user_idx
    elif callback_data.action == "next":
        user_idx = user_idx + 1 if user_idx + 1 < len(_users_to_check) else user_idx
    elif callback_data.action == "delete_user":
        await _db.delete_user(_users_to_check[user_idx]["user_id"])
        _users_to_check.pop(user_idx)

    if len(_users_to_check) > 0:
        current_user_data = await _db.get_user_by_id(
            _users_to_check[user_idx]["user_id"]
        )
        data = await state.get_data()
        await UserProfile.replace_profile_to_check(
            user_data=current_user_data,
            _db=_db,
            message=data["CheckProfiles"],
            reply_markup=admin_check(user_idx=user_idx),
        )
    else:
        await call.message.answer("Все пользователи проверены")

    await call.answer()


@router.message()
async def unknow_command_handler(message: Message, state: FSMContext):
    await message.answer(
        "Неизвестная команда.\nЧтобы узнать, как пользоваться ботом, напишите /help"
    )


@router.message()
async def unknow_command_handler(message: Message):
    await message.answer(
        "Неизвестная команда.\nЧтобы узнать, как пользоваться ботом, напишите /help"
    )
