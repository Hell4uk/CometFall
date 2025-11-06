from ..db.models import Users
from tortoise.exceptions import DoesNotExist

# TODO : Создать UserService, сделать выдачу стартового набор, сделать формулу для расчета EXP-LVL, сделать метод на добавление XP
class UserService():
    def __init__(self) -> None:
        pass

    async def get_by_telegram_id(self, id: int) -> Users:
        user = await Users.get_or_none(telegram_id=id)
        return user
    
    async def create(self, telegram_id: int, username: str='', first_name: str='', last_name: str='', coins: int = 150, exp: int = 0, lvl: int=0) -> Users:
        user, created = await Users.get_or_create(telegram_id=telegram_id, defaults={
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "coins": coins,
            "exp": exp,
            "lvl": lvl,
        },)


        if created:
            raise DoesNotExist("User already exist")
        
        return user