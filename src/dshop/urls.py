# -*- coding: utf-8 -*-

from os import path

from django.conf.urls.defaults import *
from dshop import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^', include('dshop.main.urls')),
    (r'^cookies/$', 'dshop.cookies_policy.views.cookies_accept'),
    (r'^%sscript-view/(?P<script>.+)/$' % settings.ADMIN_PREFIX, 'dshop.main.admin.script_view'),
    (r'^%sclose-related-view/(?P<tab_name>.+)/$' % settings.ADMIN_PREFIX, 'dshop.main.admin.close_related_view'),
    (r'^%s' % settings.ADMIN_PREFIX, include(admin.site.urls)),
)

urlpatterns += patterns('',
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)

# TODO: This won't be needed when ads slider will be fixed
urlpatterns += patterns('',    
    (r'^data.xml$', 'django.views.static.serve',
                    { 'path' : 'slider/data.xml', 'document_root': settings.MEDIA_ROOT }),
)

# General single page redirects
urlpatterns += patterns('',
    (r'^(?P<src>.+)$', 'dshop.main.views.redirect')
)

handler404 = 'dshop.main.views.view404'
