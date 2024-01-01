from vkbottle import Bot

from config import api, state_dispenser
from custom_labeler import CustomLabeler

labeler = CustomLabeler()
bot = Bot(
    api=api,
    labeler=labeler,
    state_dispenser=state_dispenser
)

if __name__ == "__main__":
    bot.run_forever()
