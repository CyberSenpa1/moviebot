from aiogram import Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.crud import CRUDUser
from src.database.models import User

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
        await message.answer("Вы уже зарегистрированы!")
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