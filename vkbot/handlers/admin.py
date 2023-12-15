from vkbottle.bot import BotLabeler, Message, rules

from vkbot.config import db_con, command_temp


class AdminRule(rules.ABCRule[Message]):
    async def check(self, message: Message) -> bool:
        members = await message.ctx_api.messages.get_conversation_members(peer_id=2000000000 + message.chat_id)
        admin = list(filter(lambda member: member.member_id == message.from_id, members.items))[0].is_admin
        return admin


admin_labeler = BotLabeler()
admin_labeler.auto_rules = [rules.PeerRule(from_chat=True), AdminRule()]


@admin_labeler.message(text='/addmoder' + command_temp)
async def add_moder_handler(message: Message, member_id: int, member_name: str):
    await db_con.set_user_field(member_id, 'moderator', True)
    await message.answer(f'{member_name} теперь модератор чата')


@admin_labeler.message(text='/removerole' + command_temp)
async def remove_role_handler(message: Message, member_id: int, member_name: str):
    await db_con.set_user_field(member_id, 'moderator', False)
    await message.answer(f'{member_name} больше не является модератором чата')
