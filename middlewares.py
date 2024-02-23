from vkbottle import BaseMiddleware
from vkbottle.bot import Message
from models import Member
from config import ADMIN_ID
from loguru import logger


class BaseCheckCommand(BaseMiddleware[Message]):
    COMMANDS = ()
    COMMANDS_ARGUMENT = ()
    COMMANDS_MENTION_FOR_ALL = ()
    COMMANDS_MENTION_WITHOUT_MODER = ()
    COMMANDS_REPLY_WITHOUT_MODER = ()

    @staticmethod
    async def get_member_from_mention(mention: str) -> Member | None:
        try:
            mention = mention.split("|")
            member_id = int(mention[0][3:])
            logger.info(member_id)
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
        elif command in self.COMMANDS_REPLY_WITHOUT_MODER:
            reply = self.event.reply_message
            member = await Member.get(vk_id=reply.from_id)
            if member.role == "member":
                self.send({"member": member})
                return
        elif command in self.COMMANDS:
            logger.info("standart command")
            return
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
    COMMANDS = ("help", "removenick", "nlist", "nonick", "warnlist", "muted", "banlist", "staff", "onlinelist", "zov", "online")
    COMMANDS_ARGUMENT = ("setnick", "getacc")
    COMMANDS_MENTION_FOR_ALL = ("getnick", "warnhistory")
    COMMANDS_MENTION_WITHOUT_MODER = ("kick", "unwarn", "getwarn", "mute", "unmute", "ban", "unban")
    COMMANDS_REPLY_WITHOUT_MODER = ("warn",)

    async def pre(self):
        if (await Member.get(vk_id=self.event.from_id)).role == "moder":
            await self.default_check()
        else:
            logger.info("user hasn't privilege")
            self.stop()
