import logging
from vkbottle.bot import Bot, Message
from vkbottle.dispatch.rules import ABCRule
from vkbottle.dispatch.rules.base import CommandRule
from db import DbWork
from config import TOKEN, db_config

logging.disable()


class ModerRule(ABCRule[Message]):
    def __init__(self, db: DbWork):
        self.db = db

    async def check(self, event: Message) -> bool:
        members = await event.ctx_api.messages.get_conversation_members(peer_id=2000000000 + event.chat_id)
        cond1 = sorted(members.items, key=lambda member: member.member_id == event.from_id)[0].is_admin
        cond2 = self.db.get_user_data(event.from_id)['moderator']

        return cond1 or cond2


class MuteRule(ABCRule[Message]):
    def __init__(self, db: DbWork):
        self.db = db

    async def check(self, event: Message) -> bool:
        return bool(self.db.get_user_data(event.from_id)['mute'])


bot = Bot(token=TOKEN)
bot.labeler.custom_rules['moder'] = ModerRule
bot.labeler.custom_rules['mute'] = MuteRule

db = DbWork(*db_config.values())


@bot.on.chat_message(CommandRule('kick', ['/'], 1), moder=db)
async def kick_handler(message: Message, args):
    member_id = int(args[0].split('|')[0][3:])
    await bot.api.messages.remove_chat_user(message.chat_id, member_id)


@bot.on.chat_message(CommandRule('warn', ['/'], 1), moder=db)
async def warn_handler(message: Message, args):
    member_id = int(args[0].split('|')[0][3:])
    member_name = (await bot.api.users.get([member_id]))[0].first_name

    warns = db.get_user_data(member_id)['warns']
    warns += 1
    db.set_user_field(member_id, 'warns', warns)

    await message.answer(f'{member_name} получил {warns} предупреждение')

    if warns >= 3:
        await bot.api.messages.remove_chat_user(message.chat_id, member_id)


@bot.on.chat_message(CommandRule('unwarn', ['/'], 1), moder=db)
async def unwarn_handler(message: Message, args):
    member_id = int(args[0].split('|')[0][3:])
    member_name = (await bot.api.users.get([member_id]))[0].first_name

    db.set_user_field(member_id, 'warns', 0)

    await message.answer(f'{member_name} избавлен от предупреждений')


@bot.on.chat_message(CommandRule('mute', ['/'], 1), moder=db)
async def mute_handler(message: Message, args):
        member_id = int(args[0].split('|')[0][3:])
        member_name = (await bot.api.users.get([member_id]))[0].first_name

        db.set_user_field(member_id, 'mute', True)

        await message.answer(f'{member_name} больше не может отправлять сообщения')


@bot.on.chat_message(CommandRule('unmute', ['/'], 1), moder=db)
async def unmute_handler(message: Message, args):
        member_id = int(args[0].split('|')[0][3:])
        member_name = (await bot.api.users.get([member_id]))[0].first_name

        db.set_user_field(member_id, 'mute', False)

        await message.answer(f'{member_name} снова может отправлять сообщения')


@bot.on.chat_message(CommandRule('addmoder', ['/'], 1), moder=db)
async def add_moder_handler(message: Message, args):
        member_id = int(args[0].split('|')[0][3:])
        member_name = (await bot.api.users.get([member_id]))[0].first_name

        db.set_user_field(member_id, 'moderator', True)

        await message.answer(f'{member_name} теперь модератор чата')


@bot.on.chat_message(CommandRule('removerole', ['/'], 1), moder=db)
async def remove_role_handler(message: Message, args):
        member_id = int(args[0].split('|')[0][3:])
        member_name = (await bot.api.users.get([member_id]))[0].first_name

        db.set_user_field(member_id, 'moderator', False)

        await message.answer(f'{member_name} больше не является модератором чата')


@bot.on.chat_message(text='/warnlist', moder=db)
async def warnlist_handler(message: Message):
    warnlist = db.get_users_with_warns()

    if warnlist:
        text = ''

        for member_id, warns in warnlist:
            member_name = (await bot.api.users.get(user_ids=[member_id]))[0].first_name
            text += f'{member_name}: {warns}\n'

        await message.answer(text)
    else:
        await message.answer('Нет пользователей с предупреждениями')


@bot.on.chat_message(mute=db)
async def message_handler(message: Message):
    message_id = (await bot.api.messages.get_by_conversation_message_id(
        peer_id=2000000000 + message.chat_id,
        conversation_message_ids=message.conversation_message_id
    )).items[0].id
    logging.info(message_id)
    await bot.api.messages.delete(message_ids=message_id, delete_for_all=1)


if __name__ == '__main__':
    bot.run_forever()
