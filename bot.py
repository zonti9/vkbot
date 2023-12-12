import logging

from vkbottle.bot import Bot, Message
from vkbottle.dispatch.rules import ABCRule

from db import DbWork
from config import TOKEN, db_config

# logging.disable()


class AdminRule(ABCRule[Message]):
    async def check(self, event: Message):
        members = await event.ctx_api.messages.get_conversation_members(peer_id=2000000000 + event.chat_id)
        admin = list(filter(lambda member: member.member_id == event.from_id, members.items))[0].is_admin
        return admin


class ModerRule(ABCRule[Message]):
    def __init__(self, db: DbWork):
        self.db = db

    async def check(self, event: Message) -> bool:
        members = await event.ctx_api.messages.get_conversation_members(peer_id=2000000000 + event.chat_id)
        admin = list(filter(lambda member: member.member_id == event.from_id, members.items))[0].is_admin

        if admin:
            return True
        else:
            moder = self.db.get_user_data(event.from_id)['moderator']

            if moder:
                if len(event.text.split()) == 1:
                    return True

                member_id = int(event.text.split()[1].split('|')[0][3:])
                mention_admin = list(filter(lambda member: member.member_id == member_id, members.items))[0].is_admin
                mention_moder = db.get_user_data(member_id)['moderator']

                return not (mention_moder or mention_admin)
            else:
                return False


class MuteRule(ABCRule[Message]):
    def __init__(self, db: DbWork):
        self.db = db

    async def check(self, event: Message) -> bool:
        return bool(self.db.get_user_data(event.from_id)['mute'])


bot = Bot(token=TOKEN)
bot.labeler.custom_rules['moder'] = ModerRule
bot.labeler.custom_rules['mute'] = MuteRule

com_temp = ' [id<member_id>|<member_name>]'

db = DbWork(*db_config.values())


@bot.on.chat_message(text='/kick' + com_temp, moder=db)
async def kick_handler(message: Message, member_id: int):
    await bot.api.messages.remove_chat_user(message.chat_id, member_id)


@bot.on.chat_message(text='/warn' + com_temp, moder=db)
async def warn_handler(message: Message, member_id: int, member_name: str):
    warns = db.get_user_data(member_id)['warns']
    warns += 1
    db.set_user_field(member_id, 'warns', warns)

    await message.answer(f'{member_name} получил {warns} предупреждение')

    if warns >= 3:
        await bot.api.messages.remove_chat_user(message.chat_id, member_id)


@bot.on.chat_message(text='/unwarn' + com_temp, moder=db)
async def unwarn_handler(message: Message, member_id: int, member_name: str):
    db.set_user_field(member_id, 'warns', 0)
    await message.answer(f'{member_name} избавлен от предупреждений')


@bot.on.chat_message(text='/mute' + com_temp, moder=db)
async def mute_handler(message: Message, member_id: int, member_name: str):
    db.set_user_field(member_id, 'mute', True)
    await message.answer(f'{member_name} больше не может отправлять сообщения')


@bot.on.chat_message(text='/unmute' + com_temp, moder=db)
async def unmute_handler(message: Message, member_id: int, member_name: str):
    db.set_user_field(member_id, 'mute', False)
    await message.answer(f'{member_name} снова может отправлять сообщения')


@bot.on.chat_message(AdminRule(), text='/addmoder' + com_temp)
async def add_moder_handler(message: Message, member_id: int, member_name: str):
    db.set_user_field(member_id, 'moderator', True)
    await message.answer(f'{member_name} теперь модератор чата')


@bot.on.chat_message(AdminRule(), text='/removerole' + com_temp)
async def remove_role_handler(message: Message, member_id: int, member_name: str):
    db.set_user_field(member_id, 'moderator', False)
    await message.answer(f'{member_name} больше не является модератором чата')


@bot.on.chat_message(text='/warnlist', moder=db)
async def warnlist_handler(message: Message):
    warnlist = db.get_users_with_warns()

    if warnlist:
        text = ''

        for member_id, warns in warnlist:
            member_name = (await bot.api.users.get(user_ids=member_id))[0].first_name
            text += f'{member_name}: {warns}\n'

        await message.answer(text)
    else:
        await message.answer('Нет пользователей с предупреждениями')


@bot.on.chat_message(AdminRule(), text='/staff')
async def staff_handler(message: Message):
    staff = db.get_users_with_role()

    if staff:
        text = 'Модераторы чата:\n'

        for member_id in staff:
            member_name = (await bot.api.users.get(user_ids=member_id))[0].first_name
            text += f'{member_name}\n'

        await message.answer(text)
    else:
        await message.answer('В этом чате нет модераторов')


@bot.on.chat_message(mute=db)
async def message_handler(message: Message):
    message_id = (await bot.api.messages.get_by_conversation_message_id(
        peer_id=2000000000 + message.chat_id,
        conversation_message_ids=message.conversation_message_id
    )).items[0].id
    logging.info(message_id)
    await bot.api.messages.delete(message_ids=[message_id], delete_for_all=True)


if __name__ == '__main__':
    bot.run_forever()
