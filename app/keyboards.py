from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

async def get_inline_main(bot: Bot):
    bot_username = (await bot.get_me()).username
    link = f"https://t.me/{bot_username}?startgroup=add"
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Помощь", callback_data="help")],
        [InlineKeyboardButton(text="Авторы", callback_data="authors"), 
         InlineKeyboardButton(text="Контакты", callback_data="contacts")],
        [InlineKeyboardButton(text="Добавить бота в групповой чат", url=link)]
    ])

'''inline_main = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Помощь", callback_data="help")],
        [InlineKeyboardButton(text="Авторы", callback_data="authors"), InlineKeyboardButton(text="Контакты", callback_data="contacts")],
    ])'''

inline_back_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="backButton")]
    ])