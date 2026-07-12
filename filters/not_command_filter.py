from maxapi.types import MessageCreated
from maxapi.filters.filter import BaseFilter


class NotCommandFilter(BaseFilter):
    async def __call__ (self, event: MessageCreated):
        text = event.message.body.text
        if text[0] == '/':
            return False
        return True