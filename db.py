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

    def add_user(self, vk_id: int) -> dict:
        self.cur.execute(f'insert into users (vk_id) values ({vk_id})')
        self.con.commit()
        return {'warns': 0, 'mute': False}

    def get_user_data(self, vk_id: int) -> dict:
        self.cur.execute(f'select warns, mute from users where vk_id={vk_id}')
        if isinstance(data := self.cur.fetchone(), tuple):
            return dict(zip(('warns', 'mute'), data))
        else:
            return self.add_user(vk_id)

    def set_user_warn(self, warns: int, vk_id: int) -> None:
        self.cur.execute(f'update users set warns = {warns} where vk_id={vk_id}')
        self.con.commit()

    def get_users_with_warns(self) -> list:
        self.cur.execute('select vk_id, warns from users where warns != 0')
        return self.cur.fetchall()

    def set_user_mute(self, muted: bool, vk_id: int) -> None:
        self.cur.execute(f'update users set mute = {muted} where vk_id={vk_id}')
        self.con.commit()
