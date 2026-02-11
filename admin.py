from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from api_token import ADMIN_IDS
from keyboards import admin_menu, user_menu, sponsor_list_kb
from states import AdminState
from storage import sponsors, users, results, save_sponsors

admin_router = Router()

# Фильтр для админов
def is_admin(message: Message) -> bool:
    return message.from_user.id in ADMIN_IDS

@admin_router.message(F.text == "/admin")
async def admin_panel(message: Message):
    if is_admin(message):
        await message.answer(
            "🔐 Административная панель\n\n"
            "Выберите действие:",
            reply_markup=admin_menu()
        )
    else:
        await message.answer("❌ У вас нет прав администратора.")

@admin_router.message(F.text == "⚙️ Добавить спонсора")
async def add_sponsor(message: Message, state: FSMContext):
    if not is_admin(message):
        return
        
    await state.set_state(AdminState.adding_sponsor)
    await message.answer(
        "📢 Введите @username канала или ссылку на канал:\n"
        "Примеры: @channel_name или https://t.me/channel_name\n\n"
        "Для отмены введите /cancel"
    )

@admin_router.message(AdminState.adding_sponsor)
async def save_sponsor(message: Message, state: FSMContext):
    if not is_admin(message):
        return
        
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ Добавление отменено", reply_markup=admin_menu())
        return
        
    sponsor = message.text.strip()
    
    # Очищаем и форматируем username
    if sponsor.startswith("https://t.me/"):
        sponsor = "@" + sponsor.replace("https://t.me/", "")
    elif not sponsor.startswith("@"):
        sponsor = "@" + sponsor
    
    # Добавляем спонсора (set не допустит дубликатов)
    old_count = len(sponsors)
    sponsors.add(sponsor)
    
    # Сохраняем в файл
    save_sponsors()
    
    await state.clear()
    
    if len(sponsors) > old_count:
        await message.answer(
            f"✅ Спонсор {sponsor} успешно добавлен!\n"
            f"📊 Всего спонсоров: {len(sponsors)}",
            reply_markup=admin_menu()
        )
    else:
        await message.answer(
            f"ℹ️ Спонсор {sponsor} уже существует в списке!\n"
            f"📊 Всего спонсоров: {len(sponsors)}",
            reply_markup=admin_menu()
        )

@admin_router.message(F.text == "🗑 Удалить спонсора")
async def delete_sponsor(message: Message):
    if not is_admin(message):
        return
        
    if not sponsors:
        await message.answer("📭 Список спонсоров пуст.", reply_markup=admin_menu())
        return
    
    await message.answer(
        "Выберите спонсора для удаления:",
        reply_markup=sponsor_list_kb()
    )

@admin_router.callback_query(F.data.startswith("del_sponsor_"))
async def confirm_delete_sponsor(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Нет прав", show_alert=True)
        return
        
    sponsor = callback.data.replace("del_sponsor_", "")
    
    if sponsor in sponsors:
        sponsors.remove(sponsor)
        # Сохраняем изменения в файл
        save_sponsors()
        await callback.message.edit_text(
            f"✅ Спонсор {sponsor} удален!\n"
            f"📊 Осталось спонсоров: {len(sponsors)}"
        )
    else:
        await callback.message.edit_text("❌ Спонсор не найден")
    
    await callback.answer()

@admin_router.callback_query(F.data == "back_to_admin")
async def back_to_admin(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Нет прав", show_alert=True)
        return
        
    await callback.message.delete()
    await callback.message.answer(
        "🔐 Административная панель",
        reply_markup=admin_menu()
    )
    await callback.answer()

@admin_router.message(F.text == "📋 Список спонсоров")
async def list_sponsors(message: Message):
    if not is_admin(message):
        return
        
    if not sponsors:
        await message.answer("📭 Список спонсоров пуст.", reply_markup=admin_menu())
        return
    
    text = "📢 <b>Список спонсоров:</b>\n\n"
    for i, sponsor in enumerate(sorted(sponsors), 1):
        text += f"{i}. {sponsor}\n"
    
    text += f"\n📊 Всего: {len(sponsors)}"
    
    await message.answer(text, parse_mode="HTML", reply_markup=admin_menu())

@admin_router.message(F.text == "📊 Статистика")
async def stats(message: Message):
    if not is_admin(message):
        return
        
    total_users = len(users)
    confirmed_users = sum(1 for u in users.values() if u.get("confirmed", False))
    total_tests = len(results)
    
    # Средний балл
    avg_score = 0
    if results:
        avg_score = sum(r.get("score", 0) for r in results) / len(results)
    
    await message.answer(
        f"📊 <b>СТАТИСТИКА БОТА</b>\n\n"
        f"👥 <b>Пользователи:</b>\n"
        f"├ Всего: {total_users}\n"
        f"└ Подтверждено: {confirmed_users}\n\n"
        f"📝 <b>Тесты:</b>\n"
        f"├ Всего пройдено: {total_tests}\n"
        f"└ Средний балл: {avg_score:.1f}/5\n\n"
        f"📢 <b>Спонсоры:</b>\n"
        f"└ Количество: {len(sponsors)}",
        parse_mode="HTML",
        reply_markup=admin_menu()
    )

@admin_router.message(F.text == "🚪 Выйти")
async def exit_admin(message: Message):
    if not is_admin(message):
        return
        
    await message.answer(
        "👋 Вы вышли из административной панели.",
        reply_markup=user_menu()
    )

# Обработчик отмены для всех состояний
@admin_router.message(F.text == "/cancel")
async def cancel_handler(message: Message, state: FSMContext):
    if not is_admin(message):
        return
        
    current_state = await state.get_state()
    if current_state is None:
        return
    
    await state.clear()
    await message.answer("❌ Действие отменено.", reply_markup=admin_menu())