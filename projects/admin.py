from django.contrib import admin

from projects.models import *

# Register your models here.
admin.site.register(Category)
admin.site.register(Project)
admin.site.register(TaskList)
admin.site.register(Task)
admin.site.register(Dependency)
admin.site.register(Risk)
admin.site.register(Link)
admin.site.register(Comment)
