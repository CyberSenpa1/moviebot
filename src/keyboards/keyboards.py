from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu_keyboard():
    """
    Создает клавиатуру главного меню.
    """
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Профиль")],
            [KeyboardButton(text="Обновить профиль")],
            [KeyboardButton(text="Поиск фильмов")],
        ],
        resize_keyboard=True,  # Клавиатура подстраивается под размер экрана
        one_time_keyboard=False  # Клавиатура не скрывается после нажатия
    )
    return keyboard