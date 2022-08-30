from . import views
from django.urls import path
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', views.registerPage, name ='register'),
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),

    path('settings/', views.settings, name='settings'),
    path('profile/edit/', views.editProfile, name='edit-profile'),

    path('changepassword/', views.passwordChange, name='change_password'),
   	path('changepassword/done', views.passwordChangeDone, name='change_password_done'),

    path('search/', views.userSearch, name='user-search'),

    path('reset_password/', auth_views.PasswordResetView.as_view(template_name='account/password_reset.html'), name='reset_password'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name='account/password_reset_sent.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='account/password_reset_form.html'), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='account/password_reset_done.html'), name='password_reset_complete'),
]
