from vkbottle.dispatch import BaseMiddleware
from vkbottle.bot import rules, Message
from vkbottle.dispatch.views.bot import BotMessageView
from vkbottle.dispatch.handlers import FromFuncHandler

from config import db_con, command_temp


class AdminView(BotMessageView):
    pass


class CheckAdminMessage(BaseMiddleware[Message]):
    admin_coms = ("/addmoder", "/removerole")

    async def pre(self):
        if self.event.text.split()[0] not in self.admin_coms:
            self.stop()

        members = await self.event.ctx_api.messages.get_conversation_members(peer_id=2000000000 + self.event.chat_id)
        admin = list(filter(lambda member: member.member_id == self.event.from_id, members.items))[0].is_admin

        if not admin:
            self.stop()


async def add_moder_handler(message: Message, member_id: int, member_name: str):
    await db_con.set_user_field(member_id, "moderator", True)
    await message.answer(f"{member_name} теперь модератор чата")


async def remove_role_handler(message: Message, member_id: int, member_name: str):
    await db_con.set_user_field(member_id, "moderator", False)
    await message.answer(f"{member_name} больше не является модератором чата")


admin_view = AdminView()
admin_view.register_middleware(CheckAdminMessage)
admin_view.handlers = [
    FromFuncHandler(add_moder_handler, rules.VBMLRule("/addmoder" + command_temp)),
    FromFuncHandler(remove_role_handler, rules.VBMLRule("/removerole" + command_temp))
]
