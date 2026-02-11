from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable
from storage import sponsors, users
from sponsor import check_subscription
from keyboards import sponsor_check_kb

class SubscriptionCheckMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        if isinstance(event, Message):
            if event.text in ["/admin", "/cancel", "/start"]:
                return await handler(event, data)
        
        if sponsors:
            user_id = event.from_user.id
            
            is_subscribed = await check_subscription(event.bot, user_id)
            
            if not is_subscribed:
                if user_id in users:
                    users[user_id]["confirmed"] = False
                
                if isinstance(event, Message):
                    await event.answer(
                        "❗️ Для доступа к функциям бота необходимо подписаться на канал!\n\n"
                        "Нажмите на кнопку ниже, чтобы перейти и подписаться:",
                        reply_markup=sponsor_check_kb()
                    )
                    return
                    
                elif isinstance(event, CallbackQuery):
                    await event.answer(
                        "❌ Необходимо подписаться на канал!",
                        show_alert=True
                    )
                    return
            else:
                if user_id in users:
                    users[user_id]["confirmed"] = True
        
        return await handler(event, data)