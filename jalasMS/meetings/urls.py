from django.urls import path
from . import views

urlpatterns = [
    path('view/<int:meeting_id>', views.get_meeting_info, name='get_meeting_info'),
    path('list_rooms/<str:start_time>/<str:end_time>/',
         views.list_rooms, name='list_rooms'),
    path('reserve_room/<int:poll_id>/<int:room_id>/<str:start_time>/<str:end_time>',
         views.reserve_room, name='reserve_room'),
]
