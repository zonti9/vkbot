from vkbottle.bot import BotLabeler, Message, rules
from models import Member


admin_labeler = BotLabeler()
admin_labeler.auto_rules = [rules.PeerRule(from_chat=True)]


@admin_labeler.message(command=("addmoder", 1))
async def add_moder_handler(message: Message, member: Member):
    member.role = "moder"
    await member.save()
    await message.answer(f"{member.nick or member.name} теперь модератор чата")


@admin_labeler.message(command=("removerole", 1))
async def remove_role_handler(message: Message, member: Member):
    member.role = "member"
    await member.save()
    await message.answer(f"{member.nick or member.name} больше не является модератором чата")
