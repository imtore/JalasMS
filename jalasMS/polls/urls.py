from django.urls import path
from . import views


urlpatterns = [
    path('view/<int:poll_id>', views.get_info, name='get_info'),
    path('create', views.create_poll, name='create_poll'),
    path('<int:user_id>/all', views.get_all, name='get_all'),
    path('edit', views.edit_poll, name='edit_poll'),
    path('comment/add', views.add_comment, name='add_comment'),
    path('comment/get', views.get_all_comments, name='get_all_comments'),
    path('comment/delete', views.delete_comment, name='delete_comment')
]
