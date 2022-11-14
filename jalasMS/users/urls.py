from django.urls import path
from . import views


urlpatterns = [
    path('login', views.log_in, name='log_in'),
    path('logout', views.log_out, name='log_out'),
    path('checkemail', views.check_email, name='check_email'),
    path('notifications/set', views.change_notif_setting,
         name='change_notif_setting'),
    path('notifications/get', views.check_notif_setting,
         name='check_notif_setting'),
    path('qualityinfo/add', views.add_quality_info, name='add_quality_info'),
]
