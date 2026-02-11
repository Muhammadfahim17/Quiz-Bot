from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from storage import sponsors

def user_menu():
    """Главное меню пользователя"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 Начать тест")],
            [KeyboardButton(text="🏆 Топ 10")],
            [KeyboardButton(text="ℹ️ О боте")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие..."
    )

def language_menu():
    """Меню выбора языка"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Python")],
            [KeyboardButton(text="JavaScript")],
            [KeyboardButton(text="HTML/CSS")],
            [KeyboardButton(text="⬅️ Назад")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите язык..."
    )

def admin_menu():
    """Меню администратора"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⚙️ Добавить спонсора")],
            [KeyboardButton(text="🗑 Удалить спонсора")],
            [KeyboardButton(text="📋 Список спонсоров")],
            [KeyboardButton(text="📊 Статистика")],
            [KeyboardButton(text="🚪 Выйти")]
        ],
        resize_keyboard=True
    )

def sponsor_check_kb():
    """Клавиатура для проверки подписки"""
    keyboard = []
    
    # Добавляем кнопки спонсоров
    for sponsor in sorted(sponsors):
        username = sponsor.replace("@", "").replace("https://t.me/", "")
        if not username.startswith("@"):
            username = f"@{username}"
            
        keyboard.append([
            InlineKeyboardButton(
                text=f"📢 {sponsor}",
                url=f"https://t.me/{username.replace('@', '')}"
            )
        ])
    
    # Добавляем кнопку проверки
    keyboard.append([
        InlineKeyboardButton(
            text="🔄 Проверить подписку",
            callback_data="check_sub"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def quiz_inline_kb(options):
    """Инлайн-клавиатура для вопросов теста"""
    keyboard = []
    
    for index, option in enumerate(options):
        keyboard.append([
            InlineKeyboardButton(
                text=f"{chr(65 + index)}. {option}",  
                callback_data=f"answer_{index}"
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton(
            text="❌ Прервать тест",
            callback_data="cancel_test"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def sponsor_list_kb():
    """Клавиатура со списком спонсоров для удаления"""
    keyboard = []
    
    for sponsor in sorted(sponsors):
        keyboard.append([
            InlineKeyboardButton(
                text=f"❌ {sponsor}",
                callback_data=f"del_sponsor_{sponsor}"
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton(
            text="🔙 Назад",
            callback_data="back_to_admin"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)