from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

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
            [KeyboardButton(text="Назад")]
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


# Админ меню
def admin_panel() -> InlineKeyboardMarkup:
    """Клавиатура админ-панели"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📩 Рассылка", callback_data="admin_mailing")],
        [InlineKeyboardButton(text="👤 Управление пользователями", callback_data="admin_users")],
        [InlineKeyboardButton(text="⚙ Настройки", callback_data="admin_settings")]
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