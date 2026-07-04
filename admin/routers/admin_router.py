import os
from maxapi import Router
from maxapi.context import StatesGroup, State, MemoryContext
from maxapi.enums import ParseMode
from maxapi.filters.command import Command
from maxapi.filters import F
from maxapi.types import MessageCreated, MessageCallback

from admin.keyboards import stop_auction_kb, create_auction_kb, back_admin
from admin.utils.make_auction_message import make_auction_message
from db import DBService
from timer import Timer


class AdminForm(StatesGroup):
    code = State()

admin_router = Router()

@admin_router.message_created(Command("admin"))
async def admin(event: MessageCreated, context: MemoryContext, db: DBService):
    await context.set_state(None)
    admin_data = await context.get_data()
    # if admin_data.get('code') == os.getenv('ADMIN_CODE'):
    if True:
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
        await send_last_auction(event, context, db)
    else:
        await event.message.answer(
            text="Неверный код доступа к админ панели."
        )
    await context.set_state(None)

@admin_router.message_callback(F.callback.payload == 'stop-auction')
async def stop_auction(event: MessageCallback, context: MemoryContext, db: DBService, timer: Timer):
    data = await context.get_data()
    auction_id = data['last_auction_id']
    await db.stop_auction(auction_id)
    await timer.stop_timer()
    await send_last_auction(event, context, db)

async def send_last_auction(event, context: MemoryContext, db: DBService):
    auction = await db.get_last_auction()
    if auction:
        await context.update_data(last_auction_id=auction.id)
        if isinstance(event, MessageCallback):
            await event.answer(
                new_text=make_auction_message(auction),
                format=ParseMode.HTML,
                attachments=[create_auction_kb.as_markup() if auction.state == -1 else stop_auction_kb.as_markup()]
            )
        else:
            await event.message.answer(
                text=make_auction_message(auction),
                format=ParseMode.HTML,
                attachments=[create_auction_kb.as_markup() if auction.state == -1 else stop_auction_kb.as_markup()]
            )
    else:
        await event.message.answer(text='До настоящего момента никакие аукционы не проводились',
                           attachments=[create_auction_kb.as_markup()])