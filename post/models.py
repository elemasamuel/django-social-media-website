from django.db import models
from django.contrib.auth.models import User
import uuid
from django.db.models.signals import post_save, post_delete
from django.utils.text import slugify
from django.urls import reverse
from mptt.models import MPTTModel, TreeForeignKey
from notifications.models import Notification

# Create your models here.

def user_directory_path(instance, filename):
    # this file will be uploaded to MEDIA_ROOT /user(id)/filename
    return 'user_{0}/{1}'.format(instance.user.id, filename)

class Tag(models.Model):
    title = models.CharField(max_length=75, verbose_name='Tag', null=True, blank=True)
    slug = models.SlugField(null=False, unique=True)

    class Meta:
        verbose_name_plural = 'Tags'

    def get_absolute_url(self):
        return reverse ('tags', args=[self.slug])

    # def get_absolute_url(self):
    #     return reverse('tags', args=[self.slug])

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)

class PostFileContent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='content_owner')
    file = models.FileField(upload_to=user_directory_path, null=True, blank=True)

class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.ManyToManyField(PostFileContent, related_name='contents', null=True, blank=True)
    caption = models.TextField(max_length=1500, verbose_name='Caption')
    posted = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag, related_name='tags', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, related_name='social_post')

    def __str__(self):
        return self.caption

    def get_absolute_url(self):
        return reverse('postdetails', args=[str(self.id)])

class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')

    def user_follow(sender, instance, *args, **kwargs):
        follow = instance
        sender = follow.follower
        following = follow.following

        notify = Notification(sender=sender, user=following, notification_type=3)
        notify.save()

    def user_unfollow(sender, instance, *args, **kwargs):
        follow = instance
        sender = follow.follower
        following = follow.following

        notify = Notification.objects.filter(sender=sender, user=following, notification_type=3)
        notify.delete()

class Stream(models.Model):
    following = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='stream_following')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    date = models.DateTimeField()

    def add_post(sender, instance, *args, **kwargs):
        post = instance
        user = post.user
        followers = Follow.objects.all().filter(following=user)
        for follower in followers:
            stream = Stream(post=post, user=follower.follower, date=post.posted, following=user)
            stream.save()

LIKE_CHOICES = (
    ('Like', 'Like'),
    ('Unlike', 'Unlike'),
)

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    value = models.CharField(choices=LIKE_CHOICES, default='Like', max_length=10)

    def __str__(self):
        return str(self.post)

    def user_liked_post(sender, instance, *args, **kwargs):
        like = instance
        post = like.post
        sender = like.user

        notify = Notification(post=post, sender=sender, user=post.user, notification_type=1)
        notify.save()

    def user_unlike_post(sender, instance, *args, **kwargs):
        like = instance
        post = like.post
        sender = like.user

        notify = Notification.objects.filter(post=post, sender=sender, notification_type=1)
        notify.delete()

#Comment
class Comment(MPTTModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True,)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    content = models.CharField(max_length=250, null=True)
    publish = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=True)

    class MPTTMeta:
        order_insertion_by = ["publish"]

    def __str__(self):
        return str(self.user)

    def user_comment_post(sender, instance, *args, **kwargs):
        comment = instance
        post = comment.post
        text_preview = comment.content[:90]
        sender = comment.user

        notify = Notification(post=post, sender=sender, user=post.user, text_preview=text_preview, notification_type=2)
        notify.save()

    def user_del_comment_post(sender, instance, *args, **kwargs):
        comment = instance
        post = comment.post
        sender = comment.user

        notify = Notification.objects.filter(post=post, user=post.user, sender=sender, notification_type=2)
        notify.delete()

class Story(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='story_user')
    content = models.FileField(upload_to=user_directory_path)
    expired = models.BooleanField(default=False)
    posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

class StoryStream(models.Model):
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='story_following')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    story = models.ManyToManyField(Story, related_name='stories')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.following.username + ' - ' + str(self.date)

    def add_post(sender, instance, *args, **kwargs):
        new_story = instance
        user = new_story.user
        followers = Follow.objects.all().filter(following=user)

        for follower in followers:
            try:
                s = StoryStream.objects.get(user=follower.follower, following=user)
            except StoryStream.DoesNotExist:
                s = StoryStream.objects.create(user=follower.follower, date=new_story.posted, following=user)
            s.story.add(new_story)
            s.save()

# Stream
post_save.connect(Stream.add_post, sender=Post)

# Likes Signals
post_save.connect(Like.user_liked_post, sender=Like)
post_delete.connect(Like.user_unlike_post, sender=Like)

# Follow Signals
post_save.connect(Follow.user_follow, sender=Follow)
post_delete.connect(Follow.user_unfollow, sender=Follow)

# Comment Signals
post_save.connect(Comment.user_comment_post, sender=Comment)
post_delete.connect(Comment.user_del_comment_post, sender=Comment)

# Story Stream
post_save.connect(StoryStream.add_post, sender=Story)




