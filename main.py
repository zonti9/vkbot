from vk_api.longpoll import VkEventType
from bot import VkBot
from config import TOKEN


def main() -> None:
    bot = VkBot(TOKEN)
    for event in bot.longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            if event.from_chat:
                if bot.is_admin(event.user_id, event.chat_id):
                    try:
                        member_id = int(event.text.split()[1].split('|')[0][3:])
                        member_name = bot.vk.users.get(user_ids=member_id)[0]['first_name']

                        if '/kick' in event.text:
                            bot.kick(member_id, event.chat_id)
                        elif '/warn' in event.text:
                            bot.warn(member_id, member_name, event.chat_id)
                        elif '/unwarn' in event.text:
                            bot.unwarn(member_id, member_name, event.chat_id)
                    except Exception as e:
                        print(e)


if __name__ == '__main__':
    main()
