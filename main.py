import asyncio
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from api_token import BOT_TOKEN, ADMIN_IDS
from storage import users, active_tests, results, sponsors, load_sponsors
from keyboards import *
from states import QuizState
from sponsor import check_subscription
from questions import get_random_questions
from admin import admin_router
from middlewares import SubscriptionCheckMiddleware

bot = Bot(BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())



dp.message.middleware(SubscriptionCheckMiddleware())
dp.callback_query.middleware(SubscriptionCheckMiddleware())

dp.include_router(admin_router)


@dp.message(CommandStart())
async def start(message: Message):
    user_id = message.from_user.id
    
    if user_id not in users:
        users[user_id] = {
            "username": message.from_user.username,
            "full_name": message.from_user.full_name,
            "joined_at": datetime.now(),
            "confirmed": False
        }
    
    if sponsors:
        subscribed = await check_subscription(bot, user_id)
        
        if subscribed:
            users[user_id]["confirmed"] = True
            await message.answer(
                "✅ Подписка подтверждена! Добро пожаловать в Quiz Bot!\n\n"
                "Выберите действие:",
                reply_markup=user_menu()
            )
        else:
            users[user_id]["confirmed"] = False
            await message.answer(
                "👋 Добро пожаловать в Quiz Bot!\n\n"
                "❗️ Для доступа к боту необходимо подписаться на канал:\n\n"
                "👇 Нажмите на кнопку ниже, чтобы перейти и подписаться, "
                "затем нажмите '🔄 Проверить подписку'",
                reply_markup=sponsor_check_kb()
            )
        return
    
    users[user_id]["confirmed"] = True
    await message.answer(
        "Добро пожаловать в Quiz Bot!\n\n"
        "Выберите действие:",
        reply_markup=user_menu()
    )


@dp.callback_query(F.data == "check_sub")
async def check_sub(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    if await check_subscription(callback.bot, user_id):
        users[user_id]["confirmed"] = True
        await callback.message.delete()
        await callback.message.answer(
            "✅ Подписка подтверждена! Теперь вам доступен полный функционал бота.",
            reply_markup=user_menu()
        )
    else:
        await callback.answer(
            "❌ Вы не подписаны на канал! Подпишитесь и нажмите проверку снова.",
            show_alert=True
        )
    
    await callback.answer()


@dp.message(F.text == "📝 Начать тест")
async def choose_language(message: Message, state: FSMContext):
    user_id = message.from_user.id
    
    if sponsors:
        subscribed = await check_subscription(bot, user_id)
        if not subscribed:
            users[user_id]["confirmed"] = False
            await message.answer(
                "❗️ Для прохождения тестов необходимо подписаться на спонсоров!",
                reply_markup=sponsor_check_kb()
            )
            return
        else:
            users[user_id]["confirmed"] = True
    
    await state.set_state(QuizState.choosing_language)
    await message.answer("Выберите язык программирования:", reply_markup=language_menu())


@dp.message(QuizState.choosing_language)
async def start_test(message: Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await state.clear()
        await message.answer("Главное меню", reply_markup=user_menu())
        return

    questions = get_random_questions(message.text)
    if not questions:
        await message.answer(
            "❌ Для этого языка пока нет вопросов. Выберите другой язык.",
            reply_markup=language_menu()
        )
        return

    active_tests[message.from_user.id] = {
        "language": message.text,
        "questions": questions,
        "current": 0,
        "score": 0
    }

    await state.set_state(QuizState.answering)
    await send_question(message.from_user.id, message)


async def send_question(user_id: int, message: Message):
    data = active_tests.get(user_id)
    if not data:
        return

    q = data["questions"][data["current"]]
    total_questions = len(data["questions"])

    text = (
        f"📚 <b>Вопрос {data['current'] + 1}/{total_questions}</b>\n"
        f"💻 Язык: <b>{data['language']}</b>\n"
        f"🎯 Счёт: <b>{data['score']}/{data['current']}</b>\n\n"
        f"{q['question']}"
    )

    await message.answer(
        text,
        reply_markup=quiz_inline_kb(q["options"]),
        parse_mode="HTML"
    )


@dp.callback_query(F.data.startswith("answer_"), QuizState.answering)
async def process_answer(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    data = active_tests.get(user_id)
    
    if not data:
        await callback.answer("❌ Тест уже завершён или прерван", show_alert=True)
        await state.clear()
        return

    current_index = data["current"]
    questions = data["questions"]
    
    if current_index >= len(questions):
        await callback.answer("❌ Ошибка теста", show_alert=True)
        await state.clear()
        return

    q = questions[current_index]
    selected = int(callback.data.split("_")[1])

    is_correct = selected == q["answer"]
    if is_correct:
        data["score"] += 1

    result_text = "✅ Правильно!" if is_correct else f"❌ Неправильно! Правильный ответ: {q['options'][q['answer']]}"
    await callback.message.edit_text(result_text)
    
    data["current"] += 1

    if data["current"] >= len(questions):
        score = data["score"]
        total = len(questions)
        
        results.append({
            "user_id": user_id,
            "score": score,
            "total": total,
            "date": datetime.now()
        })

        week_ago = datetime.now() - timedelta(days=7)
        weekly = [r for r in results if r["date"] >= week_ago]
        weekly.sort(key=lambda x: x["score"], reverse=True)
        
        position = 1
        for i, r in enumerate(weekly, 1):
            if r["user_id"] == user_id:
                position = i
                break

        active_tests.pop(user_id, None)
        await state.clear()

        perfect = "🔥 ПРЕВОСХОДНО! ИДЕАЛЬНЫЙ РЕЗУЛЬТАТ!\n\n" if score == total else ""
        
        text = (
            f"{perfect}"
            f"🎯 <b>Ваш результат:</b> {score}/{total}\n"
            f"📊 <b>Процент:</b> {int(score/total*100)}%\n"
            f"🏆 <b>Место на этой неделе:</b> {position}\n\n"
            f"Хотите попробовать еще раз?"
        )

        await callback.message.answer(text, parse_mode="HTML", reply_markup=user_menu())
    else:
        await asyncio.sleep(1)
        await send_question(user_id, callback.message)

    await callback.answer()


@dp.callback_query(F.data == "cancel_test", QuizState.answering)
async def cancel_test(callback: CallbackQuery, state: FSMContext):
    active_tests.pop(callback.from_user.id, None)
    await state.clear()

    await callback.message.edit_text("❌ Тест прерван.")
    await callback.message.answer("Вы вернулись в главное меню.", reply_markup=user_menu())
    await callback.answer()


@dp.message(F.text == "🏆 Топ 10")
async def top10(message: Message):
    week_ago = datetime.now() - timedelta(days=7)
    weekly = [r for r in results if r["date"] >= week_ago]
    weekly.sort(key=lambda x: (x["score"], x["date"]), reverse=True)

    if not weekly:
        await message.answer(
            "📭 Пока нет результатов за эту неделю.\n"
            "Станьте первым!",
            reply_markup=user_menu()
        )
        return

    text = "🏆 <b>ТОП-10 ЛУЧШИХ РЕЗУЛЬТАТОВ НЕДЕЛИ</b>\n\n"
    
    seen_users = set()
    unique_results = []
    
    for r in weekly:
        if r["user_id"] not in seen_users and len(unique_results) < 10:
            seen_users.add(r["user_id"])
            unique_results.append(r)

    for i, r in enumerate(unique_results, 1):
        user = users.get(r["user_id"], {})
        name = user.get("username") or user.get("full_name") or f"User_{r['user_id']}"
        if user.get("username"):
            name = f"@{name}"
        
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "▫️"
        text += f"{medal} {i}. {name} — {r['score']}/{r.get('total', 5)}\n"

    await message.answer(text, parse_mode="HTML", reply_markup=user_menu())


@dp.message(F.text == "ℹ️ О боте")
async def about(message: Message):
    await message.answer(
        "🤖 <b>Quiz Bot</b>\n\n"
        "Этот бот создан для проверки знаний по программированию.\n\n"
        "<b>Возможности:</b>\n"
        "• Тесты по Python, JavaScript, HTML/CSS\n"
        "• Система рейтинга\n"
        "• Топ-10 лучших результатов за неделю\n"
        "• Sponsor Gate для монетизации\n\n"
        "<b>Команды:</b>\n"
        "/start - Запустить бота\n"
        "/admin - Панель администратора\n\n"
        "Приятного тестирования!",
        parse_mode="HTML",
        reply_markup=user_menu()
    )


async def main():
    print("=" * 50)
    print("QUIZ BOT ЗАПУЩЕН")
    print("=" * 50)
    
    load_sponsors()
    if sponsors:
        print(f"Спонсоров: {len(sponsors)}")
    else:
        print("Спонсоры не добавлены")
    
    try:
        bot_info = await bot.get_me()
        print(f"Bot: @{bot_info.username}")
    except:
        print("Ошибка получения информации о боте")
    
    print(f"Admin ID: {ADMIN_IDS[0]}")
    print("=" * 50)
    print("Бот работает!")
    print("=" * 50)
    
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())