from django.db import models
from accounts.models import Account
from enum import Enum
from enumfields import EnumIntegerField


class MessageType(Enum):
    INFORM = 0
    ACCEPT = 1
    REJECT = -1


class LogMessage(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    message = models.CharField(max_length=512)
    type = EnumIntegerField(MessageType, default=MessageType.INFORM)
