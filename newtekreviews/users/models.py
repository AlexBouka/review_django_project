from django.contrib.auth.models import User
from django.templatetags.static import static
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_photo = models.ImageField(
        upload_to="profile_photos/", default="profile_photos/default.png",
        null=True, blank=True,
        verbose_name="Profile Photo"
        )
    name = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Name")
    bio = models.TextField(null=True, blank=True)
    social_facebook = models.CharField(max_length=200, null=True, blank=True)
    social_instagram = models.CharField(max_length=200, null=True, blank=True)
    social_twitter = models.CharField(max_length=200, null=True, blank=True)
    social_youtube = models.CharField(max_length=200, null=True, blank=True)
    social_website = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
