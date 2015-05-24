# -*- coding: utf-8 -*-

from django.contrib import admin
from django.core.urlresolvers import reverse

from dshop import settings
from dshop.main import models

def system_params(request):
    return { 'sys_param' : dict(models.SystemParam.objects.values_list('key', 'value')) }

def page_fragments(request):
    res = {}
    if request.path.startswith('/'+settings.ADMIN_PREFIX):
        return res

    if request.path == reverse('mainpage'):
        fragments = models.PageFragment.objects.all()
    else:
        fragments = models.PageFragment.objects.exclude(location__startswith='mpage_')
    for f in fragments:
        if not f.location in res:
            res[f.location] = []
        res[f.location].append(f)
    
    return { 'fragments' : res }

def common(request):
    cmm = {
        'debug'        : settings.DEBUG,
        'on_production': settings.ON_PRODUCTION,
        'URL_PREFIX'   : settings.URL_PREFIX,
        'GA'           : settings.GOOGLE_ANALYTICS,
    }

    if not request.path.startswith('/'+settings.ADMIN_PREFIX):
        helpLinks = {}
        for hl in models.HelpLink.objects.all():
            helpLinks[hl.name] = hl

        meta = {
            'default' : {},
            'mpage' : {},
            'extra' : {}
        }
        for m in models.MetaInfo.objects.all():
            if m.default:
                meta['default'][m.name] = m
            elif m.mainpage:
                meta['mpage'][m.name] = m
            else:
                meta['extra'][m.name] = m

        cmm.update({
            'authLevel'   : request.session.get('auth_level', 0),
            'client'      : request.dshop.client,
            'cart'        : request.dshop.cart,
            'headerLinks' : models.AdditionalLink.objects.filter(location='header'),
            'footerLinks' : models.AdditionalLink.objects.filter(location='footer'),
            'helpLinks'   : helpLinks,
            'meta'        : meta,
        })
    
    return cmm
