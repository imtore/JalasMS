from django.db import models
from jalasMS.polls.models import Poll
# Create your models here.


class Meeting(models.Model):
    id = models.AutoField(primary_key=True)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    title = title = models.CharField(max_length=50)
    room = models.IntegerField(null=True, blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
