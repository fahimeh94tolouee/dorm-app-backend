# Generated by Django 3.1 on 2020-08-13 07:10

import accounts.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import enumfields.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(default='', max_length=50)),
                ('last_name', models.CharField(default='', max_length=50)),
                ('city', models.CharField(default='', max_length=50)),
                ('phone_number', models.CharField(default='', max_length=50)),
                ('major', models.CharField(default='', max_length=50)),
                ('religious_belief', enumfields.fields.EnumIntegerField(default=-1, enum=accounts.models.ReligiousBelief)),
                ('sleep_type', enumfields.fields.EnumIntegerField(default=-1, enum=accounts.models.SleepType)),
                ('clean_type', enumfields.fields.EnumIntegerField(default=-1, enum=accounts.models.CleanType)),
                ('noise_type', enumfields.fields.EnumIntegerField(default=-1, enum=accounts.models.NoiseType)),
                ('personality_type', enumfields.fields.EnumIntegerField(default=-1, enum=accounts.models.PersonalityType)),
                ('note', models.CharField(default='', max_length=255)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
