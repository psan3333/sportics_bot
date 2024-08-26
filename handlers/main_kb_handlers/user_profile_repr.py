from aiogram import Bot
from aiogram.types import Message, InlineKeyboardMarkup, InputMediaPhoto

from database_actions import Database


class UserProfile:
    def __init__(self, user_data):
        self.user_data = user_data

    @staticmethod
    def get_profile_string(user_data):
        return f'\n{user_data["name"]}, {user_data["age"]}, {user_data["sex"]}.\n\nО себе:\n{user_data["about"]}'

    @staticmethod
    def get_check_profile_string(user_data):
        return f"{UserProfile.get_profile_string(user_data)}\n\nРасстояние до пользователя - {user_data['distance_to_user']}км."

    async def show_user_profile(user_data, **bot_data):
        message: Message = bot_data.get('message')
        reply_markup: InlineKeyboardMarkup = bot_data.get('reply_markup')
        _db: Database = bot_data.get('_db')
        user_photo = await _db.get_user_bot_profile_photo(user_data['user_id'])

        user_profile_string = UserProfile.get_check_profile_string(user_data)\
            if 'distance_to_user' in user_data\
            else UserProfile.get_profile_string(user_data)

        message = await message.answer_photo(
            user_photo,
            caption=user_profile_string,
            reply_markup=reply_markup
        )
        return message

    async def replace_profile_to_check(user_data, **bot_data):
        message: Message = bot_data.get('message')
        _db: Database = bot_data.get('_db')
        reply_markup: InlineKeyboardMarkup = bot_data.get('reply_markup')
        user_photo_file = await _db.get_user_bot_profile_photo(user_data['user_id'])
        user_photo = InputMediaPhoto(media=user_photo_file)

        await message.edit_media(
            media=user_photo
        )
        await message.edit_caption(
            caption=UserProfile.get_check_profile_string(user_data),
            reply_markup=reply_markup
        )
