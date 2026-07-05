from maxapi.types import MessageCreated
from maxapi.filters.filter import BaseFilter


class DigitFilter(BaseFilter):
    async def __call__ (self, event: MessageCreated):
        text = event.message.body.text
        if not text.isdigit():
            await event.message.answer(text='Значение должно быть числом. Попробуйте еще раз.')
            return False
        if text == '0':
            await event.message.answer(text='Значение не может быть равно нулю. Попробуйте еще раз.')
            return False
        if str(int(text)) != text:
            await event.message.answer(text='Значение должно быть целым числом. Попробуйте еще раз.')
            return False

        return True