from maxapi.types import CallbackButton
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder

create_auction_kb = InlineKeyboardBuilder()
create_auction_kb.row(
    CallbackButton(text='Запустить новый аукцион', payload='create-auction')
)

stop_auction_kb = InlineKeyboardBuilder()
stop_auction_kb.row(
    CallbackButton(text='Остановить аукцион', payload='stop-auction')
)

confirm_auction_kb = InlineKeyboardBuilder()
confirm_auction_kb.row(
    CallbackButton(text='Подтвердить создание аукциона', payload='confirm-auction')
)

back_main_admin = InlineKeyboardBuilder()
back_main_admin.row(
    CallbackButton(text='Вернуться в админ панель', payload='admin'),
)
back_main_admin.row(
    CallbackButton(text='Вернуться в главное меню', payload='last-auction')
)

back_admin = InlineKeyboardBuilder()
back_admin.row(
    CallbackButton(text='Вернуться в админ панель', payload='admin')
)