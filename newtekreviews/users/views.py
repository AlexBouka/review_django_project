import logging
import csv
import json
import os

from django.db.models.options import Options
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LogoutView
from django.views.generic import DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from google.oauth2 import id_token
from google.auth.transport import requests
from django.http import JsonResponse

from .models import Profile

from .forms import (
    UserRegistrationForm, UserLoginForm, UserProfileForm,
    UserPasswordChangeForm,
    )

logger = logging.getLogger(__name__)


class UserRegistrationView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'users/user_registration.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        """
        Called when the form is valid. Creates a new user and a corresponding
        profile. Logs an info message with the username of the newly created
        user.

        Returns:
            HttpResponse: The response to send to the browser.
        """

        if form.is_valid():
            form.save()
            Profile.objects.create(
                user=get_user_model().objects.get(
                    username=form.cleaned_data['username'])
            )
            logger.info(
                f'User {form.cleaned_data["username"]} registered successfully'
                )
        return super().form_valid(form)


class UserLoginView(LoginView):
    form_class = UserLoginForm
    template_name = 'users/user_login.html'

    def post(self, request, *args, **kwargs):
        if 'token' in request.POST:
            return self.google_sign_in(request)
        return super().post(request, *args, **kwargs)

    def google_sign_in(self, request):
        token = request.POST['token']
        try:
            idinfo = id_token.verify_oauth2_token(
                token, requests.Request(), os.environ.get('GOOGLE_CLIENT_ID'))

            user_email = idinfo['email']
            email_verified = idinfo.get('email_verified', False)
            user_name = idinfo.get('name', 'Unknown')

            if not email_verified:
                return JsonResponse(
                    {'success': False, 'message': 'Email not verified'},
                    status=403)

            from django.contrib.auth import login

            user, created = get_user_model().objects.get_or_create(
                email=user_email,
                defaults={
                    'username': user_email.split('@')[0],
                    'first_name': user_name
                }
            )
            if created:
                logger.info(f'User {user_email} created successfully')
                Profile.objects.create(user=user)
            login(request, user)

            return JsonResponse(
                {
                    'success': True,
                    'redirect_url': reverse_lazy('review:all_reviews')
                }
            )
        except ValueError:
            return JsonResponse(
                {'success': False, 'message': 'Invalid token'}, status=400)


class UserLogoutView(LogoutView):
    next_page = reverse_lazy('users:login')


class UserPasswordChangeView(PasswordChangeView):
    form_class = UserPasswordChangeForm
    template_name = 'users/password_change_form.html'
    success_url = reverse_lazy('users:password_change_done')


class UserProfileView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'users/profile_detail.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        return get_object_or_404(Profile, user=self.request.user)


class UpdateUserProfileView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = UserProfileForm
    template_name = 'users/profile_update.html'

    def get_object(self):
        return get_object_or_404(Profile, user=self.request.user)

    def get_success_url(self):
        return reverse_lazy('users:profile')
