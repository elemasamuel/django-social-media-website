# Generated by Django 4.0.5 on 2022-06-13 10:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0005_rename_location_profile_country_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='picture',
            field=models.ImageField(blank=True, default='static/images/profile-4.png', null=True, upload_to='profile_pictures', verbose_name='Picture'),
        ),
    ]
