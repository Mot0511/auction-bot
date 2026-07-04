from maxapi import Router
from maxapi.context import MemoryContext, StatesGroup, State
from maxapi.filters import F
from maxapi.enums import ParseMode, UploadType
from maxapi.types import MessageCreated, MessageCallback, CallbackButton, ButtonsPayload, InputMedia, AttachmentPayload, \
    AttachmentUpload

import consts
from admin.utils.make_auction_message import make_auction_message
from db import DBService
from timer import Timer
from user.keyboards import get_history_btn, take_part_btn, accept_agreenments_btn, leave_auction_btn

user_router = Router()

@user_router.message_callback(F.callback.payload == 'last-auction')
async def main_menu(event: MessageCallback, context: MemoryContext, db: DBService):
    await send_last_auction(event, context, db)

async def send_last_auction(event, context: MemoryContext, db: DBService):
    await context.set_state(None)
    auction = await db.get_last_auction()
    if auction:
        btns = [[get_history_btn]]
        if auction.state != -1: btns.insert(0, [take_part_btn])
        await event.message.answer(
            text=make_auction_message(auction),
            parse_mode=ParseMode.HTML,
            attachments=[ButtonsPayload(buttons=btns).pack()]
        )
    else:
        await event.message.answer(text='До настоящего момента никакие аукционы не проводились.')

@user_router.message_callback(F.callback.payload == 'take-part')
async def take_part(event: MessageCallback, context: MemoryContext, db: DBService, timer: Timer):
    is_user_exists = await db.is_user_exists(event.message.recipient.chat_id)
    if is_user_exists:
        await join_auction(event, db, timer)
    else:
        await event.answer(
            new_text='Сначала нужно принять согласия на условия сервиса и политику конфиденциальности.',
            attachments=[
                AttachmentUpload(
                    type=UploadType.FILE,
                    payload=AttachmentPayload(token=consts.CONDITIONS_TOKEN)
                ),

            ]
        )
        await event.message.answer(
            attachments=[
                AttachmentUpload(
                    type=UploadType.FILE,
                    payload=AttachmentPayload(token=consts.CONFIDENTIALITY_TOKEN)
                ),
                ButtonsPayload(buttons=[[accept_agreenments_btn]]).pack()
            ]
        )

@user_router.message_callback(F.callback.payload == 'accept-agreenments')
async def accept_agreenments(event: MessageCallback, db: DBService, timer: Timer):
    await join_auction(event, db, timer)

async def join_auction(event: MessageCallback, db: DBService, timer: Timer):
    auction = await db.get_last_auction()
    if not auction: await event.message.answer(text='До настоящего момента никакие аукционы не проводились.')
    await db.join_auction(event.message.recipient.chat_id, '', '', auction.id)
    await event.message.answer(
        text=f'Вы приняли участие в аукционе #{auction.id}: "{auction.title}"\n'+(f'Он начнется через {timer.seconds} секунд' if auction.state == 0 else ''),
        attachments=[ButtonsPayload(buttons=[[leave_auction_btn]]).pack()]
    )

@user_router.message_callback(F.callback.payload == 'leave-auction')
async def leave_auction(event: MessageCallback, context: MemoryContext, db: DBService, timer: Timer):
    auction = timer.current_auction
    await db.leave_auction(event.message.recipient.chat_id, auction.id)
    await event.message.answer(
        text=f'Вы покинули аукцион #{auction.id}: {auction.title}'
    )
    await send_last_auction(event, context, db)