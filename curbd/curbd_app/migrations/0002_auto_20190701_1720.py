# Generated by Django 2.2.2 on 2019-07-01 17:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('curbd_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='const',
            field=models.FloatField(default=0),
        ),
    ]
