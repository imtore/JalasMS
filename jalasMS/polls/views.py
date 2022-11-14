from django.http import HttpResponse
import json
from .models import Poll, Date, Invitation, Comment
from jalasMS.meetings.models import Meeting
from jalasMS.users.models import CustomUser
from jalasMS.vote.models import Vote
from django.core import serializers
from django.http import Http404
from collections import defaultdict
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist


def create_poll(request):
    if request.method == 'POST':
        json_list = json.loads(request.body)
        new_poll = Poll(owner_id=json_list['user_id'], title=json_list['title'],
                        status=False)
        new_poll.save()

        for email in json_list['participants']:
            participant = CustomUser.objects.filter(
                email=email).values()[0]
            new_invitation = Invitation(
                poll_id=new_poll.id, participant_id=participant['id'])
            new_invitation.save()

        for option in json_list['times']:
            start_time = option['startTime'][:-5]+"Z"
            end_time = option['endTime'][:-5]+"Z"
            new_option = Date(
                poll=new_poll, start_time=start_time, end_time=end_time)
            new_option.save()

        invitation_url = "http://localhost:4200/poll-view/" + \
            str(new_poll.id)
        for email in json_list['participants']:
            send_email('jalas meeting invitation',
                       invitation_url, email, 'on_invitation')

        return(HttpResponse(200, "poll has been created"))
    else:
        return (HttpResponse(400, "bad request"))


def get_all(request, user_id):
    all_polls = get_polls_of_user(user_id)
    all_meetings = get_meetings_of_user(user_id)
    all_invitations = get_invitations_of_user(user_id)

    final_dict = {'polls': json.loads(all_polls), 'meetings': json.loads(
        all_meetings), 'invitations': json.loads(all_invitations)}
    final_json = json.dumps(final_dict)
    return HttpResponse(final_json)


def get_info(request, poll_id):
    # if request.user.is_authenticated:
    json_list = json.loads(request.body)
    poll = Poll.objects.filter(id=poll_id, owner_id=json_list['user_id'])
    if poll.count() == 0:
        invitation = Invitation.objects.filter(
            poll_id=poll_id, participant_id=json_list['user_id'])
        if invitation.count() == 0:
            return HttpResponse(403, "forbidden")
    dictionary = {}
    poll = Poll.objects.filter(id=poll_id)

    dates = Date.objects.filter(poll=list(poll)[0])

    poll = poll.values()[0]
    dictionary['poll'] = poll

    dictionary['times'] = []

    dates_list = dates.values()

    i = 0
    for date in dates:
        date_dict = {}

        dates_list[i]['start_time'] = dates_list[i]['start_time'].strftime(
            '%Y-%m-%d %H:%M:%S')
        dates_list[i]['end_time'] = dates_list[i]['end_time'].strftime(
            '%Y-%m-%d %H:%M:%S')

        new_date = {}
        new_date['id'] = dates_list[i]['id']
        new_date['poll_id'] = dates_list[i]['poll_id']
        new_date['start_time'] = dates_list[i]['start_time'].strftime(
            '%Y-%m-%d %H:%M:%S')
        new_date['end_time'] = dates_list[i]['end_time'].strftime(
            '%Y-%m-%d %H:%M:%S')

        date_dict['date'] = new_date
        date_dict['votes'] = []
        votes = Vote.objects.filter(date=date).values()
        for vote in votes:
            date_dict['votes'].append(vote)
        dictionary['times'].append(date_dict)
        i += 1

    invitations = Invitation.objects.filter(
        poll_id=poll_id).values()
    dictionary['participants'] = []
    for invitation in invitations:
        user = CustomUser.objects.get(id=invitation['participant_id'])
        dictionary['participants'].append(user.email)
    # print(dictionary['participants'])
    return HttpResponse(json.dumps(dictionary))


def get_polls_of_user(user_id):
    result_json = serializers.serialize(
        'json', Poll.objects.filter(owner=user_id, status=False))
    return result_json


def get_meetings_of_user(user_id):
    now_meeting_polls = Poll.objects.filter(owner=user_id, status=True)
    if now_meeting_polls.count() == 0:
        return serializers.serialize('json', [])
    result_query_set = Meeting.objects.none()
    for each_poll in now_meeting_polls.values():
        meeting = Meeting.objects.filter(poll=each_poll['id'])
        result_query_set = result_query_set.union(meeting)
    result_json = serializers.serialize('json', result_query_set)
    # print(result_json)
    return result_json


def get_invitations_of_user(user_id):
    user_invitations = Invitation.objects.filter(participant_id=user_id)
    if user_invitations.count() == 0:
        return serializers.serialize('json', [])
    poll_query_set = Poll.objects.none()
    meeting_query_set = Meeting.objects.none()
    for each_invitation in user_invitations.values():
        poll = Poll.objects.filter(
            id=each_invitation['poll_id'])
        if not poll.values()[0]['status']:
            poll_query_set = poll_query_set.union(poll)
        else:
            meeting = Meeting.objects.filter(poll=poll.values()[0]['id'])
            # print(meeting_query_set)
            meeting_query_set = meeting_query_set.union(meeting)

    meeting_json = serializers.serialize('json', meeting_query_set)
    poll_json = serializers.serialize('json', poll_query_set)
    result_dict = {'polls': json.loads(
        poll_json), 'meetings': json.loads(meeting_json)}
    result_json = json.dumps(result_dict)
    # print(result_json)
    return result_json


def edit_poll(request):
    if request.method == 'POST':
        json_body = json.loads(request.body)
        poll = Poll.objects.filter(
            owner_id=json_body['user_id'], id=json_body['poll_id'])
        if poll.count() == 0:
            return HttpResponse(403, "forbidden")

        poll_id = poll.values()[0]['id']
        poll_title = poll.values()[0]['title']

        add_options(json_body['new_times'], poll_id)
        delete_options(json_body['removed_times'], poll_id)
        add_invitations(json_body['new_participants'], poll_id)
        delete_invitations(json_body['removed_participants'], poll_id)

        return HttpResponse(200, "changes have been made")
    else:
        return HttpResponse(400, "bad request")


def add_options(options, poll_id):
    if len(options) == 0:
        return
    for option in options:
        # print(option['timestampStart'])
        start_time = option['timestampStart'][:-5]+"Z"
        end_time = option['timestampEnd'][:-5]+"Z"
        new_option = Date(
            poll_id=poll_id, start_time=start_time, end_time=end_time)
        new_option.save()

    poll_title = Poll.objects.get(id=poll_id).title
    invitation_url = "http://localhost:4200/poll-view/" + str(poll_id)
    invitations = Invitation.objects.filter(poll_id=poll_id)
    for invitation in invitations:
        user = CustomUser.objects.get(id=invitation.participant_id)
        send_email('A new option has been added', invitation_url + "\n" + "dear participant of " + poll_title + ", there are a few changes in options. please check.",
                   user.email, 'on_new_option')
    return


def delete_options(options, poll_id):
    if len(options) == 0:
        return
    invitation_url = "http://localhost:4200/poll-view/" + str(poll_id)
    poll_title = Poll.objects.get(id=poll_id).title
    for option in options:
        try:
            votes = Vote.objects.filter(date_id=option['id'])
            option = Date.objects.get(id=option['id'])
            for vote in votes:
                send_email('An option has been removed', invitation_url + "\n" + "Dear participant of " + poll_title +
                           ", an option on which you had voted is now removed. please check.", vote.email, 'on_option_removal')
            option.delete()

        except ObjectDoesNotExist:
            return Http404
    return


def add_comment(request):
    req_body = json.loads(request.body)
    print(req_body)
    parent = None
    if req_body['reply_to'] == 0:
        parent = None
    else:
        parent = Comment.objects.get(id=req_body['reply_to'])
    new_comment = Comment(poll_id=req_body['poll_id'], user_id=req_body['user_id'],
                          parent=parent, context=req_body['text'])
    new_comment.save()
    return HttpResponse(200, "comment has been added")


def delete_comment(request):
    req_body = json.loads(request.body)
    comment = Comment.objects.get(id=req_body['comment_id'])
    comment.delete()
    return HttpResponse('200')


def get_all_comments(request):
    req_body = json.loads(request.body)
    comments = Comment.objects.filter(poll_id=req_body['poll_id'])
    dictionary = {'comments': []}
    for comment in comments.values():
        com = {}
        com['context'] = comment['context']
        com['user'] = CustomUser.objects.get(id=comment['user_id']).email
        if comment['parent_id'] == None:
            com['parent'] = 0
        else:
            com['parent'] = comment['parent_id']
        com['id'] = comment['id']
        dictionary['comments'].append(com)
    return HttpResponse(json.dumps(dictionary))


def add_invitations(invitations, poll_id):
    if len(invitations) == 0:
        return
    invitation_url = "http://localhost:4200/poll-view/" + \
        str(poll_id)
    for invitation in invitations:
        user = CustomUser.objects.get(email=invitation)
        new_invitation = Invitation(participant_id=user.id, poll_id=poll_id)
        new_invitation.save()
        send_email('jalas poll invitation',
                   invitation_url, invitation, 'on_invitation')
    return


def delete_invitations(invitations, poll_id):
    if len(invitations) == 0:
        return
    poll_title = Poll.objects.get(id=poll_id).title
    for invitation in invitations:
        try:
            user = CustomUser.objects.get(email=invitation)
            target = Invitation.objects.get(
                poll_id=poll_id, participant_id=user.id)
            target.delete()
            send_email('your invitation is canceled',
                       'your invitation to ' + poll_title+' has been cancled', invitation, 'on_invitation_removal')
        except ObjectDoesNotExist:
            continue
    return


def send_email(subject, message, to, condition):
    try:
        user = CustomUser.objects.get(email=to)
        conf = wrap_conf(user)
        if conf[condition] == True:
            send_mail(subject=subject, message=message,
                      from_email='jalasms@yahoo.com', recipient_list=[to])
    except ObjectDoesNotExist:
        pass

# TODO: move to user views


def wrap_conf(user):
    return {'on_invitation': user.on_invitation, 'on_meeting_arrangment': user.on_meeting_arrangment,
            'on_new_option': user.on_new_option, 'on_option_removal': user.on_option_removal,
            'on_invitation_removal': user.on_invitation_removal, 'on_room_reservation': user.on_room_reservation,
            'on_new_vote': user.on_new_vote}
