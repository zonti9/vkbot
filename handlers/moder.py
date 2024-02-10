from vkbottle.bot import BotLabeler, Message, rules
from models import Member

moder_labeler = BotLabeler()
moder_labeler.auto_rules = [rules.PeerRule(from_chat=True)]


@moder_labeler.message(command="help")
async def help_handler(message: Message):
    await message.answer(
        """
        Команды модераторов:
        /kick — исключить пользователя из беседы
        /mute — замутить пользователя
        /unmute — размутить пользователя
        /warn — выдать предупреждение пользователю
        /unwarn — снять предупреждение пользователю
        /getwarn — информация о активных предупреждениях пользователя
        /staff — пользователи с ролями
        /setnick — сменить ник у пользователя
        /removenick — очистить ник у пользователя
        /getnick — проверить ник пользователя
        /getacc — узнать пользователя по нику
        /warnlist — список пользователей с варном
        /ban — заблокировать пользователя в беседе
        /unban — разблокировать пользователя в беседе
        /zov — упомянуть всех пользователей
        /online — упомянуть пользователей онлайн
        /banlist — посмотреть заблокированных
        /onlinelist — посмотреть пользователей в онлайн
        """
    )


@moder_labeler.message(text="/setnick <nick>")
async def setnick_handler(message: Message, nick: str):
    if await Member.get_or_none(nick=nick):
        await message.answer("Пользователь с таким ником уже есть")
    else:
        member = await Member.get(vk_id=message.from_id)
        member.nick = nick
        await member.save()
        await message.answer(f"Пользователь {member.name} изменил ник на {member.nick}")


@moder_labeler.message(text="/getacc <nick>")
async def setnick_handler(message: Message, nick: str):
    member = await Member.get_or_none(nick=nick)
    if member:
        await message.answer(f"Пользователь с ником {member.nick} - это [id{member.vk_id}|{member.name}]")
    else:
        await message.answer("Нет пользователей с таким ником")


@moder_labeler.message(command="removenick")
async def setnick_handler(message: Message):
    member = await Member.get(vk_id=message.from_id)
    member.nick = ""
    await member.save()
    await message.answer(f"Пользователь {member.name} удалил свой ник")


@moder_labeler.message(command=("getnick", 1))
async def get_nick(message: Message, member: Member):
    await message.answer(f"Ник пользователя {member.name}: {member.nick}")


@moder_labeler.message(command=("kick", 1))
async def kick_handler(message: Message, member: Member):
    await message.ctx_api.messages.remove_chat_user(chat_id=message.chat_id, member_id=member.vk_id)
    await message.answer(f"Пользователь {member.nick or member.name} был исключен из чата")


@moder_labeler.message(command=("warn", 1))
async def warn_handler(message: Message, member: Member):
    member.warns += 1
    await member.save()
    name = member.nick or member.name
    await message.answer(f"Пользователь {name} получил {member.warns} предупреждение")

    if member.warns >= 3:
        await message.ctx_api.messages.remove_chat_user(message.chat_id, member.vk_id)
        await message.answer(f"{name} превысел лимит предупреждений и был исключен из чата")


@moder_labeler.message(command=("unwarn", 1))
async def unwarn_handler(message: Message, member: Member):
    member.warns = 0
    await member.save()
    await message.answer(f"Пользователь {member.nick or member.name} избавлен от предупреждений")


@moder_labeler.message(command=("getwarn", 1))
async def getwarn_handler(message: Message, member: Member):
    name = member.nick or member.name
    if member.warns:
        await message.answer(f"У пользователя {name} {member.warns} предупреждений")
    else:
        await message.answer(f"У пользователя {name} нет предупреждений")


@moder_labeler.message(command=("mute", 1))
async def mute_handler(message: Message, member: Member):
    member.mute = True
    await member.save()
    await message.answer(f"Пользователь {member.nick or member.name} больше не может отправлять сообщения")


@moder_labeler.message(command="warnlist")
async def warnlist_handler(message: Message):
    warnlist = await Member.filter(warns__not=0)

    if warnlist:
        text = "Пользователи с предупреждениями:\n"
        text += "\n".join([member.nick or member.name for member in warnlist])
        await message.answer(text)
    else:
        await message.answer("Нет пользователей с предупреждениями")


@moder_labeler.message(command=("unmute", 1))
async def unmute_handler(message: Message, member: Member):
    member.mute = False
    await member.save()
    await message.answer(f"{member.nick or member.name} снова может отправлять сообщения")


@moder_labeler.message(command="muted")
async def muted_handler(message: Message):
    muted = await Member.filter(mute=True)
    if muted:
        text = "Пользователи в муте:\n"
        for member in muted:
            text += f"{member.nick or member.name}\n"
        await message.answer(text)
    else:
        await message.answer("В этом чате нет пользователей в муте")


@moder_labeler.message(command=("ban", 1))
async def ban_handler(message: Message, member: Member):
    member.ban = True
    await member.save()
    await message.ctx_api.messages.remove_chat_user(chat_id=message.chat_id, member_id=member.vk_id)
    await message.answer(f"Пользователь {member.nick or member.name} был заблокирован")


@moder_labeler.message(command=("unban", 1))
async def unban_handler(message: Message, member: Member):
    member.ban = False
    await member.save()
    await message.answer(f"Пользователь {member.nick or member.name} был разблокирован")


@moder_labeler.message(command="banlist")
async def banlist_handler(message: Message):
    banlist = await Member.filter(ban=True)
    if banlist:
        text = "Заблокированные пользователи:\n"
        text += "\n".join([member.nick or member.name for member in banlist])
        await message.answer(text)
    else:
        await message.answer("В этом чате нет заблокированных пользователей")


@moder_labeler.message(command="staff")
async def staff_handler(message: Message):
    staff = await Member.filter(role="moder")
    if staff:
        text = "Модераторы чата:\n"
        text += "\n".join([member.nick or member.name for member in staff])
        await message.answer(text)
    else:
        await message.answer("В этом чате нет модераторов")


@moder_labeler.message(command="zov")
async def zov_handler(message: Message):
    members = await Member.filter(vk_id__not=message.from_id)
    if members:
        text = ", ".join([f"[id{member.vk_id}|{member.nick or member.name}]" for member in members])
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
        text = ""
        for member in online_members:
            text += f"[id{member.vk_id}|{member.nick or member.name}]"
        await message.answer(text[:-1])
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
        text += "\n".join([member.nick or member.name for member in online_members])
        await message.answer(text)
    else:
        await message.answer("Нет пользователей в сети")
