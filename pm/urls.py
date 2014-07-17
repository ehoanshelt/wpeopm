from django.conf.urls import patterns, include, url
from django.conf.urls.static import static

from django.contrib import admin

import settings as settings

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'projects.views.index'),
    url(r'^projects/', include('projects.urls')),
    url(r'^api/1.0/', include('api.urls')),
    url(r'^api/2.0/', include('restapi.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', 'django.contrib.auth.views.login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout'),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
