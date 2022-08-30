# Django Imports
from django.urls import resolve, reverse
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.db.models import Q
from django.core.paginator import Paginator
from django.db import transaction
from django.template import loader
from django.shortcuts import get_object_or_404, render, redirect

# Account Imports
from account.forms import CreateUserForm, ProfileForm, ChangePasswordForm
from account.models import Profile
from account.serializers import UserSerializer, HyperUserSerializer

# Chat Imports
from chat.models import Message

# Post Imports
from post.models import Follow, Post, Stream

# Django Rest Framwork Imports
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

# Create your views here.

# Register
def registerPage(request):
    form = CreateUserForm()
    if request.user.is_authenticated:
        return redirect("/")
    else:
        if request.method == "POST":
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.save()

                username = form.cleaned_data.get("username")
                email = form.cleaned_data.get("email")
                first_name = form.cleaned_data.get("first_name")
                last_name = form.cleaned_data.get("last_name")
                
                Follow.objects.create(follower=user, following=user)
                group = Group.objects.get(name="customer")
                user.groups.add(group)
                Profile.objects.create(
                    user=user,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                )

                messages.info(request, "Account Created Successfully!")
                return redirect("login")
        return render(request, "account/register.html", {"form": form})

# Login
def loginPage(request):
    if request.user.is_authenticated:
        return redirect("/")
    else:
        if request.method == "POST":
            username = request.POST.get("username")
            password = request.POST.get("password1")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                messages.info(request, "Invalid Credentials")

        return render(request, "account/login.html", {})

# Logout
def logoutUser(request):
    logout(request)
    return redirect("login")

# Profile
@login_required(login_url="login")
def profile(request, username):
    user = get_object_or_404(
        User,
        username=username,
    )
    profile = Profile.objects.get(user=user)

    url_name = resolve(request.path).url_name

    if url_name == "profile":
        posts = Post.objects.filter(user=user).order_by("-posted")
    else:
        posts = profile.favorites.all()

    # Profile Info Stats
    posts_count = Post.objects.filter(user=user).count()
    following_count = Follow.objects.filter(follower=user).count()
    followers_count = Follow.objects.filter(following=user).count()

    # Check Follow Status
    follow_status = Follow.objects.filter(
        following=user, follower=request.user
    ).exists()

    context = {
        "profile": profile,
        "posts": posts,
        "url_name": url_name,
        "posts_count": posts_count,
        "followers_count": followers_count,
        "following_count": following_count,
        "follow_status": follow_status,
    }
    return render(request, "account/profile.html", context)

# Password Change
@login_required
def passwordChange(request):
	user = request.user
	if request.method == 'POST':
		form = ChangePasswordForm(request.POST)
		if form.is_valid():
			new_password = form.cleaned_data.get('new_password')
			user.set_password(new_password)
			user.save()
			update_session_auth_hash(request, user)
			return redirect('change_password_done')
	else:
		form = ChangePasswordForm(instance=user)

	context = {
		'form':form,
	}

	return render(request, 'account/change_password.html', context)

def passwordChangeDone(request):
	return render(request, 'account/change_password_done.html')

# Follow
@login_required(login_url="login")
def follow(request, username, option):
    user = request.user
    following = get_object_or_404(User, username=username)

    try:
        f, created = Follow.objects.get_or_create(
            follower=request.user, following=following
        )

        if int(option) == 0:
            f.delete()
            Stream.objects.filter(following=following, user=user).all().delete()
        else:
            posts = Post.objects.all().filter(user=following)[:10]

            with transaction.atomic():
                for post in posts:
                    stream = Stream(
                        post=post, user=user, date=post.posted, following=following
                    )
                    stream.save()
        return HttpResponseRedirect(reverse("profile", args=[username]))
    except User.DoesNotExist:
        return HttpResponseRedirect(reverse("profile", args=[username]))

# Settings
@login_required(login_url="login")
def settings(request):
    return render(request, "account/settings.html", {})

# Edit Profile
@login_required(login_url="login")
def editProfile(request):
    profile = request.user.profile
    form = ProfileForm(instance=profile)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()

    context = {
        "form": form,
    }
    return render(request, "account/edit-profile.html", context)

# Search User
@login_required(login_url="login")
def userSearch(request):
    query = request.GET.get("q")
    context = {}

    if query:
        users = User.objects.filter(Q(username__icontains=query))

        # Pagination
        paginator = Paginator(users, 100)
        page_number = request.GET.get("page")
        users_paginator = paginator.get_page(page_number)

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

        context = {
            "users": users_paginator,
            "directs": directs,
            "messages": messages,
            "active_direct": active_direct,
        }
    else:
        profiles = Profile.objects.all()

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

        context = {
            "profiles": profiles,
            "directs": directs,
            "messages": messages,
            "active_direct": active_direct,
        }
    template = loader.get_template("account/search-user.html")

    return HttpResponse(template.render(context, request))

# Start New Conversation
@login_required(login_url="login")
def newConversation(request, username):
    try:
        to_user = User.objects.get(username=username)
    except Exception as e:
        return redirect("user-search")

    return redirect("../chat/directs/" + username)

#
class GenericViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

#
class ProfileViewAPI(APIView):
    # Get all the Stream posts from the User
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        user = self.get_object(pk)
        profile = Profile.objects.get(user=user)
        serializer = HyperUserSerializer(profile, context={'request': request})
        return Response(serializer.data)
