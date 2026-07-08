from maxapi.types import CallbackButton, RequestContactButton
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder

last_auction_kb = InlineKeyboardBuilder()
last_auction_kb.row(
    CallbackButton(text='Последний аукцион', payload='last-auction'),
)

take_part_btn = CallbackButton(text='Принять участие', payload='take-part')
get_history_btn = CallbackButton(text='История аукционов', payload='get-auctions-history')
more_history_btn = CallbackButton(text='Показать еще', payload='get-auctions-history')
accept_agreements_btn = CallbackButton(text='Принять все соглашения', payload='accept-agreements')
leave_auction_btn = CallbackButton(text='Выйти из аукциона', payload='leave-auction')
get_contact_btn = RequestContactButton(text='Отправить свой контакт')
back_main_btn = CallbackButton(text='<- Главное меню', payload='last-auction')