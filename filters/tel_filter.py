from maxapi.filters.filter import BaseFilter
from maxapi.types import MessageCreated
import re

class TelFilter(BaseFilter):
    async def __call__ (self, event: MessageCreated):
        text = event.message.body.text
        reg = r'\+?[78][0-9]{10}'
        if re.fullmatch(reg, text):
            return True
        return False