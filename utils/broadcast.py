from maxapi.types import MessageCreated
from db import DBService


async def broadcast(event: MessageCreated, message: str, auction_id: int, db: DBService):
    participants = await db.get_participants(auction_id)
    for participant in participants:
        await event.bot.send_message(
            chat_id=participant[1],
            text=message
        )