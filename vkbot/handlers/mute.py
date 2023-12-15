from vkbottle.bot import Message, rules

from vkbot.config import labeler, db_con


class MuteRule(rules.ABCRule[Message]):
    async def check(self, event: Message) -> bool:
        return bool(await db_con.get_user_field(event.from_id, 'mute'))


@labeler.chat_message(MuteRule())
async def message_handler(message: Message):
    message_id = (await message.ctx_api.messages.get_by_conversation_message_id(
        peer_id=2000000000 + message.chat_id,
        conversation_message_ids=message.conversation_message_id
    )).items[0].id
    await message.ctx_api.messages.delete(message_ids=[message_id], delete_for_all=True)
