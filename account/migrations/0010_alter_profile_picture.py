# Generated by Django 4.0.5 on 2022-06-17 20:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0009_alter_profile_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='picture',
            field=models.ImageField(blank=True, default='static/images/user-8.png', null=True, upload_to='profile_pictures', verbose_name='Picture'),
        ),
    ]
