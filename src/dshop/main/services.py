# -*- coding: utf-8 -*-
#
# TODO: move these methods to appropriate models when models will be moved to django ?

import premailer

from django.template import loader, Context
from django.core.mail import EmailMultiAlternatives

from dshop import settings
from dshop import utils as dutils
from dshop.main import gateways
from dshop.main import models as m

def send_registration_email(client):
    ctx = Context({ 'client' : client })
    _send_alternative_email([client.email], u'Aktywuj swoje konto', 'email/registration', ctx)

def send_password_recover_email(email, password):
    ctx = Context({ 'email': email, 'password': password })
    _send_alternative_email([email], u'Odzyskaj hasło', 'email/recover-password', ctx)

def send_new_order_email(order):
    ctx = Context({
        'company'   : m.Company.objects.all()[0],
        'order'     : order,
        'baseCart'  : order,
        'orderYear' : int(order.created.year)
    })
    _send_alternative_email([order.client.email],
                            u'Złożono zamówienie nr %s' % order.number,
                            'email/new-order',
                            ctx)

def send_status_change_email(order):
    subjects = {
        'AC' : u'przekazane do realizacji',
        'RJ' : u'odrzucone',
        'SE' : u'wysłane',
        'CA' : u'anulowane'
    }
    assert order.status in subjects, u'Order status "%s" is not supported.' % order.status
    
    ctx = Context({
        'company'   : m.Company.objects.all()[0],
        'order'     : order,
        'baseCart'  : order,
        'orderYear' : int(order.created.year)
    })
    _send_alternative_email([order.client.email],
                            u'Zamówienie nr %s %s' % (order.number, subjects[order.status]),
                            'email/order-status-%s' % order.status.lower(),
                            ctx)

def send_request_for_opinion(order):
    ctx = Context({
        'company'   : m.Company.objects.all()[0],
        'order'     : order,
        'baseCart'  : order,
        'orderYear' : int(order.created.year),
        'sys_param' : dict(m.SystemParam.objects.values_list('key', 'value'))
    })
    _send_alternative_email([order.client.email],
                            u'Zapraszamy ponownie',
                            'email/req-for-opinion',
                            ctx)

def send_employee_msg(order, msg):
    ctx = Context({
        'company'   : m.Company.objects.all()[0],
        'order'     : order,
        'baseCart'  : order,
        'orderYear' : int(order.created.year),
        'employee_msg' : msg
    })
    _send_alternative_email([order.client.email],
                            u'Zamówienie nr %s - wiadomość od obsługi' % order.number,
                            'email/employee-message',
                            ctx)

def _send_alternative_email(recipients, subject, template, ctx):
    ctx['SSL_PROTO'] = settings.SSL_PROTO
    ctx['HOST_NAME'] = settings.HOST_NAME
    ctx['MEDIA_URL'] = settings.MEDIA_URL
    ctx['title'] = subject

    txt_tmpl = loader.get_template(template + '.txt')
    html_tmpl = loader.get_template(template + '.html')

    html_src = html_tmpl.render(ctx).replace('\r\n', '\n').replace('\r', '\n')
    html = premailer.transform(html_src, base_url=u'http://'+settings.HOST_NAME)

    email = EmailMultiAlternatives(subject=subject,
                         body=txt_tmpl.render(ctx),
                         to=recipients)
    email.attach_alternative(html, 'text/html')
    gateways.email.send(email)
