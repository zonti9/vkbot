from vkbottle.bot import Message
from vkbottle.dispatch.views.bot import BotMessageView
from vkbottle.dispatch.rules import ABCRule
from vkbottle.dispatch.handlers import FromFuncHandler

from config import db_con


class MemberView(BotMessageView):
    pass


class MemberMute(ABCRule[Message]):
    async def check(self, message: Message) -> bool:
        return bool(await db_con.get_user_field(message.from_id, "mute"))


async def check_mute(message: Message):
    message_id = (await message.ctx_api.messages.get_by_conversation_message_id(
        peer_id=2000000000 + message.chat_id,
        conversation_message_ids=message.conversation_message_id
    )).items[0].id
    await message.ctx_api.messages.delete(message_ids=[message_id], delete_for_all=True)


member_view = MemberView()
member_view.handlers = [
    FromFuncHandler(check_mute, MemberMute())
]
