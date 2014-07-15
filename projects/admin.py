from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from projects.models import *

# Define an inline admin descriptor for APIUser model
# which acts a bit like a singleton
class APIUserInline(admin.StackedInline):
	model = APIUser
	can_delete = False
	verbose_name_plural = 'API User'

# Define a new User admin
class UserAdmin(UserAdmin):
	inlines = (APIUserInline, )

# Register your models here.
admin.site.register(Category)
admin.site.register(Project)
admin.site.register(TaskList)
admin.site.register(Task)
admin.site.register(Risk)
admin.site.register(Link)
admin.site.register(Comment)

# Need to Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)