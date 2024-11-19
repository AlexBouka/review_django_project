from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.mail import send_mail

from newtekreviews import settings

user = get_user_model()


@receiver(post_save, sender=user)
def user_postsave(sender, instance, created, **kwargs):
    if created:
        subject = instance.username
        message = f'Welcome to our website, {instance.username}!'
        from_email = settings.EMAIL_HOST_USER
        to_email = instance.email

        send_mail(subject, message, from_email, [to_email], fail_silently=False)