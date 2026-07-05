from typing import Optional


class Auction:
    id: Optional[int]
    title: str
    body: str
    start_price: int
    max_bet: int
    step: int
    media: Optional[str]
    state: int
    date: int
    countdown: int
    duration: int
    winner: int

    def __init__(self, id: Optional[int], title: str, body: str, start_price: int, max_bet: int, step: int, media: Optional[str], state: int, date: int, countdown: int, duration: int, winner = None):
        self.id = id
        self.title = title
        self.body = body
        self.start_price = start_price
        self.max_bet = max_bet
        self.step = step
        self.media = media
        self.state = state
        self.date = date
        self.countdown = countdown
        self.duration = duration
        self.winner = winner