from aiogram.filters import Command, Filter
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter


from src.keyboards.keyboards import admin_panel, cancel_kb, confirm_kb

from config import admins

from src.database.models import User
from sqlalchemy import select
import asyncio
from init_db import async_session_maker


admin_router = Router()

# Лучше хранить админов в базе данных или конфиге
ADMINS_IDS = admins

class IsAdminFilter(Filter):
    async def __call__(self, message: Message) -> bool:
        # Разрешаем команду /admin независимо от состояния
        if isinstance(message, Message) and message.text and message.text.startswith('/admin'):
            return message.from_user.id in ADMINS_IDS
        return message.from_user.id in ADMINS_IDS

    

# Регистрация фильтра    
admin_router.message.filter(IsAdminFilter())
admin_router.callback_query.filter(IsAdminFilter())


@admin_router.message(Command("admin"))
async def handle_admin_command_anywhere(message: Message, state: FSMContext):
    """Обработчик /admin из любого состояния"""
    # Сбрасываем текущее состояние (если нужно)
    await state.clear()
    
    if message.from_user.id not in ADMINS_IDS:
        pass
    
    await message.answer(
        "👨‍💻 Админ-панель:",
        reply_markup=admin_panel()
    )


@admin_router.callback_query(F.data == "admin_back")
async def go_back(callback: CallbackQuery):
    """Возвращение в админ-панель"""
    await callback.message.edit_text(
        "👨‍💻 Админ-панель:",
        reply_markup=admin_panel()  # Используем клавиатуру админ-панели
    )
    await callback.answer()


@admin_router.callback_query(F.data == "admin_stats")
async def show_statistics(callback: CallbackQuery):
    """Показ статистики бота"""
    async with async_session_maker() as session:
        result = await session.stream(select(User.telegram_id))
        user_ids = [user.telegram_id async for user in result]
        total_users = len(user_ids)
        # Здесь можно получить реальную статистику из БД
        stats_text = (
            f"📊 Статистика бота:\n\n"
            f"👥 Всего пользователей: {total_users}\n"
            f"🟢 Активных за месяц: 256\n"
            f"🔴 Новых сегодня: 12\n"
            f"📝 Сообщений сегодня: 345"
        )
        
        back_button = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back")]
        ])
        
        await callback.message.edit_text(stats_text, reply_markup=back_button)

class MailingStates(StatesGroup):
    WAITING_TEXT = State()
    WAITING_CONFIRM = State()

@admin_router.callback_query(F.data == "admin_mailing")
async def mailing(callback: CallbackQuery, state: FSMContext):
    """Рассылка сообщений"""
    await callback.message.edit_text(
        "Введите текст",
        reply_markup=cancel_kb()
    )
    await state.set_state(MailingStates.WAITING_TEXT)
    await callback.answer()

@admin_router.message(MailingStates.WAITING_TEXT)
async def process_mailing_text(message: Message, state: FSMContext):
    """Обработка текста рассылки и подтверждение"""
    await state.update_data(mailing_text=message.html_text)

    await message.answer(
        f"Подтвердите рассылку:\n\n{message.html_text}\n\n"
        "Будет отправлено всем пользователям бота.",
        reply_markup=confirm_kb(),
        parse_mode="HTML"
    )
    await state.set_state(MailingStates.WAITING_CONFIRM)

async def send_message_with_retry(bot: Bot, chat_id: int, text: str, parse_mode: str = "HTML"):
    """Отправка сообщения с повторной попыткой при ошибках"""
    try:
        await bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode)
        return True
    except TelegramRetryAfter as e:
        await asyncio.sleep(e.retry_after)
        return await send_message_with_retry(bot, chat_id, text, parse_mode)
    except TelegramForbiddenError:
        return False
    except Exception as e:
        print(f"Ошибка при отправке: {e}")
        return False
    

@admin_router.callback_query(F.data == "confirm_mailing", MailingStates.WAITING_CONFIRM)
async def execute_mailing(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Выполнение рассылки"""
    data = await state.get_data()
    mailing_text = data['mailing_text']
    admin_id = callback.from_user.id
    
    progress_msg = await callback.message.edit_text("⏳ Подготовка к рассылке...")
    await callback.answer()
    
    # Используем асинхронную сессию
    async with async_session_maker() as session:
        # Получаем только необходимые данные (telegram_id)
        result = await session.execute(select(User.telegram_id))
        user_ids = [uid for uid in result.scalars().all() if uid != admin_id]
        total_users = len(user_ids)
        
        success = 0
        failed = 0
        batch_size = 50  # Размер батча для обновления прогресса
        
        for i, user_id in enumerate(user_ids, 1):
            try:
                await bot.send_message(
                    chat_id=user_id,
                    text=mailing_text,
                    parse_mode="HTML"
                )
                success += 1
            except TelegramForbiddenError:
                # Пользователь заблокировал бота
                failed += 1
            except TelegramRetryAfter as e:
                # Превышены лимиты - делаем паузу
                await asyncio.sleep(e.retry_after)
                try:
                    await bot.send_message(
                        chat_id=user_id,
                        text=mailing_text,
                        parse_mode="HTML"
                    )
                    success += 1
                except Exception:
                    failed += 1
            except Exception as e:
                print(f"Ошибка при отправке пользователю {user_id}: {str(e)}")
                failed += 1
            
            # Обновляем прогресс
            if i % batch_size == 0 or i == total_users:
                progress = min(i / total_users * 100, 100)
                await progress_msg.edit_text(
                    f"⏳ Рассылка в процессе...\n\n"
                    f"▰{'▰' * int(progress // 10)}{'▱' * (10 - int(progress // 10))}\n"
                    f"📊 {i}/{total_users} ({progress:.1f}%)\n"
                    f"✅ {success} | ❌ {failed}"
                )
            
            # Оптимальная задержка между сообщениями
            await asyncio.sleep(0.03)
    
    # Формируем финальный отчет
    report = (
        f"📊 <b>Отчет о рассылке</b>\n\n"
        f"▪️ Всего пользователей: {total_users}\n"
        f"✅ Успешно отправлено: {success}\n"
        f"❌ Не удалось отправить: {failed}\n\n"
        f"<i>Последняя рассылка завершена</i>"
    )
    
    await progress_msg.edit_text(
        report,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 В админ-панель", callback_data="admin_back")]
        ]),
        parse_mode="HTML"
    )
    await state.clear()