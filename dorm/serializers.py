from rest_framework import serializers
from .models import Room, Room_User, UserRelationsInRoom, StateType
from accounts.serializers import AccountSerializer
from enumfields.drf.serializers import EnumSupportSerializerMixin


class RoomsSerializers(EnumSupportSerializerMixin, serializers.ModelSerializer):
    my_status = serializers.IntegerField(default=StateType.NONE.value)

    class Meta:
        model = Room
        fields = "__all__"


class Room_UserSerializers(EnumSupportSerializerMixin, serializers.ModelSerializer):
    user = AccountSerializer(read_only=True)

    class Meta:
        model = Room_User
        fields = "__all__"


class UserRelationsInRoomSerializers(EnumSupportSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = UserRelationsInRoom
        fields = "__all__"
