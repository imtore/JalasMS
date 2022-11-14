from django.contrib import admin

# Register your models here.

from .models import Poll
from .models import Date
from .models import Invitation
from .models import Comment


admin.site.register(Poll)
admin.site.register(Date)
admin.site.register(Invitation)
admin.site.register(Comment)
