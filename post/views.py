from django.shortcuts import redirect, get_object_or_404
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse

from post.models import Post, PostFileContent, Stream, Tag, Like, Story, StoryStream
from post.forms import NewPostForm, NewCommentForm, NewStoryForm
from post.serializers import StreamSerializer

from account.models import Profile

from chat.models import Message

from notifications.models import Notification

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

# Create your views here.

@login_required(login_url="login")
def index(request):
    #
    user = request.user
    posts = Stream.objects.filter(user=user)
    profiles = Profile.objects.all()

    group_ids = []

    for post in posts:
        group_ids.append(post.post_id)

    post_items = Post.objects.filter(id__in=group_ids).all().order_by("-posted")

    # Create Post
    users = request.user.id
    tags_objs = []
    files_objs = []

    if request.method == "POST":
        form = NewPostForm(request.POST, request.FILES)
        if form.is_valid():
            files = request.FILES.getlist('content')
            caption = form.cleaned_data.get("caption")
            tags_form = form.cleaned_data.get("tags")

            tags_list = list(tags_form.split(","))

            for tag in tags_list:
                t, created = Tag.objects.get_or_create(title=tag)
                tags_objs.append(t)

            for file in files:
                file_instance = PostFileContent(file=file, user=user)
                file_instance.save()
                files_objs.append(file_instance)

            p = Post.objects.create(caption=caption, user=user)
            p.content.set(files_objs)
            p.tags.set(tags_objs)
            p.save()
            return redirect("index")
    else:
        form = NewPostForm

    # Story
    stories = StoryStream.objects.filter(user=user)
    user = request.user
    file_objs = []

    if request.method == "POST":
        story_form = NewStoryForm(request.POST, request.FILES)
        if story_form.is_valid():
            file = request.FILES.get('content')

            story = Story(user=user, content=file)
            story.save()
            return redirect('index')
    else:
        story_form=NewStoryForm()

    # Notification
    user = request.user
    notifications = Notification.objects.filter(user=user).order_by('-date')
    Notification.objects.filter(user=user, is_seen=False).update(is_seen=False)

    # Chat
    messages = Message.get_messages(user=request.user)
    active_direct = 0
    directs = 0

    if messages:
        message = messages[0]
        active_direct = message["user"].username
        directs = Message.objects.filter(
            user=request.user, recipient=message["user"]
        )
        directs.update()

    template = loader.get_template("post/index.html")

    context = {
        "post_items": post_items,
        "form": form,
        "story_form": story_form,
        "stories": stories,
        "profiles": profiles,
        "notifications": notifications,
        "directs": directs,
        "messages": messages,
        "active_direct": active_direct,
    }

    return HttpResponse(template.render(context, request))


@login_required(login_url="login")
def tags(request, tag_slug):
    tag = get_object_or_404(Tag, slug=tag_slug)
    posts = Post.objects.filter(tags=tag).order_by("-posted")

    template = loader.get_template("post/tag.html")

    context = {
        "posts": posts,
        "tag": tag,
    }

    return HttpResponse(template.render(context, request))


@login_required(login_url="login")
def comment(request, post_id):
    # comments
    user = request.user
    profile = Profile.objects.get(user=user)
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.filter(status=True)

    user_comment = None

    if request.method == "POST":
        comment_form = NewCommentForm(request.POST)
        if comment_form.is_valid():
            user_comment = comment_form.save(commit=False)
            user_comment.user = request.user
            user_comment.post = post
            user_comment.save()
            return HttpResponseRedirect(request.path_info)
    else:
        comment_form = NewCommentForm()
    # end comment

    favorited = False

    if profile.favorites.filter(id=post_id).exists():
        favorited = True

    template = loader.get_template("post/comments.html")

    context = {
        "post": post,
        "comments": user_comment,
        "comments": comments,
        "comment_form": comment_form,
        "favorited": favorited,
    }

    return HttpResponse(template.render(context, request))


@login_required(login_url='login')
def like_post(request):
    user = request.user
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        post_obj = Post.objects.get(id=post_id)

        if user in post_obj.likes.all():
            post_obj.likes.remove(user)
        else:
            post_obj.likes.add(user)

        like, created = Like.objects.get_or_create(user=user, post_id=post_id)

        if not created:
            if like.value == 'Like':
                like.value = 'Unlike'
            else:
                like.value = 'Like'

        like.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required(login_url="login")
def favorite(request, post_id):
    user = request.user
    post = Post.objects.get(id=post_id)
    profile = Profile.objects.get(user=user)

    if profile.favorites.filter(id=post_id).exists():
        profile.favorites.remove(post)

    else:
        profile.favorites.add(post)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def showMedia(request, stream_id):
    stories = StoryStream.objects.get(id=stream_id)
    media_st = stories.story.all().values()

    stories_list = list(media_st)

    return JsonResponse(stories_list, safe=False)

class ListStream(APIView):
    # Get all the Stream posts from the User
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        user = self.get_object(pk)
        posts = Stream.objects.filter(user=user)
        serializer = StreamSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)

