# -*- coding: utf-8 -*-

import urllib
from decimal import Decimal

from django.core.urlresolvers import reverse
from django.http import HttpResponse

from dshop import settings

payment_factories = []

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
    return reverse('dshop.paypal.post_to_paypal_view', args=[payment.control(), payment.id()]) + \
        '?return_url=' + return_url

def post_to_paypal_view(request, control, id):
    payment = _getPaymentAdapterClass(control)()
    payment.loadPayment(control)
    hostname = '%s://%s' % (settings.SSL_PROTO, settings.HOST_NAME)

    content = POST_TO_PAYPAL_RESPONSE % {
        'paypal_url'    : settings.PAYPAL_URL,
        'business'      : settings.PAYPAL_ACCOUNT,
        'return'        : hostname + request.GET['return_url'],
        'cancel_return' : hostname + reverse('dshop.main.views.newOrderPayment', args=[id]) + "?p=failed",
        'notify_url'    : hostname + reverse('dshop.main.views.paymentStatusUpdate'),
        'custom'        : payment.control(),
        'amount_1'      : payment.amount(),
        'item_name_1'   : payment.description()
    }

    response = HttpResponse(content)
    response['Content-Type'] = u"text/html; charset=utf-8"
    return response

def authenticate_ipn_notif(data):
    args = {
        'cmd': '_notify-validate',
    }
    args.update(data)
    return urllib.urlopen(settings.PAYPAL_URL,
                          urllib.urlencode(args)).read() == 'VERIFIED'

def is_payment_valid(data, payment):
    if data.get('business', '').lower() != settings.PAYPAL_ACCOUNT.lower():
        return False
    if data.get('mc_currency', '').upper() != 'PLN':
        return False
    return True

def updatePaymentStatusView(request):
    r = None
    if request.method == 'POST':
        data = dict(request.POST.items())

        if authenticate_ipn_notif(data):
            adapter = _getPaymentAdapterClass(request.POST['custom'])()
            adapter.loadPayment(request.POST['custom'])

            if is_payment_valid(data, adapter) and adapter.shouldUpdateStatus(None):
                adapter.updatePaymentStatus(request.POST['payment_status'],
                                            request.POST['txn_id'],
                                            Decimal(request.POST['mc_gross']))
        else:
            pass
    
    return HttpResponse('OK')

def _getPaymentAdapterClass(control):
    '''Return Payment Adapter class for given control string.'''
    for factory in payment_factories:
        p = factory(control)
        if p is not None:
            return p
    raise RuntimeError(u"Could not find proper Payment Adapter class for control "
                       u"string: '%s'. Check payment factories!" % control)


POST_TO_PAYPAL_RESPONSE = u'''<!DOCTYPE html>
    <html>
        <head>
            <style type="text/css">
                html, body {
                    height: 100%%;
                    font-family: Artial, Helvetica, Sans-Serif;
                    color: #555;
                }
                form {
                    width: 60%%;
                    margin: 0 auto;
                }
                h1 {
                    margin-top: 20%%;
                    font-size: 32px;
                    font-weight: normal;
                }
                button {
                    color: #222;
                }
            </style>

            <script type="text/javascript">
                window.onload = function() {
                    var form = document.getElementById("paypal");
                    form.submit();
                };
            </script>
        </head>
        <body>
            <form id="paypal" action="%(paypal_url)s" method="POST">
                <input type="hidden" name="charset" value="utf-8">
                <input type="hidden" name="business" value="%(business)s">
                <input type="hidden" name="return" value="%(return)s">
                <input type="hidden" name="cancel_return" value="%(cancel_return)s">
                <input type="hidden" name="notify_url" value="%(notify_url)s">
                <input type="hidden" name="rm" value="1">

                <input type="hidden" name="currency_code" value="PLN">
                <input type="hidden" name="cmd" value="_cart">
                <input type="hidden" name="upload" value="1">
                <input type="hidden" name="no_shipping" value="1">

                <input type="hidden" name="custom" value="%(custom)s">
                <input type="hidden" name="amount_1" value="%(amount_1)s">
                <input type="hidden" name="item_name_1" value="%(item_name_1)s">

                <h1>Trwa przekierowywanie do serwisu PayPal,<br> może to potrwać kilka sekund...</h1>
                <p>W przypadku gdy automatyczne przekierowanie nie nastąpiło, proszę użyć
                przycisku poniżej.
                </p>
                <button type="submit">Przejdź do serwisu PayPal</button>
            </form>
        </body>
    </html>
'''