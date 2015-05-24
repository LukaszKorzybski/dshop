# -*- coding: utf-8 -*-
'''To use this module you need to do four things: implement Buyer class,
   implement Payment class, implement Payment Adapter factory and finally
   register this factory by appending it to payment_factories list.

   Payment and Buyer are simple Adapters between your models and dotpay module
   interface.

   You can have many Payment adapters if you have different kind of payments
   in your app. Each application can have it's own Payment adapters (many)
   and should have only one Payment adapter factory.

   Payment adapter factory from each of your apps should be able to return proper
   Payment adapter class using only given control string. Factory is simple function
   that takes 1 parameter (control string) and returns Payment Adapter class.

   Each Payment adapter should have it's own, project-wide unique class of control strings.
   For eg. payments for shipping orders in dshop app can have control string class:
   "dshop.order:<order_id>".

   Control string must uniquely identify given payment. Control string is passed
   to dotpay site and it is then used by dotpay to identify payment when dotpay later
   sends payment status updates. So you should be able to retrieve payment object from DB
   using it's control string.
'''

import md5
from decimal import Decimal

from django.utils import http
from django.http import HttpResponse

from dshop import settings

payment_factories = []

class Buyer(object):
    '''DotPay buyer base class.'''
    def __init__(self, buyer):
        self.buyer = buyer
    def firstName(self):
        pass
    def lastName(self):
        pass
    def email(self):
        pass
    def street(self):
        pass
    def streetNumber(self):
        pass
    def town(self):
        pass
    def postCode(self):
        pass
    def country(self):
        '''Country code.'''
        pass
    def phone(self):
        '''Phone number.'''
        pass
    def language(self):
        '''2-letter language code in which payment pages should be displayed.'''
        pass


class Payment(object):
    '''DotPay payment base class.'''
    def __init__(self, payment=None):
        '''If you give payment object the bridge will be bound, otherwise it will be unbound.'''
        self.payment = payment
    def isBound(self):
        '''Return True if payment object is bound into the bridge.'''
        return True if self.payment else False
    def control(self):
        '''Return control string for bound payment. It have to be unique
           identifier for the payment, for eg. database ID. It is used to load
           payment object form DB upon status update request sent from DotPay.'''
        pass
    def amount(self):
        '''Return amount to be paid (decimal with precision set to 2).'''
        pass
    def description(self):
        '''Return human friendly description of the item for which customer is going to pay.'''
        pass
    def statusUrl(self):
        '''Url to payment status information page.'''
        pass
    def loadPayment(self, control):
        '''Load payment object identified by given control string.'''
        pass
    def updatePaymentStatus(self, status, transaction_num, amount):
        '''Update payment status on currently bound payment object.'''
        pass
    

def getRedirectUrl(buyer, payment, return_url):
    '''Construct redirect URL, for given bound payment bridge, to DotPay.pl service.'''
    if not payment.isBound:
        raise ValueError(u'Given payment bridge is unbound. Please provide bound payment bridge.')
    params = {
        'id'       : settings.DOTPAY_USER_ID,
        'control'  : payment.control(),
        'kwota'    : str(payment.amount()),
        'opis'     : payment.description(),
        'jezyk'    : buyer.language(),
        'URL'      : '%s://%s%s' % (settings.SSL_PROTO, settings.HOST_NAME, return_url),
        'typ'      : settings.DOTPAY_TYPE,
        'txtguzik' : settings.DOTPAY_BUTTON_TEXT,
        'imie'     : buyer.firstName(),
        'nazwisko' : buyer.lastName(),
        'email'    : buyer.email(),
        'ulica'    : buyer.street(),
        'budynek'  : buyer.streetNumber(),
        'miasto'   : buyer.town(),
        'kod'      : buyer.postCode(),
        'telefon'  : buyer.phone(),
        'kraj'     : 'PL',
        'p_info'   : settings.DOTPAY_SELLER
    }
    return '%s?%s' % (settings.DOTPAY_URL, http.urlencode(params))

def create_control_string(pin, id, control, trans_id, amount, email, tstatus):
    return '%s:%s:%s:%s:%s:%s:::::%s' % (pin, id, control, trans_id, amount, email, tstatus)

def statusRequestAuthentic(request):
    print request.POST
    pin = settings.DOTPAY_PIN
    id = settings.DOTPAY_USER_ID
    control = request.POST.get("control")
    trans_id = request.POST.get("t_id")
    amount = request.POST.get("amount")
    email = request.POST.get("email")
    tstatus = request.POST.get("t_status")
    recieved_md5 = request.POST.get("md5")

    teststr = create_control_string(pin, id, control, trans_id, amount, email, tstatus)
    print teststr
    if recieved_md5 == md5.new(teststr).hexdigest():
        return True
    else:
        return False


def updatePaymentStatusView(request):
    dotpay_user = request.POST.get('id', '')
    if settings.DOTPAY_USER_ID != dotpay_user:
        print "Online payments: dotpay user id doesn't match"
        return HttpResponse('OK')
    if not statusRequestAuthentic(request):
        print "Online payments: request not authentic"
        return HttpResponse('OK')
    try:
        adapter = _getPaymentAdapterClass(request.POST['control'])()
    except:
        HttpResponse("OK")
    adapter.loadPayment(request.POST['control'])
    adapter.updatePaymentStatus(request.POST['t_status'], request.POST['t_id'], Decimal(request.POST['amount']))
    print "Online payments: %s status changed to %s (amount %s)" % (request.POST['t_id'], request.POST['t_status'], request.POST['amount'])
    return HttpResponse("OK")


def _getPaymentAdapterClass(control):
    '''Return Payment Adapter class for given control string.'''
    for factory in payment_factories:
        print factory
        p = factory(control)
        if p is not None:
            return p
    raise RuntimeError(u"Could not find proper Payment Adapter class. Check your factories! Control: %s" % control)
