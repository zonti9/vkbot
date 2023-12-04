from mysql.connector import connect


class DbWork:
    def __init__(self, host, user, password, database) -> None:
        self.con = connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.column_names = ('warns', 'mute', 'moderator')
        self.cur = self.con.cursor()

    def add_user(self, vk_id: int) -> dict:
        self.cur.execute(f'insert into users (vk_id) values ({vk_id})')
        self.con.commit()
        return dict(zip(self.column_names, (0, False, False)))

    def set_user_field(self, vk_id: int, field_name: str, value: int | bool) -> None:
        self.cur.execute(f'update users set {field_name} = {value} where vk_id={vk_id}')
        self.con.commit()

    def get_user_data(self, vk_id: int) -> dict:
        self.cur.execute(f'select {', '.join(self.column_names)} from users where vk_id={vk_id}')
        if isinstance(data := self.cur.fetchone(), tuple):
            return dict(zip(self.column_names, data))
        else:
            return self.add_user(vk_id)

    def get_users_with_warns(self) -> list:
        self.cur.execute('select vk_id, warns from users where warns != 0')
        return self.cur.fetchall()
