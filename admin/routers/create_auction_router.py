import asyncio

from maxapi import Router, F
from maxapi.context import MemoryContext, StatesGroup, State
from maxapi.enums import ParseMode
from maxapi.types import MessageCallback, MessageCreated, ButtonsPayload
from admin.keyboards import *
from admin.utils.make_confirm_auction_message import make_confirm_auction_message
from db import DBService
from filters.digit_filter import DigitFilter
from models.auction import Auction
from datetime import datetime
from models.user import User
from timer import Timer
from utils.get_str_time import get_str_time


class AuctionState(StatesGroup):
    title = State()
    body = State()
    media = State()
    step = State()
    duration = State()
    countdown = State()
    price = State()

create_auction_router = Router()

@create_auction_router.message_callback(F.callback.payload == 'create-auction')
async def get_title(event: MessageCallback, context: MemoryContext):
    await event.message.answer(text='Введите тему аукциона')
    await context.set_state(AuctionState.title)

@create_auction_router.message_callback(F.callback.payload == 'get-desc')
@create_auction_router.message_created(AuctionState.title)
async def get_body(event: MessageCreated, context: MemoryContext):
    await context.update_data(title=event.message.body.text)
    await event.message.answer(text='Введите описание аукциона')
    await context.set_state(AuctionState.body)

@create_auction_router.message_callback(F.callback.payload == 'get-media')
@create_auction_router.message_created(AuctionState.body)
async def get_media(event: MessageCreated, context: MemoryContext):
    await context.update_data(body=event.message.body.text)
    await event.message.answer(text='Можете приложить изображения (не обязательно)', attachments=[ButtonsPayload(buttons=[[skip_media_btn]]).pack()])
    await context.set_state(AuctionState.media)

@create_auction_router.message_callback(F.callback.payload == 'get-price')
@create_auction_router.message_created(AuctionState.media)
async def set_media(event: MessageCreated, context: MemoryContext):
    if event.message.body.attachments:
        tokens = [attachment.payload.token for attachment in event.message.body.attachments]
        await context.update_data(media=tokens)
    else:
        await context.update_data(media=[])
    await event.message.answer(text='Укажите стартовую цену аукциона (в руб.)')
    await context.set_state(AuctionState.price)

@create_auction_router.message_callback(F.callback.payload == 'get-step')
@create_auction_router.message_created(AuctionState.price, DigitFilter())
async def get_step(event: MessageCreated, context: MemoryContext):
    await context.update_data(price=event.message.body.text)
    await event.message.answer(text='Укажите шаг ставки (в руб.)')
    await context.set_state(AuctionState.step)

@create_auction_router.message_callback(F.callback.payload == 'get-countdown')
@create_auction_router.message_created(AuctionState.step, DigitFilter())
async def get_countdown(event: MessageCreated, context: MemoryContext):
    await context.update_data(step=event.message.body.text)
    await event.message.answer(text='Укажите время таймера до начала аукциона (в мин.)')
    await context.set_state(AuctionState.countdown)

@create_auction_router.message_callback(F.callback.payload == 'get-duration')
@create_auction_router.message_created(AuctionState.countdown, DigitFilter())
async def get_duration(event: MessageCreated, context: MemoryContext):
    await context.update_data(countdown=event.message.body.text)
    await event.message.answer(text='Укажите минимальную продолжительность аукциона (в мин.)')
    await context.set_state(AuctionState.duration)

@create_auction_router.message_created(AuctionState.duration, DigitFilter())
async def confirm(event: MessageCreated, context: MemoryContext):
    await context.set_state(None)
    await context.update_data(duration=event.message.body.text)
    data = await context.get_data()
    await event.message.answer(
        text='Все верно?\n'+await make_confirm_auction_message(data),
        attachments=[ButtonsPayload(buttons=[[confirm_auction_btn]]).pack()],
        parse_mode=ParseMode.HTML
    )

@create_auction_router.message_created(F.message.body.text == 'Подтвердить создание аукциона')
async def confirm_auction(event: MessageCreated, context: MemoryContext, db: DBService, timer: Timer):
    data = await context.get_data()
    auction_id = await db.create_auction(data)
    auction = Auction(
        id=auction_id,
        title=data['title'],
        body=data['body'],
        start_price=int(data['price']),
        max_bet=int(data['price']),
        step=int(data['step']),
        media=data['media'],
        state=0,
        date=int(datetime.now().timestamp()),
        countdown=int(data['countdown']),
        duration=int(data['duration']),
    )
    userdata = event.message.sender
    id = await db.join_auction(userdata.user_id, event.message.recipient.chat_id, '', userdata.first_name, auction_id)
    user = User(
        id=id,
        user_id=userdata.user_id,
        chat_id=event.message.recipient.chat_id,
        tel='',
        username=f'{userdata.first_name} (администратор)',
        auction=auction.id,
    )
    await timer.join(user)
    asyncio.create_task(timer.start_timer(auction))
    await event.message.answer(text=f'Аукцион создан. Он начнется через {await get_str_time(auction.countdown * 60)}', attachments=[back_main_admin_kb.as_markup()])
