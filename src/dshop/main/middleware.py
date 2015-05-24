# -*- coding: utf-8 -*-

from datetime import datetime
from datetime import timedelta
from decimal import Decimal

from django.http import HttpResponseServerError

from dshop import settings
from dshop.main import session_keys as sk
from dshop.main import models as m

def frontend_middleware(f):
    '''Execute wrapped middleware function only when processing frontend view request.'''
    def decorator(self, request):
        if request.path.startswith(settings.MEDIA_URL) or request.path.startswith('/'+settings.ADMIN_PREFIX):
            return
        return f(self, request)
    return decorator


class DshopRequestContainer(object):
    def __init__(self):
        self.client = None
        self.cart = None


class DShopRequestMiddleware(object):
    '''Put dshop placeholder object into request, etc.'''

    @frontend_middleware
    def process_request(self, request):
        request.dshop = DshopRequestContainer()


class ShoppingCartMiddleware(object):
    '''Create legacy shopping cart from session data and put it into request.'''

    @frontend_middleware
    def process_request(self, request):        
        cart = None
        if 'cart_id' in request.session:
            cart_id = request.session['cart_id']
            try:
                cart = m.Cart.objects.get(pk=cart_id)
            except m.Cart.DoesNotExist:
                pass 
        if not cart:
            cart = m.Cart()
            if request.dshop.client: # It's probably not possible to have a logged in session without a cart, but...
                cart.set_client(request.dshop.client)
            cart.session_key  = request.session.session_key
            cart.save()
            request.session['cart_id'] = cart.id

        request.dshop.cart = cart


class ThreeLevelAuthMiddleware(object):
    '''Manage 3 level authorization for dshop clients. Put client object into request.'''

    @frontend_middleware
    def process_request(self, request):

        if sk.auth_level not in request.session:
            request.session[sk.auth_level] = 0
            
        # fallback to 1 level auth if 2 level auth max age elapsed
        if request.session[sk.auth_level] == 2:
            login_time = request.session[sk.login_time]
            if (datetime.now() - login_time) > timedelta(seconds=settings.SND_LEVEL_AUTH_AGE):
                request.session[sk.auth_level] = 1

        # Put client object into request
        if request.session[sk.auth_level] > 0:
            try:
                request.dshop.client = m.Client.objects.get(pk=request.session[sk.client_id])
            except m.Client.DoesNotExist:
                # TODO log the problem (client account has been removed in the meanwhile?)
                request.session[sk.auth_level] = 0
