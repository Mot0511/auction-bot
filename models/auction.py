from typing import Optional, List


class Auction:
    id: Optional[int]
    title: str
    body: str
    start_price: int
    max_bet: int
    step: int
    media: List[str]
    state: int
    date: int
    countdown: int
    duration: int
    winner: int

    def __init__(self, id: Optional[int], title: str, body: str, start_price: int, max_bet: int, step: int, state: int, date: int, countdown: int, duration: int, winner=None, media: List[str]=None):
        self.id = id
        self.title = title
        self.body = body
        self.start_price = start_price
        self.max_bet = max_bet
        self.step = step
        self.state = state
        self.date = date
        self.countdown = countdown
        self.duration = duration
        self.winner = winner
        self.media = media