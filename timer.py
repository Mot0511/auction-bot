import asyncio
from typing import Optional

from maxapi.enums import ParseMode
from maxapi.filters import Contact
from maxapi.types import MessageCreated, attachments, ButtonsPayload, MessageButton
from db import DBService
from models.auction import Auction
from models.user import User
from utils.broadcast import broadcast


class Timer:
    stage: int = -1

    current_auction: Auction | None = None
    leader: User = None
    participants = {}
    contacts = {}
    admin_id: int

    seconds: int = None
    event: MessageCreated = None

    def __init__(self, db: DBService):
        self.db = db

    async def start_timer(self, auction: Auction):
        self.current_auction = auction
        self.seconds = auction.countdown
        self.stage = 0
        while self.stage == 0:
            await asyncio.sleep(1)
            self.seconds -= 1
            print(f'До начала аукциона - {self.seconds}')
            if self.seconds <= 0:
                await broadcast(
                    self.event,
                    f'Торги по аукциону #{auction.id}: "{auction.title}" начались! Можете сделать свою ставку сообщением с числом.\n\nСтартовая цена - {auction.start_price} руб.\nШаг ставки - {auction.step} руб.',
                    auction.id,
                    self.db,
                )
                await self.db.start_auction(auction.id)
                self.stage = 1
                await self.track_end(auction)

    async def track_end(self, auction: Auction):
        self.seconds = auction.duration
        while self.stage == 1:
            await asyncio.sleep(1)
            self.seconds -= 1
            print(f'Идет аукцион - {self.seconds}')
            if self.seconds <= 0:
                if not self.leader:
                    await broadcast(
                        self.event,
                        f'Аукцион #{auction.id}: "{auction.title}" завершен!\nСтавок не было, поэтому никто не выиграл.</b>',
                        auction.id,
                        self.db
                    )
                else:
                    await broadcast(
                        self.event,
                        f'Аукцион #{auction.id}: "{auction.title}" завершен!\nПродано участнику <b>{self.leader.username}</b> за {self.current_auction.max_bet} руб.',
                        auction.id,
                        self.db
                    )
                    if self.contacts[self.leader.user_id]:
                        await self.event.bot.send_message(
                            chat_id=self.admin_id,
                            text='Контакт победителя',
                            attachments=[self.contacts[self.leader.user_id]]
                        )
                self.stage = -1
                self.current_auction = None
                self.participants = {}
                self.contacts = {}
                await self.db.stop_auction(auction.id)

    async def add_time(self):
        self.seconds += 3

    async def stop_timer(self):
        self.stage = -1

    async def join(self, user: User, contact: Optional[Contact] = None):
        self.participants[user.user_id] = user
        self.contacts[user.user_id] = contact

    async def leave(self, user_id: int):
        del self.participants[user_id]
        del self.contacts[user_id]