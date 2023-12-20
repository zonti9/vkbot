from typing import Any

from mysql.connector import connect


class DbWork:
    def __init__(self, host: str, user: str, password: str, database: str):
        self.con = connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.default_fields = {
            "warns": 0,
            "mute": False,
            "moderator": False
        }
        self.cur = self.con.cursor()

        sql = """
            create table if not exists
                users (
                    vk_id int not null,
                    warns int not null default 0,
                    mute boolean not null default 0,
                    moderator boolean not null default 0,
                    primary key (vk_id)
                );
        """
        self.cur.execute(sql)

    async def add_user(self, vk_id: int) -> Any:
        self.cur.execute(f"insert into users (vk_id) values ({vk_id})")
        self.con.commit()

    async def set_user_field(self, vk_id: int, field_name: str, value: Any):
        self.cur.execute(f"update users set {field_name} = {value} where vk_id={vk_id}")
        self.con.commit()

    async def get_user_field(self, vk_id: int, field_name: str) -> Any:
        self.cur.execute(f"select {field_name} from users where vk_id={vk_id}")
        if data := self.cur.fetchone():
            return data[0]
        else:
            await self.add_user(vk_id)
            return self.default_fields[field_name]

    async def get_users_with_warns(self) -> list:
        self.cur.execute("select vk_id, warns from users where warns != 0")
        return self.cur.fetchall()

    async def get_users_with_mute(self) -> list:
        self.cur.execute("select vk_id from users where mute = true")
        return self.cur.fetchall()

    async def get_users_with_role(self) -> list:
        self.cur.execute("select vk_id from users where moderator = true")
        return self.cur.fetchall()
