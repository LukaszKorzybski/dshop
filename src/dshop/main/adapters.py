# -*- coding: utf-8 -*-

from decimal import Decimal

from dshop import dotpay
from dshop.main import models as m

class DotPayBuyer(dotpay.Buyer):
    '''Wraps domain.Client object.'''
    def __init__(self, client):
        super(DotPayBuyer, self).__init__(client)
    def firstName(self):
        return self.buyer.first_name
    def lastName(self):
        return self.buyer.last_name
    def email(self):
        return self.buyer.email
    def street(self):
        return self.buyer.street
    def streetNumber(self):
        return self.buyer.number
    def town(self):
        return self.buyer.town
    def postCode(self):
        return self.buyer.code
    def country(self):
        return 'PL'
    def phone(self):
        return self.buyer.phone
    def language(self):
        return 'pl'


class DShopPayment(dotpay.Payment):
    '''Abstract payment adapter for dshop orders (models.Order objects).'''
    def __init__(self, payment=None):
        super(DShopPayment, self).__init__(payment)

    def id(self):
        return self.payment.id

    def control(self):
        return 'dshop:'+str(self.payment.id)

    def amount(self):
        return self.payment.discount_gross().quantize(Decimal('1.00'))

    def description(self):
        return u'Zamówienie nr %s' % self.payment.number

    def statusUrl(self):
        raise NotImplementedError()

    def loadPayment(self, control):
        self.payment = m.Order.objects.get(id=int(control[6:]))

    def updatePaymentStatus(self, status, trans_num, amount):
        self.payment.payment_status = status
        self.payment.payment_trans_num = trans_num
        self.payment.payment_amount = amount
        self.payment.save()

    def shouldUpdateStatus(self, status):
        if self.payment.payment == m.Order.Payment.ONLINE:
            return True
        else:
            return False

class DotPayPayment(DShopPayment):
    '''DotPay payment adapter for DShop orders.'''
    def __init__(self, payment=None):
        super(DotPayPayment, self).__init__(payment)

    def statusUrl(self):
        return 'https://ssl.dotpay.pl/login.php?show=40&nt=%s' % self.payment.payment_trans_num

class PayPalPayment(DShopPayment):
    '''PayPal payment adapter for DShop orders.'''
    def __init__(self, payment=None):
        super(PayPalPayment, self).__init__(payment)

    def statusUrl(self):
        raise NotImplementedError()

    def updatePaymentStatus(self, status, trans_num, amount):
        status_mapping = {
            'In-Progress' : 1,
            'Pending' : 1,
            'Completed' : 2,
            'Denied' : 3,
            'Failed' : 3,
            'Refunded' : 4,
            'Reversed' : 4
        }
        return super(PayPalPayment, self).updatePaymentStatus(
            status_mapping.get(status, 0), trans_num, amount)


def getDotPayAdapterClass(control):
    if control.startswith('dshop:'):
        return DotPayPayment

def getPayPalAdapterClass(control):
    if control.startswith('dshop:'):
        return PayPalPayment

def getBuyerAdapter(online_provider):
    pass
