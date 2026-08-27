import os
import base64
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message

# ========== ТВОИ ДАННЫЕ ==========
BOT_TOKEN = "8680774947:AAFkHYnaU6EAOnbdbRHVq-GfqBpDNOOUkvM"   # ТОКЕН ОТ @BotFather
OWNER_ID = 2027626847                                         # ТВОЙ ID
# ====================================

# ========== API КЛЮЧИ ==========
CPM1_API_KEY = "AIzaSyBW1ZbMiUeDZHYUO2bY8Bfnf5rRgrQGPTM"
CPM2_API_KEY = "AIzaSyCQDz9rgjgmvmFkvVfmvr2-7fT4tfrzRRQ"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(msg: Message):
    await msg.answer(
        "🔐 <b>ES3 Key Generator Bot</b>\n\n"
        "Используй команду:\n"
        "<code>/key email password filename version</code>\n\n"
        "Пример:\n"
        "<code>/key my@email.com pass123 NnM5Y2Fycy9jYXlxM19XWjE2MTUz 1</code>\n\n"
        "version: 1 (CPM1) или 2 (CPM2) — по умолчанию 1"
    )

@dp.message(Command("key"))
async def gen_key(msg: Message):
    uid = msg.from_user.id
    
    if uid != OWNER_ID:
        await msg.answer("❌ Доступ запрещён.")
        return

    args = msg.text.split()[1:]
    if len(args) < 3:
        await msg.answer("❌ Формат: /key email password filename [version]")
        return

    email, password, filename = args[0], args[1], args[2]
    ver = args[3] if len(args) > 3 else "1"

    await msg.answer("⏳ Авторизация...")

    api_key = CPM2_API_KEY if ver == "2" else CPM1_API_KEY
    url = f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={api_key}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True,
        "clientType": "CLIENT_TYPE_ANDROID",
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload) as resp:
                if resp.status != 200:
                    await msg.answer("❌ Authentication failed.")
                    return
                res = await resp.json()
                local_id = res.get("localId")
                if not local_id:
                    await msg.answer("❌ Failed to get local ID.")
                    return

                account_key = local_id[:3]

                try:
                    n = filename.split(".")[0]
                    pad = len(n) % 4
                    if pad:
                        n += "=" * (4 - pad)
                    decoded = base64.b64decode(n)
                    file_key = decoded[:3].decode("utf-8", errors="replace")
                except Exception:
                    await msg.answer("❌ Invalid filename format.")
                    return

                full_key = f"{file_key}{account_key}"
                await msg.answer(f"✅ <b>ES3 Key:</b> <code>{full_key}</code>")
        except Exception as e:
            await msg.answer(f"❌ Ошибка: {e}")

async def main():
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
