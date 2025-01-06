import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InputFile
from aiogram.filters import CommandStart
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# --- Конфігурація ---
TOKEN = '7221891102:AAGog7UYTggf8-eQxYWYUfEB0GNKhbWKZ3Q'
SPREADSHEET_URL = 'https://docs.google.com/spreadsheets/d/1h9fonsw1wBFi7dDnT-0fod8BTxakW8f6tF56Au2ujEc/edit?usp=sharing'
DRIVE_FOLDER_URL = 'https://drive.google.com/drive/folders/1VcyrHUebwuHGI6_wDwWCIbKcjVTd4XNt?usp=sharing'
SCHEDULE_URL = 'https://docs.google.com/spreadsheets/d/1KuLSlD6ctB-B5960jKBzkpZGyGqd7jgo/edit?usp=sharing'

# --- Google API ---
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
CREDENTIALS_FILE = r'set/credentials.json'

creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
gs_client = gspread.authorize(creds)
sheet = gs_client.open_by_url(SPREADSHEET_URL).sheet1

# --- Ініціалізація бота ---
bot = Bot("7221891102:AAGog7UYTggf8-eQxYWYUfEB0GNKhbWKZ3Q")
dp = Dispatcher()

# --- Клавіатура ---
main_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='📦 Поставка')],
    [KeyboardButton(text='💵 Прибуток/витрати')],
    [KeyboardButton(text='📅 Графік')]
], resize_keyboard=True)

finance_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='💵 Інкасація готівки')],
    [KeyboardButton(text='💸 Витрати готівки')],
    [KeyboardButton(text='🧾 Z-звіт термінал')],
    [KeyboardButton(text='⬅️ Назад')]
], resize_keyboard=True)

# --- Обробники ---
@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("👋 Ласкаво просимо до DruidBot! Виберіть дію:", reply_markup=main_menu)

# --- Поставка ---
@dp.message(lambda message: message.text == '📦 Поставка')
async def handle_supply(message: types.Message):
    await message.answer("📸 Відправте фото накладної, і я збережу його у папці Druid НАКЛАДНІ.")

@dp.message(lambda message: message.photo)
async def save_invoice_photo(message: types.Message):
    photo = message.photo[-1]
    file_id = photo.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    destination = f"C:/Users/Lenovo/druidbot/invoices/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.jpg"
    await bot.download_file(file_path, destination)
    await message.answer("✅ Фото накладної збережено.")

# --- Прибуток/витрати ---
@dp.message(lambda message: message.text == '💵 Прибуток/витрати')
async def finance_menu_handler(message: types.Message):
    await message.answer("💼 Виберіть дію:", reply_markup=finance_menu)

@dp.message(lambda message: message.text in ['💵 Інкасація готівки', '💸 Витрати готівки', '🧾 Z-звіт термінал'])
async def finance_report(message: types.Message):
    report_type = message.text
    await message.answer(f"📝 Введіть суму для: {report_type}")

    @dp.message(lambda message: message.text.isdigit())
    async def save_finance(message: types.Message):
        amount = message.text
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sheet.append_row([now, report_type, amount])
        await message.answer(f"✅ {report_type} на суму {amount} грн збережено.", reply_markup=main_menu)

# --- Графік ---
@dp.message(lambda message: message.text == '📅 Графік')
async def show_schedule(message: types.Message):
    await message.answer(f"🗓️ Ваш графік доступний тут: {SCHEDULE_URL}")

# --- Запуск бота ---
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
