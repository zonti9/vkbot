from vkbottle.bot import Bot
from tortoise import Tortoise
from models import Member
from config import TORTOISE_ORM, CHAT_ID


async def init_database(bot: Bot):
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas(safe=True)

    included_member_ids = [member.vk_id for member in await Member.all()]
    members = await bot.api.messages.get_conversation_members(peer_id=2000000000 + CHAT_ID)
    member_ids = [member.member_id for member in members.items]
    difference = [member_id for member_id in member_ids if member_id not in included_member_ids]
    users = await bot.api.users.get(user_ids=difference)

    for user in users:
        await Member.create(vk_id=user.id, name=user.first_name)
