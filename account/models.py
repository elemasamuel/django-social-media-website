from email.policy import default
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from post.models import Post
from django.urls import reverse
from PIL import Image
from django.conf import settings
import os


# Create your models here.

# Save Folder
def user_directory_path(instance, filename):
    # this file will be uploaded to MEDIA_ROOT /user(id)/filename
    profile_pic_name = 'user_{0}/profile.jpg'.format(instance.user.id)
    full_path = os.path.join(settings.MEDIA_ROOT, profile_pic_name)

    if os.path.exists(full_path):
        os.remove(full_path)
    return profile_pic_name

class Profile(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=250, null=True, blank=True)
    last_name = models.CharField(max_length=250, null=True, blank=True)
    email = models.CharField(max_length=250, null=True, blank=True)
    phone = models.PositiveIntegerField(null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    website = models.CharField(max_length=80, null=True, blank=True)
    profile_info = models.TextField(max_length=150, null=True, blank=True)
    created = models.DateField(auto_now_add=True)
    favorites = models.ManyToManyField(Post)
    picture = models.ImageField(null=True, blank=True, verbose_name='Picture', upload_to='user_directory_path')
    cover_photo = models.ImageField(null=True, blank=True, verbose_name='Photo', upload_to='cover_photo/')

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.user.username

    # Image Resize
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        SIZE = 200, 200

        if self.picture:
            pic = Image.open(self.picture.path)
            pic.thumbnail(SIZE, Image.LANCZOS)
            pic.save(self.picture.path)





