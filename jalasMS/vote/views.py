from django.http import HttpResponse
import json
from jalasMS.polls.models import Poll, Date, Invitation
from jalasMS.users.models import CustomUser
from .models import Vote
from django.http import Http404
from jalasMS.polls.views import send_email


def add_vote(request):
    if request.method == 'POST':
        # if(request.user.is_authenticated):
        json_list = json.loads(request.body)
        user = CustomUser.objects.filter(id=json_list['user_id'])
        poll = Poll.objects.filter(
            owner_id=json_list['user_id'], id=json_list['poll_id'])
        invitation = Invitation.objects.filter(
            participant_id=json_list['user_id'], poll_id=json_list['poll_id'])

        if poll.count() == 0 and invitation. count() == 0:
            return HttpResponse(403, "forbidden")

        if not poll.count() == 0:
            is_owner = True
        else:
            is_owner = False

        user = CustomUser.objects.filter(id=json_list['user_id']).values()[0]

        for vote in json_list['votes']:
            date = Date.objects.filter(id=vote['time_id'])

            new_vote = Vote(
                date=list(date)[0], email=user['email'], choice=vote['vote'])
            new_vote.save()

        poll = Poll.objects.get(id=json_list['poll_id'])

        voter_email = user['email']

        owner = CustomUser.objects.get(id=poll.owner_id)

        owner_email = owner.email
        message = "a new vote on " + poll.title + ", from: " + voter_email
        send_email('new vote', message, owner_email, 'on_new_vote')

        return HttpResponse(200, "vote is added")
        # else:
        # return HttpResponse(401, "unauthenticated")
    else:
        return HttpResponse(400, "bad request")
