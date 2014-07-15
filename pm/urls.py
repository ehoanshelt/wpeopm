from django.conf.urls import patterns, include, url
from django.conf.urls.static import static

from django.contrib import admin

import settings as settings

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'pm.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', 'projects.views.index'),
    url(r'^projects/', include('projects.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', 'django.contrib.auth.views.login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout'),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
