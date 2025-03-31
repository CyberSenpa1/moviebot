from aiogram import Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove

from src.database.crud import CRUDUser
from src.database.models import User
from src.keyboards.keyboards import main_menu_keyboard, sex_choose_kb, update_profile_kb

import logging

router = Router()

# Определение состояний для регистрации
class RegistrationStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_sex = State()

# Обработчик команды /start
@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext, session: AsyncSession):
    user_id = message.from_user.id
    crud_user = CRUDUser()

    # Проверяем, зарегистрирован ли пользователь
    user = await crud_user.get_by_telegram_id(session, user_id)
    if user:
        await message.answer("Вы уже зарегистрированы!", reply_markup=main_menu_keyboard())
        await state.set_state(Main_menu.waiting_for_field)
        return

    # Если пользователь не зарегистрирован, начинаем процесс регистрации
    await message.answer("Привет! Давай зарегистрируем тебя. Как тебя зовут?")
    await state.set_state(RegistrationStates.waiting_for_name)

# Обработчик для ввода имени
@router.message(StateFilter(RegistrationStates.waiting_for_name))
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Отлично! Сколько тебе лет?")
    await state.set_state(RegistrationStates.waiting_for_age)

# Обработчик для ввода возраста
@router.message(StateFilter(RegistrationStates.waiting_for_age))
async def process_age(message: types.Message, state: FSMContext):
    try:
        age = int(message.text)
        if age < 0 or age > 120:
            await message.answer("Пожалуйста, введите корректный возраст (от 0 до 120).")
            return
        await state.update_data(age=age)
        await message.answer("Отлично! Укажи свой пол (мужской/женский).")
        await state.set_state(RegistrationStates.waiting_for_sex)
    except ValueError:
        await message.answer("Пожалуйста, введите число.")

# Обработчик для ввода пола
@router.message(StateFilter(RegistrationStates.waiting_for_sex))
async def process_sex(message: types.Message, state: FSMContext, session: AsyncSession):
    sex = message.text.lower()
    if sex not in ["мужской", "женский"]:
        await message.answer("Пожалуйста, выберите 'мужской' или 'женский'.")
        return

    # Получаем все данные из состояния
    user_data = await state.get_data()
    name = user_data['name']
    age = user_data['age']
    user_id = message.from_user.id

    # Создаем пользователя в базе данных
    crud_user = CRUDUser()
    await crud_user.create(
        session,
        telegram_id=user_id,
        username=message.from_user.username,
        first_name=name,
        age=age,
        sex=sex
    )

    await message.answer(f"Спасибо, {name}! Ты успешно зарегистрирован.")
    await state.clear()

# команда update_profile

# Состояния для обновления данных
class UpdateUserStates(StatesGroup):
    waiting_for_field = State()
    waiting_for_new_name = State()
    waiting_for_new_age = State()
    waiting_for_new_sex = State()

# Команда /update_profile
@router.message(Command("update_profile"))
async def cmd_update_profile(message: types.Message, state: FSMContext):
    await message.answer("Что вы хотите обновить? (имя, возраст, пол)", reply_markup=update_profile_kb())
    await state.set_state(UpdateUserStates.waiting_for_field)

# Обработчик выбора поля
@router.message(UpdateUserStates.waiting_for_field)
async def process_field_choice(message: types.Message, state: FSMContext):
    field = message.text.lower()

    if field in ["имя", "возраст", "пол", "назад"]:
        await state.update_data(field=field)
        if field == "имя":
            await message.answer("Введите имя:")
            await state.set_state(UpdateUserStates.waiting_for_new_name)
        elif field == "возраст":
            await message.answer("Введите свой возраст:")
            await state.set_state(UpdateUserStates.waiting_for_new_age)
        elif field == "пол":
            await message.answer("Выберите пол (мужской/женский):", reply_markup=sex_choose_kb())
            await state.set_state(UpdateUserStates.waiting_for_new_sex)
        elif field == "назад":
            await message.answer("Вы в главном меню", reply_markup=main_menu_keyboard())
            await state.set_state(Main_menu.waiting_for_field)
    else:
        await message.answer("Пожалуйста, выберите одно из: имя, возраст, пол.", reply_markup=update_profile_kb())



# Обработчик для обновления имени
@router.message(UpdateUserStates.waiting_for_new_name)
async def process_new_name(message: types.Message, state: FSMContext, session: AsyncSession):
    user_data = await state.get_data()
    field = user_data.get("field")

    if field != "имя":
        await message.answer("Ошибка: ожидалось обновление имени.")
        await state.clear()
        return

    new_name = message.text
    user_id = message.from_user.id  # Это telegram_id
    crud_user = CRUDUser()

    logging.info(f"Updating name for user {user_id} to {new_name}")
    await crud_user.update(session, user_id, first_name=new_name)

    await message.answer(f"Имя успешно обновлено на {new_name}!", reply_markup=main_menu_keyboard())
    await state.clear()
    await state.set_state(Main_menu.waiting_for_field)

# Обработчик для обновления возраста
@router.message(UpdateUserStates.waiting_for_new_age)
async def process_new_age(message: types.Message, state: FSMContext, session: AsyncSession):
    user_data = await state.get_data()
    field = user_data.get("field")

    if field != "возраст":
        await message.answer("Ошибка: ожидалось обновление возраста.")
        await state.clear()
        return

    try:
        new_age = int(message.text)
        if new_age < 0 or new_age > 120:
            await message.answer("Пожалуйста, введите корректный возраст (от 0 до 120).")
            return

        user_id = message.from_user.id  # Это telegram_id
        crud_user = CRUDUser()

        logging.info(f"Updating age for user {user_id} to {new_age}")
        await crud_user.update(session, user_id, age=new_age)

        await message.answer(f"Возраст успешно обновлен на {new_age}!", reply_markup=main_menu_keyboard())
        await state.clear()
        await state.set_state(Main_menu.waiting_for_field)
    except ValueError:
        await message.answer("Пожалуйста, введите число.")

# Обработчик для обновления пола
@router.message(UpdateUserStates.waiting_for_new_sex)
async def process_new_sex(message: types.Message, state: FSMContext, session: AsyncSession):
    user_data = await state.get_data()
    field = user_data.get("field")

    if field != "пол":
        await message.answer("Ошибка: ожидалось обновление пола.")
        await state.clear()
        return

    new_sex = message.text.lower()
    if new_sex not in ["мужской", "женский"]:
        await message.answer("Пожалуйста, выберите 'мужской' или 'женский'.", reply_markup=sex_choose_kb())
        return

    user_id = message.from_user.id  # Это telegram_id
    crud_user = CRUDUser()

    logging.info(f"Updating sex for user {user_id} to {new_sex}")
    await crud_user.update(session, user_id, sex=new_sex)

    await message.answer(f"Пол успешно обновлен на {new_sex}!", reply_markup=main_menu_keyboard())
    await state.clear()
    await state.set_state(Main_menu.waiting_for_field)


class Main_menu(StatesGroup):
    waiting_for_profile = State()
    waiting_for_update_profile = State()
    waiting_for_find_movie = State()
    waiting_for_field = State()

@router.message(Main_menu.waiting_for_field)
async def process_field_choice(message: types.Message, state: FSMContext, session: AsyncSession):
    field = message.text.lower()
    user_id = message.from_user.id
    crud_user = CRUDUser()
    
    if field in ["профиль", "изменить профиль", "найти фильм"]:
        await state.update_data(field=field)
        user = await crud_user.get_username_by_telegram_id(session, user_id)
        user_age = await crud_user.get_age_by_telegram_id(session, user_id)
        user_sex = await crud_user.get_sex_by_telegram_id(session, user_id)
        if field == "профиль":
            await message.answer(f"Ваше имя: {user}\n"
                                 f"Ваш возраст: {user_age}\n"
                                 f"Ваш пол: {user_sex}")
            await state.update_data(field=field)
            return
        elif field == "изменить профиль":
            await cmd_update_profile(message, state)
        elif field == "найти фильм":
            # Здесь будет логика для поиска фильма
            pass
    else:
        await message.answer("Пожалуйста, выберите один из доступных вариантов.")
                