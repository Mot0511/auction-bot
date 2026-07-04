from typing import Optional


class Auction:
    id: Optional[int]
    title: str
    body: str
    price: int
    step: int
    media: Optional[str]
    state: int
    date: int
    countdown: int
    duration: int

    def __init__(self, id: Optional[int], title: str, body: str, price: int, step: int, media: Optional[str], state: int, date: int, countdown: int, duration: int):
        self.id = id
        self.title = title
        self.body = body
        self.price = price
        self.step = step
        self.media = media
        self.state = state
        self.date = date
        self.countdown = countdown
        self.duration = duration