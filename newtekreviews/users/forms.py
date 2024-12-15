from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    UserCreationForm, AuthenticationForm, PasswordChangeForm
    )

from .models import Profile


class UserRegistrationForm(UserCreationForm):
    username = forms.CharField(
        # label="Username",
        widget=forms.TextInput(attrs={
            "class": "login__form-input", "placeholder": "Username*"}
            )
    )
    password1 = forms.CharField(
        # label="Password",
        widget=forms.PasswordInput(attrs={
            "class": "login__form-input", "placeholder": "Password*"}
            )
    )
    password2 = forms.CharField(
        # label="Repeat password",
        widget=forms.PasswordInput(attrs={
            "class": "login__form-input", "placeholder": "Repeat password*"}
            )
    )
    first_name = forms.CharField(
        # label="First name",
        widget=forms.TextInput(attrs={
            "class": "login__form-input", "placeholder": "First name",
            "required": False}
            )
    )
    last_name = forms.CharField(
        # label="Last name",
        widget=forms.TextInput(attrs={
            "class": "login__form-input", "placeholder": "Last name",
            "required": False}
            )
    )
    email = forms.EmailField(
        # label="Email",
        widget=forms.EmailInput(attrs={
            "class": "login__form-input", "placeholder": "Email*"}
            )
    )

    class Meta:
        model = get_user_model()
        fields = [
            "username", "email", "first_name", "last_name"
            ]
        labels = {
            "first_name": "First name",
            "last_name": "Last name",
            "email": "Email",
        }
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        """Sets the label of each form field to an empty string and sets
        'first_name' and 'last_name' fields to be not required."""
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'first_name' or field_name == 'last_name':
                field.required = False
            field.label = ""

    def validate_email(self):
        """Checks if the email already exists in the database.
        If yes, raises a validation error, otherwise returns the email."""
        email = self.cleaned_data.get("email")
        if email and get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists.")
        return email

    def validate_username(self):
        """Checks if the username already exists in the database.
        If yes, raises a validation error, otherwise returns the username."""
        username = self.cleaned_data.get("email")
        if username and get_user_model().objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists.")
        return username


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={
            "class": "login__form-input", "placeholder": "Username"}
            )
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            "class": "login__form-input", "placeholder": "Password"}
            )
    )

    def __init__(self, *args, **kwargs):
        """Hides the labels of the form fields."""
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.label = ""

    class Meta:
        model = get_user_model()
        fields = ["username", "password"]


class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Old password",
        widget=forms.PasswordInput(attrs={
            "class": "login__form-input", "placeholder": "Old password"}
            )
    )
    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(attrs={
            "class": "login__form-input", "placeholder": "New password"}
            )
    )
    new_password2 = forms.CharField(
        label="Repeat new password",
        widget=forms.PasswordInput(attrs={
            "class": "login__form-input", "placeholder": "Repeat new password"}
            )
    )


class UserProfileForm(forms.ModelForm):
    username = forms.CharField(
        disabled=True, label="Username",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    email = forms.CharField(
        disabled=True, label="Email",
        widget=forms.EmailInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = Profile
        fields = [
                "name", "email", "profile_photo", "bio", "social_facebook",
                "social_instagram", "social_twitter", "social_youtube",
                "social_website"
            ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "bio": forms.Textarea(attrs={"class": "form-control"}),
            "social_facebook": forms.URLInput(attrs={"class": "form-social"}),
            "social_instagram": forms.URLInput(attrs={"class": "form-social"}),
            "social_twitter": forms.URLInput(attrs={"class": "form-social"}),
            "social_youtube": forms.URLInput(attrs={"class": "form-social"}),
            "social_website": forms.URLInput(attrs={"class": "form-social"}),
        }
