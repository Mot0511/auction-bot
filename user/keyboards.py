from maxapi.types import CallbackButton
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder

last_auction_kb = InlineKeyboardBuilder()
last_auction_kb.row(
    CallbackButton(text='Последний аукцион', payload='last-auction'),
)

take_part_btn = CallbackButton(text='Принять участие', payload='take-part')
get_history_btn = CallbackButton(text='История аукционов', payload='auction-history')

accept_agreenments_btn = CallbackButton(text='Принять все соглашения', payload='accept-agreenments')
leave_auction_btn = CallbackButton(text='Выйти из аукциона', payload='leave-auction')