import os
import tempfile
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram import types
from aiogram.filters import CommandStart, Command
#from aiohttp_socks import ProxyConnector
from dotenv import load_dotenv
import aiohttp
import aiofiles
from groq import Groq
from app.keyboards import get_inline_main, inline_back_kb

load_dotenv()

dp_router = Router()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY)

#команды
@dp_router.message(CommandStart())
async def cmd_start(message: Message):
    keyboard = await get_inline_main(message.bot)
    await message.answer(f'Здравствуй, {message.from_user.first_name}!\n\nЯ бот, который умеет преобразовывать аудио или голосовые сообщения в текст.\n\nОтправь мне голосовое сообщение или выбери пункт меню:', reply_markup=keyboard)

@dp_router.message(Command("help"))
async def cmd_help(message: Message): 
    await message.answer("Список команд:\n/start - начать\n/help - помощь")
    
#обработчики голосовых сообщений
async def download_voice(file_id: str, bot: Bot) -> str: #скачивание голосового сообщения
    file = await bot.get_file(file_id)
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, f"{file_id}.ogg")

    file_url = f"https://api.telegram.org/file/bot{bot.token}/{file.file_path}"

    #proxy_url = "http://127.0.0.1:10809" 
    #connector = ProxyConnector.from_url(proxy_url)
    
    async with aiohttp.ClientSession() as session: #connector=connector
        async with session.get(file_url) as response:
            if response.status == 200:
                async with aiofiles.open(file_path, "wb") as f:
                    await f.write(await response.read())
            else:
                raise Exception(f"Не удалось скачать файл, статус: {response.status}")

    return file_path

async def transcribe_with_groq(file_path: str) -> str: #распознавание голосового сообщения
    try:
        with open(file_path, "rb") as file:
            transcription = groq_client.audio.transcriptions.create(
                file=(os.path.basename(file_path), file.read()),
                model="whisper-large-v3-turbo",
                language="ru",
                response_format="text",
                prompt="Ты слышишь фоновую музыку или звуки, которые не являются речью. Не выдумывай слова, просто обозначь это как 'музыка' или 'шум'.",
            )
        return transcription
    except Exception as e:
        return f"Ошибка распознавания: {e}"

@dp_router.message(lambda message: message.voice is not None) #обработчик голосовых сообщений
async def handle_voice(message: types.Message, bot: Bot):
    processing_msg = await message.answer("Обрабатываю голосовое сообщение...")
    try:
        file_path = await download_voice(message.voice.file_id, bot)
        text = await transcribe_with_groq(file_path)
        os.remove(file_path)

        if text and not text.startswith("Ошибка"):
            await processing_msg.delete()
            await message.answer(f"Распознанный текст:\n\n{text}", parse_mode="Markdown")
        else:
            await processing_msg.edit_text(text)
    except Exception as e:
        await processing_msg.edit_text(f"Произошла ошибка: {e}")
        
#обработчики аудио сообщений
@dp_router.message(lambda message: message.audio is not None) #обработчик аудио сообщений
async def handle_audio(message: types.Message, bot: Bot):
    processing_msg = await message.answer("Обрабатываю аудио сообщение...")
    try:
        file_path = await download_voice(message.audio.file_id, bot)
        text = await transcribe_with_groq(file_path)
        os.remove(file_path)

        if text and not text.startswith("Ошибка"):
            await processing_msg.delete()
            await message.answer(f"Распознанный текст:\n\n{text}", parse_mode="Markdown")
        else:
            await processing_msg.edit_text(text)
    except Exception as e:
        await processing_msg.edit_text(f"Произошла ошибка: {e}")
        
#callbacks
@dp_router.callback_query(F.data == "help")
async def callback_help(callback: CallbackQuery):
    await callback.message.edit_text("Список команд:\n/start - начать\n/help - помощь", reply_markup=inline_back_kb)
    
@dp_router.callback_query(F.data == "authors")
async def callback_authors(callback: CallbackQuery):
    await callback.message.edit_text("Авторы:\n- Илюшкина Анастасия\n- Коробова Евгения", reply_markup=inline_back_kb)
    
@dp_router.callback_query(F.data == "contacts")
async def callback_contacts(callback: CallbackQuery):    
    await callback.message.edit_text("Контакты:\n- @ailushkina\n- @MyMelody00", reply_markup=inline_back_kb)

@dp_router.callback_query(F.data == "backButton")
async def callback_back(callback: CallbackQuery):
    await callback.message.edit_text("Главное меню:", reply_markup=await get_inline_main(callback.bot))