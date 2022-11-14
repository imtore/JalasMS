from django.http import HttpResponse
import json
from .models import Meeting
from jalasMS.polls.models import Poll, Invitation
from django.core import serializers
from django.http import Http404, HttpResponseForbidden, HttpResponseNotAllowed
import requests
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from jalasMS.users.models import CustomUser
from jalasMS.polls.views import send_email


def get_meeting_info(request, meeting_id):
    user_id = json.loads(request.body)['user_id']
    try:
        meeting = Meeting.objects.get(id=meeting_id)
        poll_id = meeting.poll_id
    except ObjectDoesNotExist:
        return Http404

    try:
        Invitation.objects.get(
            poll_id=poll_id, participant_id=user_id)
    except ObjectDoesNotExist:
        pass

    try:
        Poll.objects.get(owner_id=user_id, id=poll_id)
    except ObjectDoesNotExist:
        return HttpResponseForbidden

    meeting_json = serializers.serialize('json', [meeting, ])
    return HttpResponse(meeting_json)


def list_rooms(request, start_time, end_time):
    res_sys_response = requests.get(
        'http://reserve.utse.ir/available_rooms', params={'start': start_time[:-5], 'end': end_time[:-5]})
    response = "{" + res_sys_response.text[1:-1] + "," + \
        "\"status\":" + str(res_sys_response.status_code) + "}"
    return HttpResponse(response)


def reserve_room(request, poll_id, room_id, start_time, end_time):
    user_id = json.loads(request.body)['user_id']
    try:
        poll = Poll.objects.get(pk=poll_id)
    except ObjectDoesNotExist:
        return Http404
    if not poll.owner_id == user_id:
        return HttpResponseForbidden

    url = 'http://reserve.utse.ir/rooms/' + str(room_id) + '/reserve'
    payload = {"username": str(
        poll_id), "start": start_time[:-5], "end": end_time[:-5]}
    res_sys_response = requests.post(url, json=payload)

    meeting_id = 0
    if(res_sys_response.status_code == 200):
        poll.status = True

        start_time = start_time[:-5] + "Z"
        end_time = end_time[:-5] + "Z"
        meeting = Meeting(
            poll=poll, title=poll.title, room=room_id, start_time=start_time, end_time=end_time)
        meeting.save()
        poll.save()
        meeting_id = meeting.id

        final_meeting_url = "http://localhost:4200/meeting-view/" + \
            str(meeting_id)

        participants = Invitation.objects.filter(poll=poll)
        for p in participants:
            user = CustomUser.objects.get(id=p.participant_id)
            send_email('jalas meeting', final_meeting_url,
                       user.email, 'on_meeting_arrangment')

        owner = CustomUser.objects.get(id=user_id)
        send_email('jalas meeting room', 'room ' + str(room_id) + 'is reserved for this meeting: ' + final_meeting_url,
                   owner.email, 'on_room_reservation')

    print(meeting_id)
    response = "{" + "\"status\":" + str(res_sys_response.status_code) + "," + \
        "\"meeting_id\":" + str(meeting_id) + "}"

    return HttpResponse(response)
