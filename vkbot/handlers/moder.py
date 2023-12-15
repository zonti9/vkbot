from vkbottle.bot import BotLabeler, Message, rules

from vkbot.config import db_con, command_temp


class ModerRule(rules.ABCRule[Message]):
    async def check(self, message: Message) -> bool:
        members = await message.ctx_api.messages.get_conversation_members(peer_id=2000000000 + message.chat_id)
        admin = list(filter(lambda member: member.member_id == message.from_id, members.items))[0].is_admin

        if admin:
            return True
        else:
            moder = await db_con.get_user_data(message.from_id, 'moderator')

            if moder:
                if len(message.text.split()) == 1:
                    return True

                member_id = int(message.text.split()[1].split('|')[0][3:])
                mention_admin = list(filter(lambda member: member.member_id == member_id, members.items))[0].is_admin
                mention_moder = await db_con.get_user_data(member_id, 'moderator')

                return not (mention_moder or mention_admin)
            else:
                return False


moder_labeler = BotLabeler()
moder_labeler.auto_rules = [rules.PeerRule(from_chat=True), ModerRule()]


@moder_labeler.message(text='/kick' + command_temp)
async def kick_handler(message: Message, member_id: int):
    await message.ctx_api.messages.remove_chat_user(message.chat_id, member_id)


@moder_labeler.message(text='/warn' + command_temp)
async def warn_handler(message: Message, member_id: int, member_name: str):
    warns = await db_con.get_user_field(member_id, 'warns')
    warns += 1
    await db_con.set_user_field(member_id, 'warns', warns)

    await message.answer(f'{member_name} получил {warns} предупреждение')

    if warns >= 3:
        await message.ctx_api.messages.remove_chat_user(message.chat_id, member_id)


@moder_labeler.message(text='/unwarn' + command_temp)
async def unwarn_handler(message: Message, member_id: int, member_name: str):
    await db_con.set_user_field(member_id, 'warns', 0)
    await message.answer(f'{member_name} избавлен от предупреждений')


@moder_labeler.message(text='/mute' + command_temp)
async def mute_handler(message: Message, member_id: int, member_name: str):
    await db_con.set_user_field(member_id, 'mute', True)
    await message.answer(f'{member_name} больше не может отправлять сообщения')


@moder_labeler.message(text='/unmute' + command_temp)
async def unmute_handler(message: Message, member_id: int, member_name: str):
    await db_con.set_user_field(member_id, 'mute', False)
    await message.answer(f'{member_name} снова может отправлять сообщения')


@moder_labeler.message(text='/warnlist')
async def warnlist_handler(message: Message):
    warnlist = await db_con.get_users_with_warns()

    if warnlist:
        text = ''

        for member_id, warns in warnlist:
            member_name = (await message.ctx_api.users.get(user_ids=member_id))[0].first_name
            text += f'{member_name}: {warns}\n'

        await message.answer(text)
    else:
        await message.answer('Нет пользователей с предупреждениями')


@moder_labeler.message(text='/staff')
async def staff_handler(message: Message):
    staff = await db_con.get_users_with_role()

    if staff:
        text = 'Модераторы чата:\n'

        for member_id in staff:
            member_name = (await message.ctx_api.users.get(user_ids=member_id))[0].first_name
            text += f'{member_name}\n'

        await message.answer(text)
    else:
        await message.answer('В этом чате нет модераторов')
