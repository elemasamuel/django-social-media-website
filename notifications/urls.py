from django.urls import path
from . import views


urlpatterns = [
    path('', views.showNotifications, name ='show-notifications'),
    path('<noti_id>/delete', views.deleteNotification, name ='delete-notification'),
]