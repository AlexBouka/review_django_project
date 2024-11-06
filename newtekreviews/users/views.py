import logging
import csv
from django.db.models.options import Options

from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LogoutView
from django.views.generic import DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView

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


class UpdateUserProfileView(LoginRequiredMixin, CreateView):
    model = Profile
    form_class = UserProfileForm
    template_name = 'users/profile_update.html'

    def get_success_url(self):
        return reverse_lazy('users:profile')
