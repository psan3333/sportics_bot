from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from handlers.main_kb_handlers.user_profile_repr import UserProfile
from keyboards.fabric import UserProfileCheck, DeleteUserLink, UsersContainer, user_profile_check_kb
from keyboards.reply import main_bot_keyboard
from keyboards.fabric import url_btn_markup, not_bot_kb
from bot_states import BotMode
from database_actions import Database

router = Router()


@router.callback_query(DeleteUserLink.filter(F.action.in_(["delete_user_link"])))
async def delete_user_link(
    call: CallbackQuery,
    callback_data: DeleteUserLink,
    state: FSMContext,
    bot: Bot
):
    """This callback query can be used to delete any type of message which uses DeleteUserLink callback data"""
    await bot.delete_message(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id
    )
    await call.answer()


@router.callback_query(BotMode.CheckProfilesMode, UserProfileCheck.filter(F.action.in_(["prev", "next", "check", "exit", "not_bot"])))
async def switch_user_handler(
    call: CallbackQuery,
    callback_data: UserProfileCheck,
    state: FSMContext,
    _db: Database,
    bot: Bot
):
    user_idx = int(callback_data.user_idx)

    if callback_data.action == "prev":
        user_idx = user_idx - 1 if user_idx - \
            1 >= 0 else user_idx
    elif callback_data.action == "next":
        user_idx = user_idx + 1 if user_idx + \
            1 < len(UsersContainer.users) else user_idx
    elif callback_data.action == "check":
        await call.message.answer(
            "Подтвердите, что вы не бот!",
            reply_markup=not_bot_kb(user_idx)
        )
        return
    elif callback_data.action == "not_bot":
        current_user_data = await _db.get_user_by_id(UsersContainer.users[user_idx]['user_id'])
        await bot.delete_message(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )
        await call.message.answer(
            f"Ссылка пользователя {current_user_data['name']}",
            reply_markup=url_btn_markup(
                text="Ссылка",
                url=f"tg://resolve?domain={current_user_data['username']}",
                cancel_text="Убрать"
            )
        )
        return
    elif callback_data.action == "exit":
        await state.set_state(BotMode.MainKeyboardMode)
        await call.message.answer(
            "Вы вышли из режима просмотра пользовательских профилей.",
            reply_markup=main_bot_keyboard()
        )
        await call.message.delete()
        return

    current_user_data = await _db.get_user_by_id(UsersContainer.users[user_idx]['user_id'], distance_to_user=UsersContainer.users[user_idx]['distance_to_user'])
    data = await state.get_data()
    await UserProfile.replace_profile_to_check(
        user_data=current_user_data,
        _db=_db,
        message=data['CheckProfiles'],
        reply_markup=user_profile_check_kb(
            users=UsersContainer.users,
            user_idx=user_idx
        )
    )

    await call.answer()
