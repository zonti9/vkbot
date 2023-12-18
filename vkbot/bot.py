from vkbottle import Bot

from config import api, state_dispenser
from custom_labeler import CustomLabeler

labeler = CustomLabeler()
bot = Bot(
    api=api,
    labeler=labeler,
    state_dispenser=state_dispenser
)
bot.run_forever()
