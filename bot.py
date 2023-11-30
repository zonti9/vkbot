import vk_api
from vk_api.longpoll import VkLongPoll
from db import DbWork


class VkBot:
    def __init__(self, token):
        self.vk_session = vk_api.VkApi(token=token)
        self.longpoll = VkLongPoll(self.vk_session)
        self.vk = self.vk_session.get_api()
        self.db = DbWork()

    def is_admin(self, sender_id: int, chat_id: int) -> bool:
        members = self.vk.messages.getConversationMembers(peer_id=2000000000 + chat_id)
        for member in members['items']:
            if member['member_id'] == sender_id:
                return member.get('is_admin', False)

    def kick(self, member_id: int, chat_id: int) -> None:
        self.vk.messages.removeChatUser(
            chat_id=chat_id,
            member_id=member_id
        )

    def warn(self, member_id: int, member_name: str, chat_id: int) -> None:
        warns = self.db.get_user_warns(member_id)
        warns += 1
        self.db.add_user_warn(warns, member_id)

        self.vk.messages.send(
            random_id=0,
            chat_id=chat_id,
            message=f'{member_name} получил {warns} предупреждение'
        )

        if warns >= 5:
            self.kick(member_id, chat_id)

    def unwarn(self, member_id: int, member_name: str, chat_id: int) -> None:
        self.db.add_user_warn(0, member_id)

        self.vk.messages.send(
            random_id=0,
            chat_id=chat_id,
            message=f'{member_name} избавлен от предупреждений'
        )
