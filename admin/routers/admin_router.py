import os
from maxapi import Router
from maxapi.context import StatesGroup, State, MemoryContext
from maxapi.enums import ParseMode
from maxapi.filters.command import Command
from maxapi.filters import F
from maxapi.types import MessageCreated, MessageCallback, ButtonsPayload
from admin.keyboards import *
from admin.utils.get_media_attachments import get_media_attachments
from admin.utils.make_auction_message import make_auction_message
from admin.utils.make_participants_message import make_participants_message
from db import DBService
from timer import Timer
from user.keyboards import get_history_btn
from utils.broadcast import broadcast


class AdminForm(StatesGroup):
    code = State()
    new_step = State()

admin_router = Router()

@admin_router.message_created(Command("admin"))
async def admin(event: MessageCreated, context: MemoryContext, db: DBService, timer: Timer):
    await context.set_state(None)
    timer.admin_id = event.message.recipient.chat_id
    admin_data = await context.get_data()
    if admin_data.get('code') == os.getenv('ADMIN_CODE'):
        await send_last_auction(event, context, db)
    else:
        await context.set_state(AdminForm.code)
        await event.message.answer(
            text="Введите код доступа к админ панели"
        )

@admin_router.message_callback(F.callback.payload == 'admin')
async def admin(event: MessageCallback, context: MemoryContext, db: DBService):
    await context.set_state(None)
    await send_last_auction(event, context, db)

@admin_router.message_created(AdminForm.code)
async def get_admin_code(event: MessageCreated, context: MemoryContext, db: DBService):
    await context.set_state(None)
    code = event.message.body.text
    if code == os.getenv('ADMIN_CODE'):
        await context.update_data(code=code)
        await send_last_auction(event, context, db)
    else:
        await event.message.answer(
            text="Неверный код доступа к админ панели."
        )
    await context.set_state(None)

@admin_router.message_callback(F.callback.payload == 'stop-auction')
async def stop_auction(event: MessageCallback, context: MemoryContext, db: DBService, timer: Timer):
    auction = await db.get_last_auction()
    if timer.stage != -1:
        await broadcast(event, f'Аукцион #{auction.id}: "{auction.title}" остановлен досрочно.', auction.id, db)

    await timer.stop_timer()
    await db.stop_auction(auction.id)
    await send_last_auction(event, context, db)

async def send_last_auction(event, context: MemoryContext, db: DBService):
    await context.update_data(auctions_history_start=None)
    auction = await db.get_last_auction()
    btns = []
    if auction:
        await context.update_data(last_auction_id=auction.id)
        btns += [[create_auction_btn if auction.state == -1 else stop_auction_btn], [get_participants_btn, get_history_btn]]
        if auction.state != -1: btns.insert(1, [change_step_btn])
        attachments = [ButtonsPayload(buttons=btns).pack()]
        if auction.media: attachments += await get_media_attachments(auction.media)
        if isinstance(event, MessageCallback):
            await event.answer(
                new_text=await make_auction_message(auction),
                format=ParseMode.HTML,
                attachments=attachments
            )
        else:
            await event.message.answer(
                text=await make_auction_message(auction),
                format=ParseMode.HTML,
                attachments=attachments
            )
    else:
        btns.append([create_auction_btn])
        await event.message.answer(text='До настоящего момента никакие аукционы не проводились',
                           attachments=[ButtonsPayload(buttons=btns).pack()])

@admin_router.message_callback(F.callback.payload == 'change-step')
async def change_step(event, context):
    await event.message.answer(text='Укажите новый шаг ставки')
    await context.set_state(AdminForm.new_step)

@admin_router.message_created(AdminForm.new_step)
async def set_new_step(event, context, timer, db):
    await context.set_state(None)
    step = int(event.message.body.text)
    timer.current_auction.step = step
    await broadcast(
        event,
        f'Новый шаг ставки - {step} руб.',
        timer.current_auction.id,
        db
    )
    await db.set_step(step, timer.current_auction.id)
