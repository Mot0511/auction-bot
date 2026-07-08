from models.auction import Auction
from models.user import User

async def make_participants_message(users: list[User], auction: Auction):
    list = '\n'.join([f'{i+1}. [{user.username}]({user.user_id})' for i, user in enumerate(users)])
    return f"""
**Список участников последнего аукциона #{auction.id} "{auction.title}":**

{list}
"""