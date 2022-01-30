from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('login/', auth_views.LoginView.as_view(
        template_name='users/login.html'),
        name='login'),
    path('logout/', auth_views.LogoutView.as_view(
        template_name='users/logged_out.html'),
        name='logout'),
    path('password_change_done/',
         auth_views.PasswordChangeDoneView.as_view(
             template_name='users/password_change_done.html'),
         name='password_change_done',),
    path('password_change_form/', auth_views.PasswordChangeView.as_view(
         template_name='users/password_change_form.html'),
         name='password_change_form',),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(
         template_name='users/password_reset_done.html'),
         name='password_reset_done',),
    path('password_reset_form/', auth_views.PasswordResetView.as_view(
         template_name='users/password_reset_form.html'),
         name='password_reset_form',),
    path('password_reset_confirm/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='users/password_reset_confirm.html'),
         name='password_reset_confirm',),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='users/password_reset_confirm.html'),
         name='password_reset_confirm'),
]
