import asyncio
import os
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
)
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / '.env')

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
WEBAPP_URL = os.getenv('WEBAPP_URL', 'https://admin.ansortushenka.uz/')
API_URL = os.getenv('REACT_APP_API_URL', 'https://admin.ansortushenka.uz/api')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


async def register_user(user: types.User, phone: str | None = None):
    payload = {
        'telegram_id': user.id,
        'full_name': user.full_name,
        'username': user.username or '',
    }
    if phone:
        payload['phone'] = phone
    try:
        async with aiohttp.ClientSession() as session:
            await session.post(f"{API_URL}/users/register/", json=payload, timeout=10)
    except Exception as e:
        print(f"register_user error: {e}")


@dp.message(CommandStart())
async def start(message: types.Message):
    await register_user(message.from_user)

    phone_keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📞 Raqamni yuborish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await message.answer(
        "🍽 <b>Ansor Tushenka Botiga xush kelibsiz!</b>\n\n"
        "Buyurtma berishda tezroq bog'lanish uchun telefon raqamingizni yuboring 👇",
        reply_markup=phone_keyboard,
        parse_mode="HTML"
    )


@dp.message(lambda m: m.contact is not None)
async def contact_handler(message: types.Message):
    if message.contact.user_id != message.from_user.id:
        return

    await register_user(message.from_user, phone=message.contact.phone_number)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🛒 Buyurtma berish",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )]
    ])
    await message.answer(
        "✅ Rahmat! Endi menyuni ko'rish va buyurtma berish uchun tugmani bosing 👇",
        reply_markup=ReplyKeyboardRemove(),
    )
    await message.answer(
        "Buyurtma berish uchun bosing:",
        reply_markup=keyboard,
    )


async def main():
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
