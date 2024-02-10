from vkbottle import BaseMiddleware
from vkbottle.bot import Message
from models import Member
from config import ADMIN_ID
from loguru import logger


class BaseCheckCommand(BaseMiddleware[Message]):
    COMMANDS: tuple
    COMMANDS_ARGUMENT: tuple
    COMMANDS_MENTION_FOR_ALL: tuple
    COMMANDS_MENTION_WITHOUT_MODER: tuple

    @staticmethod
    async def get_member_from_mention(mention: str) -> Member | None:
        if all(char in mention for char in "[|]") and ("id" in mention):
            mention = mention.split("|")
        try:
            member_id = int(mention[0][3:])
            member = await Member.get_or_none(vk_id=member_id)
        except Exception:
            member = None
        return member

    async def default_check(self):
        split_text = self.event.text.split()
        command = split_text[0][1:]
        logger.info(command)
        if len(split_text) == 2:
            member = await self.get_member_from_mention(split_text[1])
            if member:
                if command in self.COMMANDS_MENTION_FOR_ALL:
                    logger.info("for all")
                    self.send({"member": member})
                    return
                elif command in self.COMMANDS_MENTION_WITHOUT_MODER:
                    logger.info("except moder")
                    member = await self.get_member_from_mention(command[1])
                    if member and member.role == "member":
                        logger.info("he isn't moder")
                        if not member.nick:
                            username = (await self.event.ctx_api.users.get(user_ids=member.vk_id))[0].first_name
                            member.name = username
                            await member.save()
                            logger.info("name was updated")
                        self.send({"member": member})
                        return
            elif command in self.COMMANDS_ARGUMENT:
                logger.info("command with argument")
                return
        elif command in self.COMMANDS:
            logger.info("standart command")
            return
        await self.event.answer("Ошибка синтаксиса в команде")
        self.stop()


class AdminCommandMiddleware(BaseCheckCommand):
    COMMANDS_MENTION_WITHOUT_MODER = ("addmoder", "removerole")

    async def pre(self):
        if self.event.from_id == ADMIN_ID:
            await self.default_check()
        else:
            logger.info("user hasn't privilege")
            self.stop()


class ModerCommandMiddleware(BaseCheckCommand):
    COMMANDS = ("help", "removenick", "warnlist", "muted", "banlist", "staff", "onlinelist", "zov", "online")
    COMMANDS_ARGUMENT = ("setnick", "getacc")
    COMMANDS_MENTION_FOR_ALL = ("getnick",)
    COMMANDS_MENTION_WITHOUT_MODER = ("kick", "warn", "unwarn", "getwarn", "mute", "unmute", "ban", "unban")

    async def pre(self):
        if (await Member.get(vk_id=self.event.from_id)).role == "moder":
            await self.default_check()
        else:
            logger.info("user hasn't privilege")
            self.stop()
