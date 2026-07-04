from models.auction import Auction
from datetime import datetime

def make_confirm_auction_message(data):
    return f"""
<u>Тема:</u>
{data['title']}\n
<u>Описание:</u>
{data['body']}\n
<u>Шаг ставки:</u> {data['step']}\n
<u>До начала (в мин.):</u> {data['countdown']}
<u>Продолжительность аукциона (в мин.):</u> {data['duration']}
"""