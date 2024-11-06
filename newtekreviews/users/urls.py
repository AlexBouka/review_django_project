from django.urls import path
from django.contrib.auth.views import LogoutView, PasswordChangeView, PasswordChangeDoneView

from .views import (
    UserRegistrationView, UserLoginView, UserLogoutView,
    UserPasswordChangeView,
    UserProfileView, UpdateUserProfileView
)

app_name = 'users'

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),

    path(
        'password-change/', UserPasswordChangeView.as_view(),
        name='password_change'
        ),
    path(
        'password-change/done/',
        PasswordChangeDoneView.as_view(
            template_name='users/password_change_done.html'),
        name='password_change_done'
        ),

    path('profile/', UserProfileView.as_view(), name='profile'),
    path(
        'edit-profile/', UpdateUserProfileView.as_view(),
        name='edit-profile'
        ),
]
