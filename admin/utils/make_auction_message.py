from models.auction import Auction
from datetime import datetime

async def make_auction_message(auction: Auction):

    date = datetime.fromtimestamp(auction.date)

    return f"""
<b>Последний аукцион #{auction.id} ({date.strftime("%d.%m.%Y")}):</b>\n
<u>Тема:</u>
{auction.title}\n
<u>Описание:</u>
{auction.body}\n
<u>Стартовая цена:</u> {auction.start_price} руб.
<u>Шаг ставки:</u> {auction.step} руб.
{f"<u>Максимальная ставка:</u> {auction.max_bet} руб." if auction.state == -1 else ''}\n
<u>Состояние:</u> <i>{'еще не начался' if auction.state == 0 else 'проводится' if auction.state == 1 else 'завершен'}.</i>
"""