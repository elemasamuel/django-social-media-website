from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('tag/<slug:tag_slug>', views.tags, name='tags'),
    path('like/', views.like_post, name='like_post'),
    path('<uuid:post_id>/comment', views.comment, name='postcomment'),
    path('<uuid:post_id>/favorite', views.favorite, name='postfavorite'),

    path('show-media/<stream_id>', views.showMedia, name='show-media'),
]