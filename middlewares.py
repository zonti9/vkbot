from vkbottle import BaseMiddleware
from vkbottle.bot import Message
from models import Member
from config import ADMIN_ID


async def get_member(mention: str) -> Member | None:
    if all(char in mention for char in "[|]") and ("id" in mention):
        mention = mention.split("|")

    member_id = int(mention[0][3:])
    member = await Member.get_or_none(vk_id=member_id)
    return member


class AdminCommandMiddleware(BaseMiddleware[Message]):
    COMMANDS = ("addmoder", "removerole")

    async def pre(self):
        if self.event.from_id == ADMIN_ID:
            command = self.event.text.split()
            if command[0][1:] in self.COMMANDS and len(command) == 2:
                member = await get_member(command[1])
                if member:
                    if member.nick:
                        self.send({"member": member, "name": member.nick})
                    else:
                        username = (await self.event.ctx_api.users.get(user_ids=member.vk_id)).items[0].first_name
                        self.send({"member": member, "name": username})
                    return
                self.event.answer("Такого пользователя нет в чате")
        self.stop()


class ModerCommandMiddleware(BaseMiddleware[Message]):
    COMMANDS_MENTION = ("kick", "warn", "unwarn", "getwarn", "mute", "unmute", "ban", "unban")
    COMMANDS = ("setnick", "removenick", "warnlist", "muted", "banlist", "staff", "onlinelist", "zov", "online")

    async def pre(self):
        if (await Member.get(vk_id=self.event.from_id)).role == "moder":
            command = self.event.text.split()
            if command[0][1:] in self.COMMANDS_MENTION and len(command) == 2:
                member = await get_member(command[1])
                if member:
                    if member.nick:
                        self.send({"member": member, "name": member.nick})
                    else:
                        username = (await self.event.ctx_api.users.get(user_ids=member.vk_id)).items[0].first_name
                        self.send({"member": member, "name": username})
                    return
                self.event.answer("Такого пользователя нет в чате")
            elif command[0][1:] in self.COMMANDS:
                return
        self.stop()
