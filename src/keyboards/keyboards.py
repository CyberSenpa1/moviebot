from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_menu_keyboard():
    """
    Создает клавиатуру главного меню.
    """
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Профиль")],
            [KeyboardButton(text="Изменить профиль")],
            [KeyboardButton(text="Найти фильм")],
        ],
        resize_keyboard=True,  # Клавиатура подстраивается под размер экрана
        one_time_keyboard=False  # Клавиатура не скрывается после нажатия
    )
    return keyboard

def update_profile_kb():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Имя")],
            [KeyboardButton(text="Возраст")],
            [KeyboardButton(text="Пол")],
            [KeyboardButton(text="Назад")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    return keyboard



def sex_choose_kb():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Мужской")],
            [KeyboardButton(text="Женский")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    return keyboard


# Админ меню
def admin_panel() -> InlineKeyboardMarkup:
    """Клавиатура админ-панели"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📩 Рассылка", callback_data="admin_mailing")],
        [InlineKeyboardButton(text="Главное меню", callback_data="back_to_menu")]
    ])

def confirm_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Начать рассылку", callback_data="confirm_mailing")],
        [InlineKeyboardButton(text="✏️ Изменить текст", callback_data="admin_mailing")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_back")]
    ])

def cancel_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_back")]

    ])

def movie_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Поиск фильма по названию", callback_data="find_movie")],
        [InlineKeyboardButton(text="Рандомный фильм", callback_data="random_movie")],
        [InlineKeyboardButton(text="Рандомный фильм по жанру", callback_data="random_movie_genre")],
    ])


def genre_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Комедия", callback_data="comedy_btn")],
            [InlineKeyboardButton(text="Драма", callback_data="drama_btn")],
            [InlineKeyboardButton(text="Фэнтези", callback_data="fantasy_btn")],
            [InlineKeyboardButton(text="Аниме", callback_data="anime_btn")],
            [InlineKeyboardButton(text="Приключения", callback_data="adventure_btn")],
            [InlineKeyboardButton(text="Ужасы", callback_data="horror_btn")],
            [InlineKeyboardButton(text="Назад", callback_data="back_to_menu")]
        ],
    )


def random_movie_panel():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Дальше", callback_data="random_movie")],
        [InlineKeyboardButton(text="Меню", callback_data="back_to_menu")]
    ])