import django.contrib.auth.views as authviews
from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path(
        'signup/',
        views.SignUp.as_view(),
        name='signup'
    ),
    path(
        'login/',
        authviews.LoginView.as_view(template_name='users/login.html'),
        name='login'
    ),
    path(
        'logout/',
        authviews.LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout'
    ),
    path(
        'password_change/',
        authviews.PasswordChangeView.as_view(
            template_name='users/password_change_form.html'),
        name='password_change'
    ),
    path(
        'password_change/done/',
        authviews.PasswordChangeDoneView.as_view(
            template_name='users/password_change_done.html'),
        name='password_change_done'
    ),
    path(
        'password_reset/',
        authviews.PasswordResetView.as_view(
            template_name='users/password_reset_form.html'),
        name='password_reset_form'
    ),
    path(
        'password_reset/done/',
        authviews.PasswordResetDoneView.as_view(
            template_name='users/password_reset_done.html'),
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        authviews.PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confirm.html'),
        name='password_reset_confirm'
    ),
    path(
        'reset/done/',
        authviews.PasswordResetCompleteView.as_view(
            template_name='users/password_reset_complete.html'),
        name='password_reset_complete'
    )
]
