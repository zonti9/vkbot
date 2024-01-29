from typing import Dict

from vkbottle import Bot
from vkbottle.bot import BotLabeler
from vkbottle.dispatch.views.bot import BotMessageView

from tortoise import run_async

from middlewares import AdminCommandMiddleware, ModerCommandMiddleware
from handlers import admin_labeler, moder_labeler, member_labeler
from db_methods import init_database
from config import TOKEN


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
    run_async(init_database(bot))
    bot.run_forever()
