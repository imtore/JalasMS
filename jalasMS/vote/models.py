from django.db import models
from jalasMS.polls.models import Date, Invitation
# Create your models here.


class Vote(models.Model):
    VOTE_TYPE = (
        ('N', 'Negative'),
        ('P', 'Positive'),
        ('I', 'PositiveIfNeeded'),
    )
    date = models.ForeignKey(Date, on_delete=models.CASCADE)
    email = models.EmailField()
    choice = models.CharField(max_length=1, choices=VOTE_TYPE)
