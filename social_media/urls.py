"""social_media URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# Django Imports
from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static

# Account Imports
from account.views import newConversation, profile, follow, GenericViewSet, ProfileViewAPI

from post.views import ListStream, tags_api

# Django Rest Framwork Imports
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'users', GenericViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/', include('account.urls')),
    path('', include('post.urls')),

    path('chat/', include('chat.urls')),
    path('notifications/', include('notifications.urls')),

    path('<username>/', profile, name='profile'),
    path('<username>/new-conversation', newConversation, name='new-conversation'),
    path('<username>/saved', profile, name='profilefavorites'),
    path('<username>/follow/<option>', follow, name='follow'),

    # Django REST Framework
    path('api/', include(router.urls)),
    path('api/getstreams/<int:pk>', ListStream.as_view(), name='api-list-streams'),
    path('api/getprofile/<int:pk>', ProfileViewAPI.as_view(), name='api-get-profile'),
    path('api/tags', tags_api, name='api-tags'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
