from django.conf.urls import patterns, include, url
from django.conf.urls.static import static

from django.contrib import admin

from rest_framework import routers
from restapi import views

import settings as settings

admin.autodiscover()

router = routers.DefaultRouter()
router.register(r'links', views.LinkViewSet)
router.register(r'projects', views.ProjectViewSet)
router.register(r'tasklists', views.TaskListViewSet)
router.register(r'tasks', views.TaskViewSet)

urlpatterns = patterns('',
    url(r'^$', 'projects.views.index'),
    url(r'^projects/', include('projects.urls')),
    url(r'^api/1.0/', include('api.urls')),
    url(r'^api/2.0/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', 'projects.views.ssl_login', name='login_view'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', name='logout_view'),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
