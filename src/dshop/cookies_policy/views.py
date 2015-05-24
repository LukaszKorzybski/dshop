# -*- coding: utf-8 -*-
from django.template.context import RequestContext
from django.template import Context, loader
from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404
import datetime

def cookies_accept(request):
    template = 'cookies_policy/cookies_policy.html'
    c = Context({
                'cookie_domain': '<a href="http://sklep.optionall.pl" title="sklep.optionall.pl">sklep.optionall.pl</a>' 
    })
    
    response = render_to_response(template, c, RequestContext(request))
    response.set_cookie('optionall-cookie-info','1',365*24*60*60)
    return response      
