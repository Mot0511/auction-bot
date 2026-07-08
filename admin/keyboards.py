from maxapi.types import CallbackButton, MessageButton
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder

create_auction_btn = CallbackButton(text='Запустить новый аукцион', payload='create-auction')
stop_auction_btn = CallbackButton(text='Остановить аукцион', payload='stop-auction')
get_auctions_history = CallbackButton(text='История аукционов', payload='get-auctions-history')
get_participants_btn = CallbackButton(text='Список участников', payload='get-participants')
skip_media_btn = MessageButton(text='Пропустить')

confirm_auction_kb = InlineKeyboardBuilder()
confirm_auction_kb.row(
    MessageButton(text='Подтвердить создание аукциона')
)

back_main_admin_kb = InlineKeyboardBuilder()
back_main_admin_kb.row(
    CallbackButton(text='<- Админ панель', payload='admin'),
)
back_main_admin_kb.row(
    CallbackButton(text='<- Главное меню', payload='last-auction')
)

back_admin_kb = InlineKeyboardBuilder()
back_admin_kb.row(
    CallbackButton(text='<- Админ панель', payload='admin')
)