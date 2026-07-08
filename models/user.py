class User:
    id: int
    user_id: int
    chat_id: int
    tel: str
    username: str
    auction: int

    def __init__(self, id: int, user_id: int, chat_id: int, tel: str, username: str, auction: int):
        self.id = id
        self.user_id = user_id
        self.chat_id = chat_id
        self.username = username
        self.tel = tel
        self.auction = auction