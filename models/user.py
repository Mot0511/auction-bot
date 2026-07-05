class User:
    id: int
    chat_id: int
    username: str
    tel: int

    def __init__(self, id: int, chat_id: int, username: str, tel: int):
        self.id = id
        self.chat_id = chat_id
        self.username = username
        self.tel = tel
