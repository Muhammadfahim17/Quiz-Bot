from aiogram import Bot
from storage import sponsors

async def check_subscription(bot: Bot, user_id: int) -> bool:
    """
    Проверка подписки на всех спонсоров
    """
    if not sponsors:
        return True

    # Убираем логирование полностью, только проверка
    for sponsor in sponsors:
        try:
            username = sponsor.replace("@", "").replace("https://t.me/", "")
            chat_id = f"@{username}"
            
            try:
                # Проверяем статус пользователя
                member = await bot.get_chat_member(chat_id, user_id)
                status = member.status
                
                if status in ("left", "kicked", "banned"):
                    return False
                    
            except Exception:
                # Если ошибка - считаем что не подписан
                return False
                
        except Exception:
            return False
    
    return True