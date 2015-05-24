# -*- coding: utf-8 -*-

from django import template

from dshop.main import models as m

register = template.Library()

#### DShop specific tags and filters

@register.filter
def d_exectime(etime, helpurl=None):
    if type(etime) == str:
        return etime
    if not etime.isNone():
        return unicode(etime)
    elif helpurl:
        return u'<a href="%s" class="new-window" title="Pokaż dane kontaktowe">zapytaj</a>' % helpurl
    else:
        return u'zapytaj'

@register.filter
def paging(page, baseurl='', sect_id='article-list'):
    html = [u'<ul class="paging">']

    if page.prev:
        html.append('<li class="prev" title="Poprzednia strona"><a href="%s%d/#%s"></a></li>' % (baseurl, page.prev, sect_id))
    if page.page_num > 1:
        html.append('<li><a href="%s1/#%s">1</a></li>' % (baseurl, sect_id))
    if page.page_num > 5:
        html.append('<li>...</li>')
    for p in page.prev_pages:
        html.append('<li><a href="%s%d/#%s">%d</a></li>' % (baseurl, p, sect_id, p))

    html.append('<li class="current">%d</li>' % page.page_num)

    for p in page.next_pages:
        html.append('<li><a href="%s%d/#%s">%d</a></li>' % (baseurl, p, sect_id, p))
    if page.page_num < page.total_pages - 4:
        html.append('<li>...</li>')
    if page.page_num < page.total_pages:
        html.append('<li><a href="%s%d/#%s">%d</a></li>' % (baseurl, page.total_pages, sect_id, page.total_pages))
    if page.next:
        html.append(u'<li class="next"><a href="%s%d/#%s" title="Następna strona"></a></li>' % (baseurl, page.next, sect_id))

    html.append('</ul><ul class="clear"></ul>')
    return ''.join(html)


STATUSES_DICT = dict(m.Order.STATUS_CHOICES)
@register.filter
def order_status(status):
    return STATUSES_DICT.get(status, 'b.d.')


PAYMENTS_DICT = dict(m.Order.PAYMENT_CHOICES)
@register.filter
def order_payment(payment):
    return PAYMENTS_DICT.get(payment, u'b.d.')


@register.filter
def cat_tree_qs(cl, cat_id=None):
    '''Filter for CategoryTreeAdmin'''
    if cat_id:
        return cl.get_query_string({ cl.model_admin.CAT_TREE_VAR + '__id__exact': cat_id })
    else:
        return cl.get_query_string({}, [cl.model_admin.CAT_TREE_VAR + '__id__exact'])