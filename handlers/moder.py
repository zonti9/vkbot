from vkbottle.bot import BotLabeler, Message, rules
from models import Member

moder_labeler = BotLabeler()
moder_labeler.auto_rules = [rules.PeerRule(from_chat=True)]


@moder_labeler.message(text="/setnick <nick>")
async def setnick_handler(message: Message, nick: str):
    member = await Member.get(vk_id=message.from_id)
    member.nick = nick
    await member.save()


@moder_labeler.message(command=("removenick", 1))
async def setnick_handler(message: Message):
    member = await Member.get(vk_id=message.from_id)
    member.nick = None
    await member.save()


@moder_labeler.message(command=("kick", 1))
async def kick_handler(message: Message, member: Member, name: str):
    await message.ctx_api.messages.remove_chat_user(chat_id=message.chat_id, member_id=member.vk_id)
    await message.answer(f"{name} был исключен из чата")


@moder_labeler.message(command=("warn", 1))
async def warn_handler(message: Message, member: Member, name: str):
    member.warns += 1
    await member.save()
    await message.answer(f"{name} получил {member.warns} предупреждение")

    if member.warns >= 3:
        await message.ctx_api.messages.remove_chat_user(message.chat_id, member.vk_id)
        await message.answer(f"{name} превысел лимит предупреждений и был исключен из чата")


@moder_labeler.message(command=("unwarn", 1))
async def unwarn_handler(message: Message, member: Member, name: str):
    member.warns = 0
    await member.save()
    await message.answer(f"{name} избавлен от предупреждений")


@moder_labeler.message(command=("getwarn", 1))
async def getwarn_handler(message: Message, member: Member, name: str):
    if member.warns:
        await message.answer(f"У {name} {member.warns} предупреждений")
    else:
        await message.answer(f"У {name} нет предупреждений")


@moder_labeler.message(command=("mute", 1))
async def mute_handler(message: Message, member: Member, name: str):
    member.mute = True
    await member.save()
    await message.answer(f"{name} больше не может отправлять сообщения")


@moder_labeler.message(command="warnlist")
async def warnlist_handler(message: Message):
    warnlist = await Member.filter(warns__not=0)

    if warnlist:
        text = "Пользователи с предупреждениями:\n"
        text += "\n".join([member.nick for member in warnlist])
        await message.answer(text)
    else:
        await message.answer("Нет пользователей с предупреждениями")


@moder_labeler.message(command=("unmute", 1))
async def unmute_handler(message: Message, member: Member, username: str):
    member.mute = False
    await member.save()
    nick = username or member.nick
    await message.answer(f"{nick} снова может отправлять сообщения")


@moder_labeler.message(command="muted")
async def muted_handler(message: Message):
    muted = await Member.filter(mute=True)
    if muted:
        text = "Пользователи в муте:\n"
        for member in muted:
            text += f"{member.nick}\n"
        await message.answer(text)
    else:
        await message.answer("В этом чате нет пользователей в муте")


@moder_labeler.message(command=("ban", 1))
async def ban_handler(message: Message, member: Member, username: str):
    member.ban = True
    await member.save()
    nick = username or member.nick
    await message.ctx_api.messages.remove_chat_user(chat_id=message.chat_id, member_id=member.vk_id)
    await message.answer(f"{nick} был заблокирован")


@moder_labeler.message(command=("unban", 1))
async def unban_handler(message: Message, member: Member):
    member.ban = False
    await member.save()
    await message.answer(f"{member.nick} был разблокирован")


@moder_labeler.message(command="banlist")
async def banlist_handler(message: Message):
    banlist = await Member.filter(ban=True)
    if banlist:
        text = "Заблокированные пользователи:\n"
        text += "\n".join([member.nick for member in banlist])
        await message.answer(text)
    else:
        await message.answer("В этом чате нет заблокированных пользователей")


@moder_labeler.message(command="staff")
async def staff_handler(message: Message):
    staff = await Member.filter(role="moder")
    if staff:
        text = "Модераторы чата:\n"
        text += "\n".join([member.nick for member in staff])
        await message.answer(text)
    else:
        await message.answer("В этом чате нет модераторов")


@moder_labeler.message(command="zov")
async def zov_handler(message: Message):
    members = await Member.filter(vk_id__not=message.from_id)
    if members:
        text = ", ".join([f"[id{member.vk_id}|{member.nick}]" for member in members])
        await message.answer(text)
    else:
        await message.answer("В этом чате нет пользователей")


@moder_labeler.message(command="online")
async def online_handler(message: Message):
    members = await Member.filter(vk_id__not=message.from_id)
    member_ids = [member.vk_id for member in members]
    online_users = await message.ctx_api.users.get(user_ids=member_ids, fields=["online"])
    online_user_ids = [user.id for user in online_users if user.online]
    online_members = [member for member in members if member.vk_id in online_user_ids]

    if online_members:
        await message.answer(", ".join([f"[id{member.vk_id}|{member.nick}]" for member in online_members]))
    else:
        await message.answer("Нет пользователей в сети")


@moder_labeler.message(command="onlinelist")
async def onlinelist_hadler(message: Message):
    members = await Member.filter(vk_id__not=message.from_id)
    member_ids = [member.vk_id for member in members]
    online_users = await message.ctx_api.users.get(user_ids=member_ids, fields=["online"])
    online_user_ids = [user.id for user in online_users if user.online]
    online_members = [member for member in members if member.vk_id in online_user_ids]

    if online_members:
        text = "Пользователи онлайн:\n"
        text += "\n".join([member.nick for member in online_members])
        await message.answer(text)
    else:
        await message.answer("Нет пользователей в сети")
