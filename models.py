from tortoise.models import Model
from tortoise import fields


class Member(Model):
    vk_id = fields.IntField(pk=True)
    nick = fields.CharField(max_length=255, default=None)
    role = fields.CharField(max_length=255, default="member")
    warns = fields.IntField(default=0)
    mute = fields.BooleanField(default=False)
    ban = fields.BooleanField(default=False)

    class Meta:
        table = "members"

    def __str__(self):
        return self.nick
