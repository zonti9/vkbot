from vkbottle import Bot

from config import api, labeler, state_dispenser
from handlers import admin_labeler, moder_labeler

labeler.load(admin_labeler)
labeler.load(moder_labeler)

bot = Bot(
    api=api,
    labeler=labeler,
    state_dispenser=state_dispenser
)

bot.run_forever()
