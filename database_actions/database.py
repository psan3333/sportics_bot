import motor.motor_asyncio as aiomongo
import numpy as np
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCursor
from aiogram import Bot
from aiogram.types import BufferedInputFile
from aiogram.fsm.context import FSMContext
from haversine import haversine

from bot_data.constants import FETCH_USERS_NUMBER


class Database:
    def __init__(self, db: AsyncIOMotorClient):
        self.__db = db
        self.__fs = aiomongo.AsyncIOMotorGridFSBucket(self.__db.Users)

    def get_photo_filename(self, user_data) -> str:
        # TODO: убрать строку для тестирования
        # для тестирования программы
        return f"{user_data['photo']}_{1111101170}.jpg"
        # return f"{user_data['photo']}_{user_data['user_id']}.jpg" - правильная версия

    async def get_user_by_id(self, user_id, distance_to_user=None):
        user = await self.__db.Users.users.find_one({'user_id': user_id})
        if distance_to_user is not None:
            user['distance_to_user'] = distance_to_user
        return user

    async def get_user_bot_profile_photo(self, user_id) -> BufferedInputFile:
        user_data = await self.__db.Users.users.find_one({"user_id": user_id})
        file_id = await self.__db.Users['fs.files'].find_one({"filename": self.get_photo_filename(user_data)})
        grid_out = await self.__fs.open_download_stream(file_id['_id'])
        photo_contents: bytes = await grid_out.read()
        photo = BufferedInputFile(
            photo_contents,
            filename=self.get_photo_filename(user_data)
        )
        return photo

    async def is_user_banned(self, user_id):
        user = await self.__db.Users.user_black_list.find_one({'user_id': user_id})
        return True if user is not None else False

    async def sort_users_by_distance(self, current_user, all_users, search_radius):
        distances = []
        current_user_location = (
            current_user['location']['latitude'],
            current_user['location']['longitude']
        )

        for index, user in enumerate(all_users):
            user_location = (
                user['location']['latitude'],
                user['location']['longitude']
            )
            distances.append(haversine(current_user_location, user_location))
            all_users[index]['distance_to_user'] = round(distances[index], 1)
        distances = np.array(distances)
        sorted_indexes = np.argsort(distances)
        sorted_distances = np.sort(distances)
        distances_to_return = sorted_indexes[sorted_distances < search_radius]
        all_users = np.array(all_users)
        return all_users[distances_to_return].tolist()

    async def filter_users_by_sex(self, users, sex):
        if sex == "Неважно":
            return users
        else:
            sex = "Парень" if sex == "Парни" else "Девушка"
            filter_func = np.vectorize(
                lambda user: True if user['sex'] == sex else False)
            users = np.array(users)
            return users[filter_func(users)].tolist()

    async def get_closest_users(self, user_id, bot_state: FSMContext):
        # default search filters
        search_radius = 5
        sex = "Неважно"
        # set user filters
        state_data = await bot_state.get_data()
        if 'profiles_search_filters' in state_data:
            if 'search_radius' in state_data['profiles_search_filters']:
                search_radius = state_data['profiles_search_filters']['search_radius']
            if 'sex' in state_data['profiles_search_filters']:
                sex = state_data['profiles_search_filters']['sex']

        # get users from database
        user_data_id_projection = {
            "_id": False, "user_id": True, "location": True, "sex": True}
        users_cursor: AsyncIOMotorCursor = self.__db.Users.users.find(
            filter={}, projection=user_data_id_projection)
        total_number_of_users = await self.__db.Users.users.count_documents({})
        users: list = await users_cursor.to_list(total_number_of_users)

        # apply user filters
        current_user_list_idx, current_user_data = next(
            ((index, user) for index, user in enumerate(users) if user['user_id'] == user_id), None)
        users.pop(current_user_list_idx)
        sorted_by_distance_users = await self.sort_users_by_distance(current_user_data, users, search_radius)
        filtered_by_sex_users = await self.filter_users_by_sex(sorted_by_distance_users, sex)
        return filtered_by_sex_users[:FETCH_USERS_NUMBER]

    async def insert_user(self, user_data: dict, bot: Bot):
        """
        Insert new user into bot database
        """
        photo_file_info = await bot.get_file(user_data['photo'])
        photo_file_stream = await bot.download_file(photo_file_info.file_path)
        grid_in = self.__fs.open_upload_stream(
            f"{user_data['photo']}_{user_data['user_id']}.jpg")
        await grid_in.write(photo_file_stream)
        await grid_in.close()
        result = await self.__db.Users.users.insert_one(user_data)
        return result

    async def delete_user(self, user_id):
        user_data = await self.get_user_by_id(user_id)
        if user_data is not None:
            await self.__db.Users.users.delete_one({'user_id': user_id})
        file_id = await self.__db.Users['fs.files'].find_one({"filename": self.get_photo_filename(user_data)})
        if file_id is not None:
            self.__fs.delete(file_id['_id'])
