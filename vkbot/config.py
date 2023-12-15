from vkbottle import API, BuiltinStateDispenser
from vkbottle.bot import BotLabeler

from db import DbWork
from private import TOKEN, db_config


api = API(TOKEN)
labeler = BotLabeler()
state_dispenser = BuiltinStateDispenser()

db_con = DbWork(*db_config.values())
command_temp = ' [id<member_id>|<member_name>]'
