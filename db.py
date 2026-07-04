from datetime import datetime
from sqlite3 import Connection, Cursor

from models.auction import Auction


class DBService:
    def __init__(self, connection: Connection, cursor: Cursor):
        self.connection = connection
        self.cursor = cursor

    async def get_auctions(self):
        self.cursor.execute("SELECT * FROM auctions")
        data = self.cursor.fetchall()
        if data:
            res = [Auction(*row) for row in data]
            return res
        else:
            return None

    async def get_last_auction(self):
        self.cursor.execute("SELECT * FROM auctions ORDER BY date DESC LIMIT 1")
        data = self.cursor.fetchone()
        if data:
            return Auction(*data)
        else:
            return None

    async def create_auction(self, data):
        self.cursor.execute(
            "INSERT INTO auctions (title, body, price, step, media, state, date, countdown, duration) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) RETURNING id",
            (data['title'], data['body'], 0, int(data['step']), '', 0, datetime.now().timestamp(), data['countdown'], data['duration'])
        )
        data = self.cursor.fetchone()
        self.connection.commit()

        return data[0]

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

    async def join_auction(self, chat_id, tel, username, auction_id):
        self.cursor.execute(
            "INSERT INTO users (chat_id, tel, username, auction) VALUES (?, ?, ?, ?)",
            (chat_id, tel, username, auction_id)
        )
        self.connection.commit()


    async def leave_auction(self, chat_id, auction_id):
        self.cursor.execute(
            "DELETE FROM users WHERE chat_id=? and auction=?",
            (chat_id, auction_id)
        )
        self.connection.commit()

    async def get_participants(self, auction_id):
        self.cursor.execute("SELECT * FROM users WHERE auction=?", (auction_id,))
        return self.cursor.fetchall()

    async def is_user_exists(self, chat_id):
        self.cursor.execute("SELECT * FROM users WHERE chat_id=?", (chat_id,))
        data = self.cursor.fetchone()
        if data: return True
        return False