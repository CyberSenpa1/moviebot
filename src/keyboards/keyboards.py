from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu_keyboard():
    """
    Создает клавиатуру главного меню.
    """
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Профиль")],
            [KeyboardButton(text="Изменить профиль")],
            [KeyboardButton(text="Поиск фильмов")],
        ],
        resize_keyboard=True,  # Клавиатура подстраивается под размер экрана
        one_time_keyboard=False  # Клавиатура не скрывается после нажатия
    )
    return keyboard

def update_profile_kb():
    keyboard = ReplyKeyboardMarkup(
        keyboard=(
            [KeyboardButton(text="Имя")],
            [KeyboardButton(text="Возраст")],
            [KeyboardButton(text="Пол")],
        )
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