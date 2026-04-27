import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.client.session.aiohttp import AiohttpSession
from dotenv import load_dotenv
from app.handlers import dp_router

#PROXY_URL = "http://127.0.0.1:10809"

#session = AiohttpSession(proxy=PROXY_URL)

async def main():
    load_dotenv()
    bot = Bot(token=os.getenv('TELEGRAM_TOKEN')) #, session=session
    dp = Dispatcher()
    dp.startup.register(startup)
    dp.shutdown.register(shutdown)
    dp.include_routers(dp_router)
    await dp.start_polling(bot)
    
async def startup(dispatcher: Dispatcher):
    print("Бот запущен")

async def shutdown(dispatcher: Dispatcher):
    print("Бот остановлен")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass