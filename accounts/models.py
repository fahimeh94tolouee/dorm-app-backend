from django.db import models
from enum import Enum
from django.contrib.auth.models import User
from enumfields import EnumField, EnumIntegerField


class ReligiousBelief(Enum):
    NONE = -1
    RELIGIOUS = 1
    NON_RELIGIOUS = 2
    NEITHER = 3


class SleepType(Enum):
    NONE = -1
    LIGHT_SENSITIVE = 1
    NOISE_SENSITIVE = 2
    BOTH = 3
    NEITHER = 4


class CleanType(Enum):
    NONE = -1
    SENSITIVE = 1
    NOT_IMPORTANT = 2


class NoiseType(Enum):
    NONE = -1
    SENSITIVE = 1
    NOT_IMPORTANT = 2


class PersonalityType(Enum):
    NONE = -1
    INTROVERT = 1
    EXTROVERT = 2


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, default="")
    last_name = models.CharField(max_length=50, default="")
    city = models.CharField(max_length=50, default="")
    phone_number = models.CharField(max_length=50, default="")
    major = models.CharField(max_length=50, default="")
    religious_belief = EnumIntegerField(ReligiousBelief, default=ReligiousBelief.NONE)
    sleep_type = EnumIntegerField(SleepType, default=SleepType.NONE)
    clean_type = EnumIntegerField(CleanType, default=CleanType.NONE)
    noise_type = EnumIntegerField(NoiseType, default=NoiseType.NONE)
    personality_type = EnumIntegerField(PersonalityType, default=PersonalityType.NONE)
    note = models.CharField(max_length=255, default="")
