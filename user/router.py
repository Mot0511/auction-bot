from maxapi import Router
from maxapi.context import MemoryContext, StatesGroup, State
from maxapi.filters import F, ContactFilter
from maxapi.enums import ParseMode, UploadType
from maxapi.types import MessageCreated, MessageCallback, CallbackButton, ButtonsPayload, InputMedia, AttachmentPayload, \
    AttachmentUpload, MessageButton

import consts
from admin.keyboards import get_participants_btn
from admin.utils.get_media_attachments import get_media_attachments
from admin.utils.make_auction_message import make_auction_message
from admin.utils.make_participants_message import make_participants_message
from db import DBService
from filters.digit_filter import DigitFilter
from filters.not_command_filter import NotCommandFilter
from timer import Timer
from user.keyboards import get_history_btn, take_part_btn, accept_agreements_btn, leave_auction_btn, get_contact_btn, \
    back_main_btn, more_history_btn
from utils.broadcast import broadcast
from models.user import User
from maxapi.types.attachments.contact import Contact
from maxapi.types import AttachmentUpload, PhotoAttachmentPayload, BotStarted
from filters.tel_filter import TelFilter
from utils.get_str_time import get_str_time

user_router = Router()

class UserState(StatesGroup):
    tel = State()

@user_router.message_callback(F.callback.payload == 'last-auction')
async def main_menu(event: MessageCallback, context: MemoryContext, db: DBService): 
    await send_last_auction(event, context, db)

async def send_last_auction(event, context: MemoryContext, db: DBService):
    await context.set_state(None)
    await context.update_data(auctions_history_start=None)
    auction = await db.get_last_auction()
    if auction:
        attachments = []
        btns = [[get_history_btn]]
        if auction.state != -1:
            btns.insert(0, [take_part_btn])
            btns[1].append(get_participants_btn)
        attachments.append(ButtonsPayload(buttons=btns).pack())
        if auction.media: attachments += await get_media_attachments(auction.media)
        if isinstance(event, BotStarted):
            await event.bot.send_message(
                chat_id=event.chat_id,
                text=await make_auction_message(auction),
                parse_mode=ParseMode.HTML,
                attachments=attachments
            )
            return
        
        await event.message.answer(
            text=await make_auction_message(auction),
            parse_mode=ParseMode.HTML,
            attachments=attachments
        )
    else:
        if isinstance(event, BotStarted): 
            await event.bot.send_message(chat_id=event.chat_id, text='До настоящего момента никакие аукционы не проводились.')
            return
        await event.message.answer(text='До настоящего момента никакие аукционы не проводились.')

@user_router.message_callback(F.callback.payload == 'get-participants')
async def get_participants(event: MessageCallback, db: DBService):
    auction = await db.get_last_auction()
    participants = await db.get_participants(auction.id)
    await event.answer(new_text=await make_participants_message(participants, auction), format=ParseMode.MARKDOWN, attachments=[ButtonsPayload(buttons=[[back_main_btn]]).pack()])

@user_router.message_callback(F.callback.payload == 'get-auctions-history')
async def get_auctions_history(event: MessageCallback, db: DBService, context: MemoryContext):
    memory = await context.get_data()
    start = 0
    if memory.get('auctions_history_start'):
        start = memory['auctions_history_start']

    auctions = await db.get_auctions(start, start+3)
    if not auctions:
        await event.message.answer(text='Больше аукционов пока не проходило.', attachments=[ButtonsPayload(buttons=[[back_main_btn]]).pack()])  
        return
    for i, auction in enumerate(auctions):
        attachments = []
        if i == len(auctions) - 1: attachments.append(ButtonsPayload(buttons=[[more_history_btn], [back_main_btn]]).pack())
        if auction.media: attachments += await get_media_attachments(auction.media)
        await event.message.answer(
            text=await make_auction_message(auction),
            attachments=attachments,
            parse_mode=ParseMode.HTML
        )

    await context.update_data(auctions_history_start=start+3)


@user_router.message_callback(F.callback.payload == 'take-part')
async def take_part(event: MessageCallback, db: DBService, context: MemoryContext):
    is_user_exists = await db.is_user_exists(event.message.recipient.chat_id)
    if is_user_exists:
        await get_contact(event, context)
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
                ButtonsPayload(buttons=[[accept_agreements_btn]]).pack()
            ]
        )

@user_router.message_callback(F.callback.payload == 'accept-agreements')
async def accept_agreements(event: MessageCallback, context: MemoryContext):
    await get_contact(event, context)

async def get_contact(event: MessageCallback, context: MemoryContext):
    await event.message.answer(
        text='Напишите свой номер телефона (например +79221234567), чтобы администратор смог связаться с вами в случае вашего выигрыша.',
    )
    await context.set_state(UserState.tel)

@user_router.message_created(F.message.body.text and UserState.tel and NotCommandFilter() and TelFilter())
async def join_auction(event: MessageCreated, db: DBService, timer: Timer, context: MemoryContext):
    await context.set_state(None)
    tel = event.message.body.text
    auction = await db.get_last_auction()
    if not auction: await event.message.answer(text='До настоящего момента никакие аукционы не проводились.')
    userdata = event.message.sender
    id = await db.join_auction(userdata.user_id, event.message.recipient.chat_id, tel, userdata.first_name, auction.id)
    user = User(
        id=id,
        user_id=userdata.user_id,
        chat_id=event.message.recipient.chat_id,
        tel=tel,
        username=userdata.first_name,
        auction=auction.id
    )
    await timer.join(user)
    await event.message.answer(
        text=f'Вы приняли участие в аукционе #{auction.id}: "{auction.title}".\n' +
        (f'Он начнется через {await get_str_time(timer.seconds)}' if auction.state == 0 else 
         (f'Он закончится через {await get_str_time(timer.seconds)}' if auction.state == 1 else '')
         ),
        attachments=[ButtonsPayload(buttons=[[leave_auction_btn]]).pack()]
    )

@user_router.message_callback(F.callback.payload == 'leave-auction')
async def leave_auction(event: MessageCallback, context: MemoryContext, db: DBService, timer: Timer):
    auction = timer.current_auction
    await db.leave_auction(event.message.recipient.chat_id, auction.id)
    await timer.leave(event.message.recipient.user_id)
    await event.message.answer(
        text=f'Вы покинули аукцион #{auction.id}: "{auction.title}".'
    )
    await send_last_auction(event, context, db)

@user_router.message_created(F.message.body.text, DigitFilter())
async def place_bet(event: MessageCreated, db: DBService, timer: Timer):
    auction = timer.current_auction
    if timer.stage != 1: return
    if not event.message.sender.user_id in timer.participants: return

    bet = int(event.message.body.text)
    if bet % auction.step != 0:
        await event.message.answer(text=f'Ставка должна быть кратна шагу ставки текущего аукциона ({auction.step} руб.)')
        return

    if bet <= auction.max_bet:
        await event.message.answer(text=f'Ваша ставка должна быть больше прошлой максимальной ставки ({auction.max_bet} руб.)')
        return

    await broadcast(
        event,
        f"{event.message.sender.first_name} - {bet} руб. (+{bet - auction.max_bet})",
        auction.id,
        db,
        attachments=[ButtonsPayload(buttons=[[MessageButton(text=f'{bet+auction.step}')]]).pack()]
    )
    timer.current_auction.max_bet = bet
    timer.leader = timer.participants[event.message.sender.user_id]
    await db.set_max_bet(bet, auction.id)
    if timer.seconds <= 120:
        await timer.add_time()