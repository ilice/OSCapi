from __future__ import unicode_literals

from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token
from django.conf import settings


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class Error(models.Model):
    S_WARNING = 'W'
    S_ERROR = 'E'

    SEVERITIES = (
        (S_WARNING, 'Warning'),
        (S_ERROR, 'Error')
    )

    date = models.DateTimeField()
    process_name = models.CharField(max_length=20)
    module_name = models.CharField(max_length=255)
    function_name = models.CharField(max_length=255)
    severity = models.CharField(max_length=1, choices=SEVERITIES)
    message = models.TextField()
    actionable_info = models.TextField(null=True)


class Feed(models.Model):
    url = models.CharField(max_length=255)
    date_launched = models.DateTimeField()
    date_finished = models.DateTimeField(null=True)
    update_date = models.DateTimeField()
    success = models.BooleanField()
    info = models.TextField(null=True)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created=False, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        instance.userprofile.save()


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    gender = models.CharField(max_length=10, null=True)
    google_id = models.CharField(max_length=255, null=True)
    facebook_id = models.CharField(max_length=255, null=True)
    link = models.URLField(null=True)
    picture_link = models.URLField(null=True)
    locale = models.CharField(max_length=10, null=True)


class UserParcel(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cadastral_code = models.CharField(max_length=255)

    class Meta:
        unique_together = ('user', 'cadastral_code')
