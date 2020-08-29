from rest_framework import serializers
from .models import LogMessage
from enumfields.drf.serializers import EnumSupportSerializerMixin


class LogMessageSerializers(EnumSupportSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = LogMessage
        fields = "__all__"
