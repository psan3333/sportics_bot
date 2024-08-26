MIN_USER_AGE = 16
"""Minimal user age allowed to use this telegram bot"""
MAX_USER_AGE = 120
"""Maximal user age allowed to use this telegram bot"""
FETCH_USERS_NUMBER = 100
"""Number of user to fetch for profiles viewing."""
main_kb_button_names = [
    "Смотреть 🏃‍♂️",
    "Фильтры 🔎⚙️",
    "Мой профиль 👤",
    "Поддержать 🤝"
]
"""Names for main keyboard buttons."""
main_kb_actions = [
    "watch_profiles",
    "profiles_query_filters",
    "watch_own_profile",
    "donations"
]
"""Action names for BotMode.CheckProfiles state inline keyboard"""
