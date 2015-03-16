from django.conf.urls import patterns, include, url

from django.contrib import admin

import settings
from cloud_monitor.view import *

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'cloud_monitor.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    #url(r'^$', monitor),
    url(r'^$', get_resource),
    url(r'^resource/$', get_resource),
	url(r'^components/$', get_components),
	url(r'^res_hostlist/$', res_get_host_list),
	url(r'^res_hostmetadata/$', res_get_host_metadata),
	url(r'^res_hostmetric/$', res_get_host_metric),
	url(r'^comp_getfsms/$', comp_get_fsms),
    url(r'^links/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_URL}),
)
