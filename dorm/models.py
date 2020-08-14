from django.db import models
from accounts.models import Account
from enum import Enum
from enumfields import EnumIntegerField


class Room(models.Model):
    block_number = models.IntegerField(max_length=10)
    room_number = models.IntegerField(max_length=10)
    capacity = models.IntegerField(max_length=10)

    def __str__(self):
        return str(self.block_number) + "-" + str(self.room_number)


class RelationStateType(Enum):
    NONE = -1
    OK = 1
    PENDING = 2
    UNKNOWN = 3


class StateType(Enum):
    NONE = -1
    OK = 1
    PENDING = 2


class Room_User(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE, unique=True)
    user_state = EnumIntegerField(StateType, default=StateType.NONE)

    # class Meta:
    #     unique_together = (("room", "user"),)


class UserRelationsInRoom(models.Model):
    user1 = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="user1")
    user2 = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="user2")
    user1_to_user2_state = EnumIntegerField(RelationStateType, default=RelationStateType.NONE)

    class Meta:
        unique_together = (("user1", "user2"),)
