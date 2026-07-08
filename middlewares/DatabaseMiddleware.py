from sqlite3 import Connection

from maxapi.filters.middleware import BaseMiddleware
from typing import Any, Awaitable, Callable, Dict

from db import DBService

class DatabaseMiddleware(BaseMiddleware):
    db: DBService

    def __init__(self, db: DBService):
        self.db = db

    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event_object: Any,
        data: Dict[str, Any],
    ) -> Any:
        data['db'] = self.db
        return await handler(event_object, data)