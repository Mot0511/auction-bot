import asyncio
import os
import sqlite3

from dotenv import load_dotenv
from maxapi import Bot, Dispatcher
from maxapi.context import MemoryContext
from maxapi.enums import ParseMode
from maxapi.types import BotStarted, Command, MessageCreated, MessageCallback, ButtonsPayload, RequestContactButton
from maxapi.filters import F, ContactFilter
from admin.routers.admin_router import admin_router
from admin.routers.create_auction_router import create_auction_router
from admin.utils.make_auction_message import make_auction_message
from db import DBService
from middlewares.TimerMiddleware import TimerMiddleware
from middlewares.DatabaseMiddleware import DatabaseMiddleware
from timer import Timer
from user.router import user_router, send_last_auction
from user.keyboards import *
from admin.keyboards import get_participants_btn
from admin.utils import get_media_attachments
from maxapi.types.attachments.contact import Contact

load_dotenv()
bot = Bot(token=os.getenv("TOKEN"))

dp = Dispatcher()

conn = sqlite3.connect('db.db')
db = DBService(conn, conn.cursor())
dp.register_inner_middleware(DatabaseMiddleware(db))

timer = Timer(db)
dp.register_inner_middleware(TimerMiddleware(timer))

@dp.bot_started()
async def start(event: BotStarted, db: DBService, context: MemoryContext):
    await event.bot.send_message(
        chat_id=event.chat_id,
        text="Добро пожаловать в бот автомобильных аукционов!",
    )
    await send_last_auction(event, context, db)

@dp.message_created(Command("start"))
async def start(event: MessageCreated, context: MemoryContext, db: DBService):
    await send_last_auction(event, context, db)

dp.include_routers(admin_router)
dp.include_routers(create_auction_router)
dp.include_routers(user_router)

async def main():
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())