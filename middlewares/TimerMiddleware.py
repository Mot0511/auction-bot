from sqlite3 import Connection

from maxapi.filters.middleware import BaseMiddleware
from typing import Any, Awaitable, Callable, Dict

from db import DBService
from timer import Timer


class TimerMiddleware(BaseMiddleware):

    def __init__(self, timer: Timer) -> None:
        self.timer = timer

    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event_object: Any,
        data: Dict[str, Any],
    ) -> Any:
        self.timer.event = event_object
        data['timer'] = self.timer
        return await handler(event_object, data)
