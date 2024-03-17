from tortoise.models import Model
from tortoise import fields


class Member(Model):
    vk_id = fields.IntField(pk=True)
    nick = fields.CharField(max_length=255, default="")
    name = fields.CharField(max_length=255)
    role = fields.CharField(max_length=255, default="member")
    mute = fields.BooleanField(default=False)
    ban = fields.BooleanField(default=False)

    class Meta:
        table = "members"

    def __str__(self):
        return self.nick or self.name

    def mention(self, use_nick_if_exists: bool):
        if use_nick_if_exists:
            return f"[id{self.vk_id}|{self.nick or self.name}]"
        else:
            return f"[id{self.vk_id}|{self.name}]"


class Warn(Model):
    member = fields.ForeignKeyField("models.Member", related_name="warns", on_delete=fields.CASCADE)
    active = fields.BooleanField(default=True)
    message = fields.TextField()
    
    class Meta:
        table = "warns"
