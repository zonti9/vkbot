from vkbottle.bot import BotLabeler, Message, rules
from vkbottle.dispatch import ABCRule
from models import Member

member_labeler = BotLabeler()


class MutedMemberRule(ABCRule[Message]):
    async def check(self, event: Message) -> bool:
        member = await Member.get_or_none(vk_id=event.from_id)
        if member.mute:
            return True
        return False


@member_labeler.chat_message(MutedMemberRule())
async def delete_message(message: Message):
    message_id = (await message.ctx_api.messages.get_by_conversation_message_id(
        peer_id=2000000000 + message.chat_id,
        conversation_message_ids=message.conversation_message_id
    )).items[0].id
    await message.ctx_api.messages.delete(message_ids=message_id, delete_for_all=True)


@member_labeler.chat_message(rules.ChatActionRule([
    "chat_invite_user",
    "chat_invite_user_by_link",
    "chat_invite_user_by_message_request"
]))
async def create_member(message: Message):
    member = await Member.get_or_none(vk_id=message.action.member_id)
    if member:
        if member.ban:
            await message.ctx_api.messages.remove_chat_user(chat_id=message.chat_id, member_id=member.vk_id)
    else:
        user = (await message.ctx_api.users.get(user_ids=[message.action.member_id]))[0]
        await Member.create(vk_id=user.id, nick=user.screen_name or user.first_name)
