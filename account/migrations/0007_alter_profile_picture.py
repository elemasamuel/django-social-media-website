# Generated by Django 4.0.5 on 2022-06-13 10:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0006_alter_profile_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='picture',
            field=models.ImageField(blank=True, null=True, upload_to='profile_pictures', verbose_name='Picture'),
        ),
    ]
