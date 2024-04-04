import asyncio
from telegram import Bot
from userInfo import bot_token, group_chat_id

async def send_group_message(message):
    MAX_TRIES = 5
    retried = 0

    while retried <= MAX_TRIES:
        try:
            bot = Bot(token=bot_token)
            await bot.send_message(chat_id=group_chat_id, text=message)
            print("Telegram Mesajı Gönderildi.")
            break
        except Exception as e:
            retried += 1
            print(f"Telegram Mesaj Gönderimi Başarılı olunamadı. Deneme sayısı: {str(retried)}")
            print("Hata:", str(e))
        await asyncio.sleep(0)