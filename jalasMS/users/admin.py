from django.contrib import admin

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, Qmetric


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ('email', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('email', 'is_staff', 'is_active',
                   'date_joined', 'on_invitation')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
        ('Notifications of Invitaion', {'fields': (
            'on_invitation', 'on_meeting_arrangment', 'on_new_option', 'on_option_removal', 'on_invitation_removal')}),
        ('Notifications of Owner', {
         'fields': ('on_room_reservation', 'on_new_vote')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active', 'on_invitation', 'on_meeting_arrangment', 'on_new_option', 'on_option_removal', 'on_invitation_removal', 'on_room_reservation', 'on_new_vote')}
         ),
    )
    search_fields = ('email',)
    ordering = ('email',)


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Qmetric)
