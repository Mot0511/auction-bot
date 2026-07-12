from datetime import datetime
from sqlite3 import Connection, Cursor
from typing import Any

from models.user import User
from models.auction import Auction


class DBService:
    def __init__(self, connection: Connection, cursor: Cursor):
        self.connection = connection
        self.cursor = cursor

    async def get_media_tokens(self, auction_id: int):
        self.cursor.execute("SELECT token FROM media WHERE auction=?", (auction_id,))
        tokens = [row[0] for row in self.cursor.fetchall()]
        return tokens

    async def get_auctions(self, start, end):
        self.cursor.execute("SELECT * FROM auctions ORDER BY id DESC LIMIT ?, ?", (start, end))
        data = self.cursor.fetchall()
        if data:
            res = [Auction(*row, await self.get_media_tokens(row[0])) for row in data]
            return res
        else:
            return None

    async def get_last_auction(self):
        self.cursor.execute("SELECT * FROM auctions ORDER BY date DESC LIMIT 1")
        data = self.cursor.fetchone()
        media = await self.get_media_tokens(data[0])
        if data:
            return Auction(*data, media)
        else:
            return None

    async def create_auction(self, data):
        self.cursor.execute(
            "INSERT INTO auctions (title, body, start_price, max_bet, step, state, date, countdown, duration) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) RETURNING id",
            (data['title'], data['body'], data['price'], data['price'], int(data['step']), 0, datetime.now().timestamp(), data['countdown'], data['duration'])
        )
        res = self.cursor.fetchone()
        if data['media']:
            for token in data['media']:
                self.cursor.execute("INSERT INTO media (token, auction) VALUES (?, ?)", (token, res[0]))

        self.connection.commit()

        return res[0]

    async def start_auction(self, auction_id):
        self.cursor.execute(
            "UPDATE auctions SET state=1 WHERE id=?",
            (auction_id,)
        )
        self.connection.commit()

    async def stop_auction(self, auction_id):
        self.cursor.execute(
            "UPDATE auctions SET state=-1 WHERE id=?", (auction_id,)
        )
        self.connection.commit()

    async def join_auction(self, user_id, chat_id, tel, username, auction_id) -> Any:
        self.cursor.execute(
            "INSERT INTO users (user_id, chat_id, tel, username, auction) VALUES (?, ?, ?, ?, ?) RETURNING id",
            (user_id, chat_id, tel, username, auction_id)
        )
        data = self.cursor.fetchone()
        self.connection.commit()
        return data[0]

    async def set_max_bet(self, bet: int, auction_id: int):
        self.cursor.execute(
            "UPDATE auctions SET max_bet=? WHERE id=?",
            (bet, auction_id)
        )
        self.connection.commit()

    async def set_step(self, new_step: int, auction_id: int):
        self.cursor.execute(
            "UPDATE auctions SET step=? WHERE id=?",
            (new_step, auction_id)
        )

        self.connection.commit()

    async def leave_auction(self, chat_id, auction_id):
        self.cursor.execute(
            "DELETE FROM users WHERE chat_id=? AND auction=?",
            (chat_id, auction_id)
        )
        self.connection.commit()

    async def get_participants(self, auction_id):
        self.cursor.execute("SELECT * FROM users WHERE auction=?", (auction_id,))
        data = self.cursor.fetchall()
        res = [User(*row) for row in data]
        return res

    async def is_user_exists(self, chat_id):
        self.cursor.execute("SELECT * FROM users WHERE chat_id=?", (chat_id,))
        data = self.cursor.fetchone()
        if data: return True
        return False
