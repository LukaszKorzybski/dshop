from django.conf.urls.defaults import *
from dshop.cookies_policy.views import cookies_accept

urlpatterns = patterns('',
                       url(r'^$', cookies_accept, name='cookies_accept'),
)
