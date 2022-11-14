from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    # invited
    on_invitation = models.BooleanField(default=True)
    on_meeting_arrangment = models.BooleanField(default=True)
    on_new_option = models.BooleanField(default=True)
    on_option_removal = models.BooleanField(default=True)
    on_invitation_removal = models.BooleanField(default=True)

    # owner
    on_room_reservation = models.BooleanField(default=True)
    on_new_vote = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Qmetric(models.Model):
    reserved_rooms = models.IntegerField(default=0)
    poll_creation_avg = models.FloatField()
    poll_creation_num = models.IntegerField(default=0)
    edited_polls = models.IntegerField(default=0)
    response_time_avg = models.FloatField()
    response_time_num = models.IntegerField(default=0)
    throughput = models.IntegerField(default=0)
