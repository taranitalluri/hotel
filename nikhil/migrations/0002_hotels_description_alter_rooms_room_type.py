# Generated by Django 5.1.3 on 2024-11-09 08:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nikhil', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='hotels',
            name='description',
            field=models.CharField(default='null', max_length=500000),
        ),
        migrations.AlterField(
            model_name='rooms',
            name='room_type',
            field=models.CharField(choices=[('1', 'Hotel'), ('2', 'Farm House')], max_length=50),
        ),
    ]