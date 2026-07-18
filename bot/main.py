import asyncio
import os
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / '.env')

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
WEBAPP_URL = os.getenv('WEBAPP_URL', 'https://admin.ansortushenka.uz/')
API_URL = os.getenv('REACT_APP_API_URL', 'https://admin.ansortushenka.uz/api')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


async def register_user(user: types.User):
    payload = {
        'telegram_id': user.id,
        'full_name': user.full_name,
        'username': user.username or '',
    }
    try:
        async with aiohttp.ClientSession() as session:
            await session.post(f"{API_URL}/users/register/", json=payload, timeout=10)
    except Exception as e:
        print(f"register_user error: {e}")


@dp.message(CommandStart())
async def start(message: types.Message):
    await register_user(message.from_user)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🛒 Buyurtma berish",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )]
    ])
    await message.answer(
        "🍽 <b>Ansor Tushenka Botiga xush kelibsiz!</b>\n\n"
        "Menyuni ko'rish va buyurtma berish uchun tugmani bosing 👇",
        reply_markup=keyboard,
        parse_mode="HTML"
    )


async def main():
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
