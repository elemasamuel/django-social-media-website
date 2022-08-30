from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render, redirect
from chat.models import Message
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required(login_url="login")
def inbox(request):
    messages = Message.get_messages(user=request.user)
    active_direct = 0
    directs = 0

    if messages:
        message = messages[0]
        active_direct = message["user"].username
        directs = Message.objects.filter(user=request.user, recipient=message["user"])
        directs.update()

    context = {
        "directs": directs,
        "messages": messages,
        "active_direct": active_direct,
    }

    template = loader.get_template("chat/chat.html")

    return HttpResponse(template.render(context, request))


@login_required(login_url="login")
def directs(request, username):
    user = request.user
    messages = Message.get_messages(user=user)
    active_direct = username
    directs = Message.objects.filter(user=user, recipient__username=username)
    directs.update(is_read=True)

    message = 0

    for message in messages:
        if message["user"].username == username:
            message["unread"] = 0

    context = {
        "message": message,
        "directs": directs,
        "messages": messages,
        "active_direct": active_direct,
    }

    template = loader.get_template("chat/direct.html")

    return HttpResponse(template.render(context, request))


@login_required(login_url="login")
def sendDirect(request):
    from_user = request.user
    to_user_username = request.POST.get("to_user")
    body = request.POST.get("body")

    if request.method == "POST":
        to_user = User.objects.get(username=to_user_username)
        Message.send_message(from_user, to_user, body)
        return redirect("../directs/" + to_user_username)
    else:
        HttpResponseBadRequest()


def checkDirects(request):
    directs_count = 0
    if request.user.is_authenticated:
        directs_count = Message.objects.filter(user=request.user, is_read=False).count()

    return {"directs_count": directs_count}
