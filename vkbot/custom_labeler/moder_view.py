from vkbottle.dispatch import BaseMiddleware
from vkbottle.bot import rules, Message
from vkbottle.dispatch.views.bot import BotMessageView
from vkbottle.dispatch.handlers import FromFuncHandler

from config import db_con, command_temp


class ModerView(BotMessageView):
    pass


class CheckModerMessage(BaseMiddleware[Message]):
    moder_coms = ("/kick", "/warn", "/unwarn", "/mute", "/unmute", "/warnlist", "/muted", "/staff", "/zov")

    async def pre(self):
        if self.event.text.split()[0] not in self.moder_coms:
            self.stop()

        moder = await db_con.get_user_field(self.event.from_id, "moderator")
        if moder:
            if len(self.event.text.split()) > 1:
                members = await self.event.ctx_api.messages.get_conversation_members(
                    peer_id=2000000000 + self.event.chat_id
                )
                member_id = int(self.event.text.split()[1].split("|")[0][3:])
                mention_admin = list(filter(lambda member: member.member_id == member_id, members.items))[0].is_admin
                mention_moder = await db_con.get_user_field(member_id, "moderator")

                if mention_admin or mention_moder:
                    self.stop()
        else:
            self.stop()


async def kick_handler(message: Message, member_id: int):
    await message.ctx_api.messages.remove_chat_user(message.chat_id, member_id)


async def warn_handler(message: Message, member_id: int, member_name: str):
    warns = await db_con.get_user_field(member_id, "warns")
    warns += 1
    await db_con.set_user_field(member_id, "warns", warns)

    await message.answer(f"{member_name} получил {warns} предупреждение")

    if warns >= 3:
        await message.ctx_api.messages.remove_chat_user(message.chat_id, member_id)


async def unwarn_handler(message: Message, member_id: int, member_name: str):
    await db_con.set_user_field(member_id, "warns", 0)
    await message.answer(f"{member_name} избавлен от предупреждений")


async def mute_handler(message: Message, member_id: int, member_name: str):
    await db_con.set_user_field(member_id, "mute", True)
    await message.answer(f"{member_name} больше не может отправлять сообщения")


async def unmute_handler(message: Message, member_id: int, member_name: str):
    await db_con.set_user_field(member_id, "mute", False)
    await message.answer(f"{member_name} снова может отправлять сообщения")


async def warnlist_handler(message: Message):
    warnlist = await db_con.get_users_with_warns()

    if warnlist:
        text = ""

        for member_id, warns in warnlist:
            member_name = (await message.ctx_api.users.get(user_ids=member_id))[0].first_name
            text += f"{member_name}: {warns}\n"

        await message.answer(text)
    else:
        await message.answer("Нет пользователей с предупреждениями")


async def muted_handler(message: Message):
    muted = await db_con.get_users_with_mute()

    if muted:
        text = "Пользователи в муте:\n"

        for member_id in muted:
            member_name = (await message.ctx_api.users.get(user_ids=member_id))[0].first_name
            text += f"{member_name}\n"

        await message.answer(text)
    else:
        await message.answer("В этом чате нет пользователей в муте")


async def staff_handler(message: Message):
    staff = await db_con.get_users_with_role()

    if staff:
        text = "Модераторы чата:\n"

        for member_id in staff:
            member_name = (await message.ctx_api.users.get(user_ids=member_id))[0].first_name
            text += f"{member_name}\n"

        await message.answer(text)
    else:
        await message.answer("В этом чате нет модераторов")


async def zov_handler(message: Message):
    members = await message.ctx_api.messages.get_conversation_members(peer_id=2000000000 + message.chat_id)
    text = ""

    for member in members.items:
        member_id = member.member_id

        if member_id > 0 and member_id != message.from_id:
            text += f"[id{member_id}|&]"

    await message.answer(text)


moder_view = ModerView()
moder_view.register_middleware(CheckModerMessage)
moder_view.handlers = [
    FromFuncHandler(kick_handler, rules.VBMLRule("/kick" + command_temp)),
    FromFuncHandler(warn_handler, rules.VBMLRule("/warn" + command_temp)),
    FromFuncHandler(unwarn_handler, rules.VBMLRule("/unwarn" + command_temp)),
    FromFuncHandler(mute_handler, rules.VBMLRule("/mute" + command_temp)),
    FromFuncHandler(unmute_handler, rules.VBMLRule("/unmute" + command_temp)),
    FromFuncHandler(warnlist_handler, rules.VBMLRule("/warnlist")),
    FromFuncHandler(muted_handler, rules.VBMLRule("/muted")),
    FromFuncHandler(staff_handler, rules.VBMLRule("/staff")),
    FromFuncHandler(zov_handler, rules.VBMLRule("/zov"))
]
