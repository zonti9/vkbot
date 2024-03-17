from vkbottle.bot import BotLabeler, Message, rules
from models import Member, Warn

moder_labeler = BotLabeler()
moder_labeler.auto_rules = [rules.PeerRule(from_chat=True)]


@moder_labeler.message(command="help")
async def help_handler(message: Message):
    await message.answer(
        """
        Команды модераторов:
        /kick <упоминание пользователя> — исключить пользователя из беседы
        /mute <упоминание пользователя> — замутить пользователя
        /unmute <упоминание пользователя> — размутить пользователя
        /warn — выдать предупреждение пользователю (отправлять ответом на сообщение, за которое выдается предупреждение)
        /unwarn <упоминание пользователя> — снять предупреждение пользователю
        /getwarn <упоминание пользователя> — информация о активных предупреждениях пользователя
        /staff — пользователи с ролями
        /setnick <ник> — сменить ник у пользователя
        /removenick — очистить ник у пользователя
        /nlist — посмотреть ники пользователей
        /nonick — пользователи без ников
        /getnick <упоминание пользователя> — проверить ник пользователя
        /getacc <ник> — узнать пользователя по нику
        /warnlist — список пользователей с варном
        /ban <упоминание пользователя> — заблокировать пользователя в беседе
        /unban <упоминание пользователя> — разблокировать пользователя в беседе
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
        await message.answer(f"Пользователь {member.mention(False)} изменил ник на {member.nick}")


@moder_labeler.message(text="/getacc <nick>")
async def getacc_handler(message: Message, nick: str):
    member = await Member.get_or_none(nick=nick)
    if member:
        await message.answer(f"Пользователь с ником {member.nick} - это {member.mention(False)}")
    else:
        await message.answer("Нет пользователей с таким ником")


@moder_labeler.message(command="removenick")
async def removenick_handler(message: Message):
    member = await Member.get(vk_id=message.from_id)
    member.nick = ""
    await member.save()
    await message.answer(f"Пользователь {member.mention(True)} удалил свой ник")


@moder_labeler.message(command=("getnick", 1))
async def getnick_handler(message: Message, member: Member):
    mention = member.mention(False)
    if member.nick:
        await message.answer(f"Ник пользователя {mention}: {member.nick}")
    else:
        await message.answer(f"У пользователя {mention} нет ника")


@moder_labeler.message(command="nlist")
async def nlist_handler(message: Message):
    moders_with_nick = await Member.filter(nick__not="", role="moder")
    if moders_with_nick:
        text = "Модератор - ник:\n"
        text += "\n".join([moder.mention(True) for moder in moders_with_nick])
        await message.answer(text)
    else:
        await message.answer("В этом чате нет модераторов с ником")


@moder_labeler.message(command="nonick")
async def nonick_handler(message: Message):
    moders_without_nick = await Member.filter(nick="", role="moder")
    if moders_without_nick:
        text = "Модераторы без ника:\n"
        text += "\n".join([moder.mention(True) for moder in moders_without_nick])
        await message.answer(text)
    else:
        await message.answer("В этом чате все модераторы с ником")


@moder_labeler.message(command=("kick", 1))
async def kick_handler(message: Message, member: Member):
    await message.ctx_api.messages.remove_chat_user(chat_id=message.chat_id, member_id=member.vk_id)
    await message.answer(f"Пользователь {member.mention(True)} был исключен из чата")


@moder_labeler.message(command="warn")
async def warn_handler(message: Message, member: Member):
    reply = message.reply_message
    await Warn.create(member_id=reply.from_id, message=reply.text)
    active = len(await member.warns.filter(active=True))
    mention = member.mention(True)
    await message.answer(f"Пользователь {mention} получил {active} предупреждение")

    if active >= 3:
        await message.ctx_api.messages.remove_chat_user(message.chat_id, member.vk_id)
        await message.answer(f"{mention} превысел лимит предупреждений и был исключен из чата")


@moder_labeler.message(command=("unwarn", 1))
async def unwarn_handler(message: Message, member: Member):
    active_warns = await member.warns.filter(active=True)
    for warn in active_warns:
        warn.active = False
        await warn.save()
    await message.answer(f"Пользователь {member.mention(True)} избавлен от предупреждений")


@moder_labeler.message(command=("getwarn", 1))
async def getwarn_handler(message: Message, member: Member):
    mention = member.mention(True)
    active = ""
    for i, warn in enumerate(await member.warns.filter(active=True), start=1):
        active += f"{i}) сообщение: {warn.message}\n"
    if active:
        await message.answer(f"Активные предупреждения пользователя {mention}:\n{active}")
    else:
        await message.answer(f"У пользователя {mention} нет активных предупреждений")


@moder_labeler.message(command=("warnhistory", 1))
async def warnhistory_handler(message: Message, member: Member):
    total_count = len(await member.warns)
    mention = member.mention(True)
    if total_count:
        inactive = ""
        for i, warn in enumerate(await member.warns.filter(active=False), start=1):
            inactive += f"{i}) сообщение: {warn.message}\n"
        active = ""
        for i, warn in enumerate(await member.warns.filter(active=True), start=1):
            active += f"{i}) сообщение: {warn.message}\n"
        await message.answer(f"История предупреждений пользователя {mention}:\n"
                             f"Неактивных предупреждений:\n{inactive}"
                             f"Активные предупреждения:\n{active}")
    else:
        await message.answer(f"У пользователя {mention} нет и не было предупреждений")


@moder_labeler.message(command="warnlist")
async def warnlist_handler(message: Message):
    warned_members = await Member.filter(warns__not=0)
    warnlist = [member for member in set(warned_members) if await member.warns.filter(active=True)]

    if warnlist:
        text = "Пользователи с предупреждениями:\n"
        text += "\n".join([member.mention(True) for member in warnlist])
        await message.answer(text)
    else:
        await message.answer("Нет пользователей с предупреждениями")


@moder_labeler.message(command=("mute", 1))
async def mute_handler(message: Message, member: Member):
    member.mute = True
    await member.save()
    await message.answer(f"Пользователь {member.mention(True)} больше не может отправлять сообщения")


@moder_labeler.message(command=("unmute", 1))
async def unmute_handler(message: Message, member: Member):
    member.mute = False
    await member.save()
    await message.answer(f"{member.mention(True)} снова может отправлять сообщения")


@moder_labeler.message(command="muted")
async def muted_handler(message: Message):
    muted = await Member.filter(mute=True)
    if muted:
        text = "Пользователи в муте:\n"
        text += "\n".join([member.mention(True) for member in muted])
        await message.answer(text)
    else:
        await message.answer("В этом чате нет пользователей в муте")


@moder_labeler.message(command=("ban", 1))
async def ban_handler(message: Message, member: Member):
    member.ban = True
    await member.save()
    await message.ctx_api.messages.remove_chat_user(chat_id=message.chat_id, member_id=member.vk_id)
    await message.answer(f"Пользователь {member.mention(True)} был заблокирован")


@moder_labeler.message(command=("unban", 1))
async def unban_handler(message: Message, member: Member):
    member.ban = False
    await member.save()
    await message.answer(f"Пользователь {member.mention(True)} был разблокирован")


@moder_labeler.message(command="banlist")
async def banlist_handler(message: Message):
    banlist = await Member.filter(ban=True)
    if banlist:
        text = "Заблокированные пользователи:\n"
        text += "\n".join([member.mention(True) for member in banlist])
        await message.answer(text)
    else:
        await message.answer("В этом чате нет заблокированных пользователей")


@moder_labeler.message(command="staff")
async def staff_handler(message: Message):
    staff = await Member.filter(role="moder")
    if staff:
        text = "Модераторы чата:\n"
        text += "\n".join([member.mention(True) for member in staff])
        await message.answer(text)
    else:
        await message.answer("В этом чате нет модераторов")


@moder_labeler.message(command="zov")
async def zov_handler(message: Message):
    members = await Member.filter(vk_id__not=message.from_id)
    if members:
        text = "\n".join([member.mention(True) for member in members])
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
        text = "\n".join([member.mention(True) for member in online_members])
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
