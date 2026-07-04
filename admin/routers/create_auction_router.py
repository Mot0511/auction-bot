import asyncio

from maxapi import Router, F
from maxapi.context import MemoryContext, StatesGroup, State
from maxapi.enums import ParseMode
from maxapi.types import MessageCallback, MessageCreated
from admin.keyboards import confirm_auction_kb, back_main_admin
from admin.utils.make_confirm_auction_message import make_confirm_auction_message
from db import DBService
from models.auction import Auction
from datetime import datetime

from timer import Timer


class AuctionState(StatesGroup):
    title = State()
    body = State()
    step = State()
    duration = State()
    countdown = State()

create_auction_router = Router()

@create_auction_router.message_callback(F.callback.payload == 'create-auction')
async def get_title(event: MessageCallback, context: MemoryContext):
    await event.message.answer(text='Введите тему аукциона')
    await context.set_state(AuctionState.title)

@create_auction_router.message_created(AuctionState.title)
async def get_body(event: MessageCreated, context: MemoryContext):
    await context.update_data(title=event.message.body.text)
    await event.message.answer(text='Введите описание аукциона')
    await context.set_state(AuctionState.body)

@create_auction_router.message_created(AuctionState.body)
async def get_step(event: MessageCreated, context: MemoryContext):
    await context.update_data(body=event.message.body.text)
    await event.message.answer(text='Укажите шаг ставки (в руб.)')
    await context.set_state(AuctionState.step)

@create_auction_router.message_created(AuctionState.step)
async def get_step(event: MessageCreated, context: MemoryContext):
    await context.update_data(step=event.message.body.text)
    await event.message.answer(text='Укажите время таймера до начала аукциона (в мин.)')
    await context.set_state(AuctionState.countdown)

@create_auction_router.message_created(AuctionState.countdown)
async def get_step(event: MessageCreated, context: MemoryContext):
    await context.update_data(countdown=event.message.body.text)
    await event.message.answer(text='Укажите минимальную продолжительность аукциона (в мин.)')
    await context.set_state(AuctionState.duration)

@create_auction_router.message_created(AuctionState.duration)
async def get_step(event: MessageCreated, context: MemoryContext):
    await context.set_state(None)
    await context.update_data(duration=event.message.body.text)
    data = await context.get_data()
    await event.message.answer(text='Все верно?\n'+make_confirm_auction_message(data), attachments=[confirm_auction_kb.as_markup()], parse_mode=ParseMode.HTML)

@create_auction_router.message_callback(F.callback.payload == 'confirm-auction')
async def confirm_auction(event: MessageCallback, context: MemoryContext, db: DBService, timer: Timer):
    data = await context.get_data()
    auction_id = await db.create_auction(data)
    auction = Auction(
        id=auction_id,
        title=data['title'],
        body=data['body'],
        price=0,
        step=data['step'],
        media='',
        state=0,
        date=int(datetime.now().timestamp()),
        countdown=int(data['countdown']),
        duration=int(data['duration']),
    )
    await db.join_auction(event.message.recipient.chat_id, '', '', auction_id)
    asyncio.create_task(timer.start_timer(auction))
    await event.answer(new_text=f'Аукцион создан. Минут до запуска: {data['countdown']}', attachments=[back_main_admin.as_markup()])
