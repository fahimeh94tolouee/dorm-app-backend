from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Account
from django.core.validators import RegexValidator
from rest_framework.validators import UniqueValidator
from enumfields.drf.serializers import EnumSupportSerializerMixin


class SetCustomErrorMessagesMixin:
    """
    Replaces built-in validator messages with messages, defined in Meta class.
    This mixin should be inherited before the actual Serializer class in order to call __init__ method.

    Example of Meta class:

    >>> class Meta:
    >>>     model = User
    >>>     fields = ('url', 'username', 'email', 'groups')
    >>>     custom_error_messages_for_validators = {
    >>>         'username': {
    >>>             UniqueValidator: _('This username is already taken. Please, try again'),
    >>>             RegexValidator: _('Invalid username')
    >>>         }
    >>>     }
    """

    def __init__(self, *args, **kwargs):
        # noinspection PyArgumentList
        super(SetCustomErrorMessagesMixin, self).__init__(*args, **kwargs)
        self.replace_validators_messages()

    def replace_validators_messages(self):
        for field_name, validators_lookup in self.custom_error_messages_for_validators.items():
            # noinspection PyUnresolvedReferences
            for validator in self.fields[field_name].validators:
                if type(validator) in validators_lookup:
                    validator.message = validators_lookup[type(validator)]

    @property
    def custom_error_messages_for_validators(self):
        meta = getattr(self, 'Meta', None)
        return getattr(meta, 'custom_error_messages_for_validators', {})


class UserSerializer(SetCustomErrorMessagesMixin, serializers.ModelSerializer):
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        account = Account.objects.create(user=user)
        return user

    class Meta:
        model = User
        fields = ('id', 'username', 'password')
        extra_kwargs = {
            'password': {'write_only': True}
        }
        custom_error_messages_for_validators = {
            'username': {
                UniqueValidator: 'حسابی با این نام کاربری ثبت شده‌است. لطفا از قسمت ورود استفاده کنید.',
                RegexValidator: 'نام کاربری نامعتبر است.'
            }
        }

    def __init__(self, *args, **kwargs):
        super(UserSerializer, self).__init__(*args, **kwargs)
        self.fields["username"].error_messages["required"] = u"نام کاربری را وارد کنید."
        self.fields["username"].error_messages["blank"] = u"نام کاربری نمی‌تواند خالی باشد."
        # self.fields["email"].error_messages["required"] = u"email is required"
        # self.fields["email"].error_messages["blank"] = u"email cannot be blank"
        self.fields["password"].error_messages["min_length"] = u"password must be at least 8 chars"


class AccountSerializer(EnumSupportSerializerMixin, serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    first_name = serializers.CharField(
        required=False,
        max_length=50,
        error_messages={
            "blank": "نام نمی‌تواند خالی باشد.",
            "max_length": "نام نمی‌تواند از ۵۰ کاراکتر بیشتر باشد.",
        },
    )
    last_name = serializers.CharField(
        required=False,
        max_length=50,
        error_messages={
            "blank": "نام خانوادگی نمی‌تواند خالی باشد.",
            "max_length": "نام خانوادگی نمی‌تواند از ۵۰ کاراکتر بیشتر باشد.",
        },
    )

    class Meta:
        model = Account
        fields = "__all__"
        extra_kwargs = {
            'user': {'required': False},
            'note': {'allow_blank': True},
            'city': {'allow_blank': True},
            'major': {'allow_blank': True},
            'phone_number': {'allow_blank': True},
        }

