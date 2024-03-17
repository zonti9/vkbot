from os import getenv
from typing import Dict

from vkbottle import Bot
from vkbottle.bot import BotLabeler
from vkbottle.dispatch.views.bot import BotMessageView

from tortoise import Tortoise, run_async

from models import Member
from middlewares import AdminCommandMiddleware, ModerCommandMiddleware
from handlers import admin_labeler, moder_labeler, member_labeler
from config import TOKEN


async def init_database():
    await Tortoise.init(db_url="sqlite://db.sqlite3",
                        modules={"models": ["models"]})
    await Tortoise.generate_schemas(safe=True)

    included_member_ids = [member.vk_id for member in await Member.all()]
    members = await bot.api.messages.get_conversation_members(peer_id=2000000000 + int(getenv("CHAT_ID")))
    member_ids = [member.member_id for member in members.items]
    difference = [member_id for member_id in member_ids if member_id not in included_member_ids]
    users = await bot.api.users.get(user_ids=difference)

    for user in users:
        await Member.create(vk_id=user.id, name=user.first_name)


admin_view = BotMessageView()
admin_view.register_middleware(AdminCommandMiddleware)
admin_view.handlers = admin_labeler.message_view.handlers

moder_view = BotMessageView()
moder_view.register_middleware(ModerCommandMiddleware)
moder_view.handlers = moder_labeler.message_view.handlers

member_view = BotMessageView()
member_view.handlers = member_labeler.message_view.handlers


class CustomLabeler(BotLabeler):
    def views(self) -> Dict[str, "BotMessageView"]:
        return {
            "admin_view": admin_view,
            "moder_view": moder_view,
            "member_view": member_view,
        }


bot = Bot(token=TOKEN, labeler=CustomLabeler())

if __name__ == "__main__":
    run_async(init_database())
    bot.run_forever()
