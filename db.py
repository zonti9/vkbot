from mysql.connector import connect
from config import db


class DbWork:
    def __init__(self) -> None:
        self.con = connect(
            host=db['host'],
            user=db['username'],
            password=db['password'],
            database='vkbot'
        )

        self.cur = self.con.cursor()

    def add_user(self, vk_id: int) -> int:
        self.cur.execute(f'insert into users (vk_id, warns) values ({vk_id}, 0)')
        self.con.commit()
        return 0

    def get_user_warns(self, vk_id: int) -> int:
        self.cur.execute(f'select warns from users where vk_id={vk_id}')
        if isinstance(warns := self.cur.fetchone()[0], int):
            return warns
        else:
            return self.add_user(vk_id)

    def add_user_warn(self, warns: int, vk_id: int) -> None:
        self.cur.execute(f'update users set warns = {warns} where vk_id={vk_id}')
        self.con.commit()
