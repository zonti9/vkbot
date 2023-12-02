import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from db import DbWork
from config import TOKEN


class VkBot:
    def __init__(self, token):
        self.vk_session = vk_api.VkApi(token=token)
        self.longpoll = VkLongPoll(self.vk_session)
        self.vk = self.vk_session.get_api()
        self.db = DbWork()
        self.commands_to_user = ('/kick', '/warn', '/unwarn', '/mute', '/unmute')
        self.ind_commands = ('/warnlist',)

    def kick(self, member_id: int, chat_id: int) -> None:
        self.vk.messages.removeChatUser(
            chat_id=chat_id,
            member_id=member_id
        )

    def warn(self, member_id: int, member_name: str, chat_id: int, warns: int) -> None:
        warns += 1
        self.db.set_user_warn(warns, member_id)

        self.vk.messages.send(
            random_id=0,
            chat_id=chat_id,
            message=f'{member_name} получил {warns} предупреждение'
        )

        if warns >= 3:
            self.kick(member_id, chat_id)

    def run(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.from_chat and event.to_me and event.text:
                members = self.vk.messages.getConversationMembers(peer_id=2000000000 + event.chat_id)
                is_admin = sorted(members['items'],
                                  key=lambda member: member['member_id'] == event.user_id,
                                  reverse=True)[0].get('is_admin', False)
                if is_admin:
                    if (msg := event.text.split())[0] in self.commands_to_user:
                        member_id = msg[1].split('|')[0][3:]
                        try:
                            member_name = self.vk.users.get(user_ids=member_id)[0]['first_name']
                        except IndexError:
                            self.vk.messages.send(
                                random_id=0,
                                chat_id=event.chat_id,
                                message='Указан неверный пользователь'
                            )
                            continue
                        member_data = self.db.get_user_data(member_id)

                        match msg[0]:
                            case '/kick':
                                self.kick(member_id, event.chat_id)
                            case '/warn':
                                self.warn(member_id, member_name, event.chat_id, member_data['warns'])
                            case '/unwarn':
                                self.db.set_user_warn(0, member_id)

                                self.vk.messages.send(
                                    random_id=0,
                                    chat_id=event.chat_id,
                                    message=f'{member_name} избавлен от предупреждений'
                                )
                            case '/mute':
                                self.db.set_user_mute(True, member_id)

                                self.vk.messages.send(
                                    random_id=0,
                                    chat_id=event.chat_id,
                                    message=f'{member_name} больше не может отправлять сообщения'
                                )
                            case '/unmute':
                                self.db.set_user_mute(False, member_id)

                                self.vk.messages.send(
                                    random_id=0,
                                    chat_id=event.chat_id,
                                    message=f'{member_name} снова может отправлять сообщения'
                                )
                    elif event.text in self.ind_commands:
                        match event.text:
                            case '/warnlist':
                                warnlist = self.db.get_users_with_warns()

                                if warnlist:
                                    message = ''

                                    for member_id, warns in warnlist:
                                        member_name = self.vk.users.get(user_ids=member_id)[0]['first_name']
                                        message += f'{member_name}: {warns}\n'

                                    self.vk.messages.send(
                                        random_id=0,
                                        chat_id=event.chat_id,
                                        message=message
                                    )
                                else:
                                    self.vk.messages.send(
                                        random_id=0,
                                        chat_id=event.chat_id,
                                        message='Нет пользователей с предупреждениями'
                                    )
            elif event.type == VkEventType.MESSAGE_NEW and event.from_chat and event.to_me:
                member_id = event.user_id
                member_name = self.vk.users.get(user_ids=member_id)[0]['first_name']
                member_data = self.db.get_user_data(member_id)

                if member_data['mute']:
                    self.warn(member_id, member_name, event.chat_id, member_data['warns'])


if __name__ == '__main__':
    VkBot(TOKEN).run()
