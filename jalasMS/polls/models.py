from django.db import models
from jalasMS.users.models import CustomUser

# Create your models here.


class Poll(models.Model):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Date(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    start_time = models.DateTimeField(default=0)
    end_time = models.DateTimeField(default=0)


class Invitation(models.Model):
    participant = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)


class Comment(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    # TODO: ask what to on delete?
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    parent = models.ForeignKey(
        'self', blank=True, null=True, on_delete=models.CASCADE)
    context = models.TextField(max_length=150)
    # created_on = models.DateTimeField(auto_now_add=True)
