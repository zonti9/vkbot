from vkbottle import BaseMiddleware
from vkbottle.bot import Message
from models import Member
from config import ADMIN_ID


async def get_member(mention: str) -> Member | None:
    if all(char in mention for char in "[|]") and ("id" in mention):
        mention = mention.split("|")

    member_id = int(mention[0][3:])
    if member_id:
        member = await Member.get_or_none(vk_id=member_id)
        return member


class AdminCommandMiddleware(BaseMiddleware[Message]):
    COMMANDS = ("addmoder", "removerole")

    async def pre(self):
        if self.event.from_id == ADMIN_ID:
            command = self.event.text.split()
            if command[0][1:] in self.COMMANDS:
                if len(command) == 2:
                    if member := await get_member(command[1]):
                        self.send({"member": member})
            else:
                self.stop()
        else:
            self.stop()


class ModerCommandMiddleware(BaseMiddleware[Message]):
    COMMANDS = ("kick", "warn", "unwarn", "getwarn", "mute", "unmute", "warnlist", "muted", "staff", "onlinelist",
                "zov", "online")

    async def pre(self):
        if (await Member.get(vk_id=self.event.from_id)).role == "moder":
            command = self.event.text.split()

            if command[0][1:] in self.COMMANDS:
                if len(command) == 2:
                    if member := await get_member(command[1]):
                        self.send({"member": member})
            else:
                self.stop()
        else:
            self.stop()
