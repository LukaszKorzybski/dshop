# -*- coding: utf-8 -*-

#import java.lang.Exception

from django.utils.http import urlquote
from django.http import HttpResponseRedirect
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.urlresolvers import reverse

from dshop import settings
from dshop.main import session_keys as sk

def sess_key_required(key, redirect):
    '''Redirect to given url if session doesn't have key or if value at the key is None.'''
    def wrap(f):
        def decorated(request, *args, **kwargs):
            val = request.session.get(key, None)
            if val == None:
                return HttpResponseRedirect(redirect)
            else:
                return f(request, *args, **kwargs)
        return decorated
    return wrap

def login_required(level=1):
    '''Restrict access to decorated view for authorized clients only.'''
    def wrap(f):
        def decorated(request, *args, **kwargs):
            authlvl = request.session.get(sk.auth_level, 0)
            if request.session.get(sk.client_id, None) != None:
                if authlvl >= level:
                    return f(request, *args, **kwargs)

            path = urlquote(request.get_full_path())
            if authlvl > 0:
                tup = settings.AUTH_URL, REDIRECT_FIELD_NAME, path
            else:
                tup = settings.LOGIN_URL, REDIRECT_FIELD_NAME, path
            return HttpResponseRedirect('%s?%s=%s' % tup)
        return decorated
    return wrap

def logout_required(f):
    '''Display info message for logged in clients that they are already logged in.'''
    def decorated(request, *args, **kwargs):
        if request.session[sk.auth_level] > 0:
            return HttpResponseRedirect(reverse('dshop.main.views.alreadyLoggedIn'))
        else:
            return f(request, *args, **kwargs)
    return decorated