# Generated by Django 4.0.5 on 2022-06-18 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0010_alter_profile_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='picture',
            field=models.ImageField(blank=True, default='static/images/user-8.png', null=True, upload_to='user_directory_path', verbose_name='Picture'),
        ),
    ]