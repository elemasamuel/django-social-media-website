# Generated by Django 4.0.5 on 2022-06-21 19:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0012_alter_profile_favorites'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='picture',
            field=models.ImageField(blank=True, null=True, upload_to='user_directory_path', verbose_name='Picture'),
        ),
    ]
