# -*- coding: utf-8 -*-
import os
import re

from django import template
from django.template import defaultfilters as df
from django.template.defaultfilters import stringfilter
from django.utils import simplejson

from dshop import settings


register = template.Library()

STATIC_PATH = settings.MEDIA_ROOT
rx = re.compile(r"^(.*)\.(.*?)$")
version_cache = {}


def clearVersionCache():
    version_cache = {}


@register.filter
def jsonify(obj):
    '''Serialize obj to JSON format.'''
    return simplejson.dumps(obj)


@register.filter
def sort(list, prop):
    '''Return new sorted list of objects by given property.'''
    return sorted(list, lambda x,y: cmp(x.getattr(prop), y.getattr(prop)))

@register.filter
def make_range(num):
    '''Make list [0 ... num-1] out of given integer number.'''
    return range(num)

@register.filter
@stringfilter
def slugify_pl(text):
    return df.slugify(text.replace(u'ł', u'l').replace(u'Ł', u'L'))

@register.filter
def money(value):
    '''Format decimal number according to Polish currency locale.'''
    if value is not None:
        return df.floatformat(value, -2).replace('.', ',') + u' zł'
    else:
        return ''

@register.filter
def number(value, precision=0):
    '''Format number according to Polish locales.'''
    return df.floatformat(value, precision).replace('.',',')

@register.filter
def us_num(value):
    return str(value)

@register.simple_tag
def version(path_string):
    '''Add file modification date to given filepath. Use it for static files versioning.'''
    def murl(fpath):
        return os.path.join(settings.MEDIA_URL, fpath)

    if settings.DEBUG and settings.STATICS_VERSIONING == 'name':
        return murl(path_string)
    try:
        if path_string in version_cache:
            mtime = version_cache[path_string]
        else:
            mtime = os.path.getmtime(os.path.join(STATIC_PATH, path_string))
            version_cache[path_string] = mtime

        if settings.STATICS_VERSIONING == 'name':
            return murl(rx.sub(r"\1.%d.\2" % mtime, path_string))
        else:
            return murl("%s?v=%d" % (path_string, mtime))
    except:
        return murl(path_string)


@register.filter
@stringfilter
def firstline(val, expand_str=' ...', max_length=20):
    '''Return first line of val. If val have more lines, expand_str is appended at the end.'''
    if '\n' in val:
        return val[:min(max_length, val.find('\n'))] + expand_str
    else:
        return val[:max_length] + (expand_str if len(val) > max_length else '')