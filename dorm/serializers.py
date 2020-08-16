from rest_framework import serializers
from .models import Room, Room_User, UserRelationsInRoom
from accounts.serializers import AccountSerializer
from enumfields.drf.serializers import EnumSupportSerializerMixin


class RoomsSerializers(serializers.ModelSerializer):
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
