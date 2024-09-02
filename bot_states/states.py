from aiogram.fsm.state import State, StatesGroup


class UserRegistrationForm(StatesGroup):
    """
    Form used to register a new user.
    Contains such user data as: name, age, city, district, about, photo.
    """

    name = State()
    age = State()
    sex = State()
    location = State()
    about = State()
    photo = State()
    create_user = State()


class BotByStartLaunch(StatesGroup):
    """
    Used to restrict user from using the bot before using the /start command
    """

    Running = State()


class BotMode(StatesGroup):
    """
    Bot states used after user registration
    """

    MainKeyboardMode = State()
    CheckProfilesMode = State()
    DeleteProfileState = State()
    profiles_search_filters = State()


class Admin(StatesGroup):
    """
    State for admin user
    """

    IsIn = State()
    FilterUsers = State()
