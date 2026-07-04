from maxapi.context import MemoryContext
from maxapi.enums import ParseMode

from db import DBService

async def send_auction_message(attachments, event, context: MemoryContext, db: DBService):
    auction = await db.get_last_auction()
    if auction:
        await context.update_data(last_auction_id=auction.id)
        await event.message.answer(
            text=make_auction_message(auction),
            parse_mode=ParseMode.HTML,
            attachments=[create_auction_kb.as_markup() if auction.state == -1 else stop_auction_kb.as_markup()]
        )
    else:
        await event.message.answer(text='До настоящего момента никакие аукционы не проводились.',
                                   attachments=[create_auction_kb.as_markup()])