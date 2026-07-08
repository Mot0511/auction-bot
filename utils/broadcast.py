from maxapi.enums import ParseMode
from maxapi.types import MessageCreated, ButtonsPayload
from db import DBService


async def broadcast(event: MessageCreated, message: str, auction_id: int, db: DBService, attachments=None):
    participants = await db.get_participants(auction_id)
    for participant in participants:
        await event.bot.send_message(
            chat_id=participant.chat_id,
            text=message,
            parse_mode=ParseMode.HTML,
            attachments=attachments
        )