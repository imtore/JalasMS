from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseForbidden
import json
from django.core import serializers
from .models import CustomUser, Qmetric
from django.core.exceptions import ObjectDoesNotExist
from jalasMS.polls.views import wrap_conf
from django.shortcuts import render
import ast


def log_in(request):
    json_list = json.loads(request.body)
    email = json_list['email']
    password = json_list['password']
    user = authenticate(request, email=email, password=password)
    dictionary = {}
    if user is not None:
        login(request, user)
        dictionary['id'] = user.id
        dictionary['email'] = user.email

    return HttpResponse(json.dumps(dictionary))


def log_out(request):
    logout(request)
    return HttpResponse("200")


def check_email(request):
    json_list = json.loads(request.body)
    try:
        CustomUser.objects.get(email=json_list['email'])
    except ObjectDoesNotExist:
        return HttpResponse(404)
    return HttpResponse(200)


def check_notif_setting(request):
    json_list = json.loads(request.body)
    user = CustomUser.objects.get(id=json_list['user_id'])
    setting = {'user_id': json_list['user_id'], 'setting': wrap_conf(user)}
    return HttpResponse(json.dumps(setting))


def change_notif_setting(request):
    json_list = json.loads(request.body)
    user = CustomUser.objects.get(id=json_list['user_id'])
    assign_change(json_list['setting'], user)
    return HttpResponse('200')


def assign_change(new, user):
    user.on_invitation = new['on_invitation']
    user.on_meeting_arrangment = new['on_meeting_arrangment']
    user.on_new_option = new['on_new_option']
    user.on_option_removal = new['on_option_removal']
    user.on_invitation_removal = new['on_invitation_removal']

    user.on_room_reservation = new['on_room_reservation']
    user.on_new_vote = new['on_new_vote']
    user.save()

# def quality_in_use(request):
#     user_id = json.loads(request.body)['user_id']
#     user = CustomUser.objects.get(id=user_id)
#     if not user.is_staff:
#         return HttpResponseForbidden
#     # assign metric1, value1, metric2, value2
#     return render(request, 'users/index.html', {'metric1': metric1, 'value1': value1, 'metric2': metric2, 'value2': value2})


def add_quality_info(request):
    data = json.loads(request.body)
    met = Qmetric.objects.get(id=1)

    if not data['room_reserved'] == 0:
        met.reserved_rooms = met.reserved_rooms+1
    if not data['create_poll'] == 0:
        n = met.poll_creation_num
        old_avg = met.poll_creation_avg
        met.poll_creation_avg = (old_avg*n + data['create_poll'])/(n+1)
        met.poll_creation_num = n+1
    if not data['edit_poll'] == 0:
        met.edited_polls = met.edited_polls+1
    if not data['average_responsetime'] == 0:
        n = met.response_time_num
        old_avg = met.response_time_avg
        met.response_time_avg = (
            old_avg*n + data['average_responsetime'])/(n+1)
        met.response_time_num = n+1
    if not data['throughput'] == 0:
        met.throughput = data['throughput']

    met.save()
    return HttpResponse('200')
