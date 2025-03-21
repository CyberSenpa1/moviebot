from aiogram.dispatcher.router import Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram import F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from src.database.models import User
from init_db import engine

from src.keyboards.simple_row import make_row_keyboard

from sqlalchemy.orm import Session


router = Router()

class RegistrationStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_sex = State()

# Доступные варианты пола
available_sex_options = ["мужской", "женский"]

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await message.answer("Привет! Давай зарегистрируемся. Как тебя зовут?",
                         reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(RegistrationStates.waiting_for_name)
    

@router.message(StateFilter(RegistrationStates.waiting_for_name))
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Отлично! Сколько тебе лет?",
                         reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(RegistrationStates.waiting_for_age)

@router.message(StateFilter(RegistrationStates.waiting_for_age))
async def process_age(message: Message, state: FSMContext):
    try:
        age = int(message.text)
        if age < 0 or age > 120:
            await message.answer("Пожалуйста, введите корректный возраст")
            return
        await state.update_data(age=age)
        await message.answer(
            text="Отлично! Укажи свой пол:",
            reply_markup=make_row_keyboard(available_sex_options)
        )
        await state.set_state(RegistrationStates.waiting_for_sex)
    except ValueError:
        await message.answer("Пожалуйста, введите число")

@router.message(StateFilter(RegistrationStates.waiting_for_sex), F.text.in_(available_sex_options))
async def process_sex(message: Message, state: FSMContext):
    sex = message.text.lower()

    # Получаем все данные из состояния
    user_data = await state.get_data()
    name = user_data['name']
    age = user_data['age']

    with Session(engine) as session:
        new_user = User(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=name,
            age=age,
            sex=sex
        )
        session.add(new_user)
        session.commit()

        await message.answer(
            text=f"Спасибо, {name}! Вы успешно зарегистрированы",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.clear()

@router.message(StateFilter(RegistrationStates.waiting_for_sex))
async def process_sex_incorrectly(message: Message):
    await message.answer(
        text="Пожалуйста, выберите один из вариантов из списка ниже:",
        reply_markup=make_row_keyboard(available_sex_options)
    )
# try:
#     with Session(engine) as session:
#         # Создаем нового пользователя
#         new_user = crud_user.create(
#             db=session,
#             telegram_id=123456789,
#             username="john_doe",
#             first_name="John",
#             last_name="Doe"
#         )
#         print(f"Создан пользователь: {new_user.username}")

# except Exception as e:
#     print(e)