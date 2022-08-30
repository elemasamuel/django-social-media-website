from django.urls import path
from . import views


urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('directs/<username>', views.directs, name='directs'),
    path('send/', views.sendDirect, name='send-direct'),
]