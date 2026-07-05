import asyncio
from maxapi.types import MessageCreated, attachments, ButtonsPayload
from db import DBService
from models.auction import Auction
from models.user import User
from utils.broadcast import broadcast


class Timer:
    stage: int = -1

    current_auction: Auction = None
    leader: User

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
            if self.seconds <= 0:
                await broadcast(
                    self.event,
                    f'Аукцион #{auction.id}: "{auction.title}" завершен!\nПродано участнику - Matvey.',
                    auction.id,
                    self.db
                )
                self.stage = -1
                await self.db.stop_auction(auction.id)

    async def add_time(self):
        self.seconds += 3


    async def stop_timer(self):
        self.stage = -1