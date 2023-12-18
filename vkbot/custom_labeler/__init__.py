from vkbottle.bot import BotLabeler
from vkbottle.dispatch.views.bot import BotMessageView
from typing import Dict

from .admin_view import admin_view
from .moder_view import moder_view
from .member_view import member_view


class CustomLabeler(BotLabeler):
    def views(self) -> Dict[str, 'BotMessageView']:
        # Из views должны быть возвращены все view которые
        # будут позже обрабатываться роутером
        return {
            'admin_view': admin_view,
            'moder_view': moder_view,
            'member_view': member_view
        }
