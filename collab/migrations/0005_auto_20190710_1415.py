# Generated by Django 2.2 on 2019-07-10 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collab', '0004_auto_20190710_1325'),
    ]

    operations = [
        migrations.AlterField(
            model_name='featuretype',
            name='slug',
            field=models.SlugField(max_length=256, unique=True, verbose_name='Slug'),
        ),
    ]