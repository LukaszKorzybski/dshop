# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseServerError
from django.utils import simplejson
from django.core import serializers

from .templatetags import utils
from . import forms
from . import middleware

from dshop.main import models as m

JSONRPC_SERVICES = [
    "setCartItemParam",
    "setOrderNotes",
    "getArticle",
    "getProperties",
    "getArticleParam",
    "reportOpinionAbuse",
    "getArticleVariants"
]


def httpDontCache(f):
    '''Set cache preventing headers on HTTP response.'''
    def decorated(*args, **kwargs):
        response = f(*args, **kwargs)
        response['Cache-Control'] = "no-cache,max-age=0"
        response["Pragma"] = "no-cache"
        return response
    return decorated


def jsonrpc(f):
    '''Make JSON-RPC-like service from any django view.'''
    def decorated(request, *args, **kwargs):
        response = { 'version' : '1.1' }
        try:
            response['result'] = f(request, *args, **kwargs)
            httpresp = HttpResponse(simplejson.dumps(response))
        except Exception, exp:
            # TODO - error logging (mail need to be sent on unhandled exceptions)
            response['error'] = {
                'name' : 'JSONRPCError',
                'code' : 500,
                'message' : exp.message
            }
            httpresp = HttpResponseServerError(simplejson.dumps(response))
        httpresp['Content-Type'] = "application/json"
        return httpresp
    return decorated


class JsonRpcError(Exception):
    def __init__(self, code, *args, **kwargs):
        super(JsonRpcError, self).__init__(*args, **kwargs)
        self.code = code
    def __repr__(self):
        return "<JsonRpcError (%d, '%s')>" % (self.code, self.message)


@httpDontCache
@jsonrpc
def rpcController(request, method=""):
    '''Provide HTTP based JSON-RPC-like services. Accepts GET and POST requests.'''
    params = {}

    if request.method == 'POST':
        if 'params' in request.POST:
            params = dict([(str(x),y) for x,y in simplejson.loads(request.POST['params']).items()])
        method = request.POST.get('method', "")
    elif request.method == 'GET':
        params = dict([(str(x),y) for x,y in request.GET.items()])
        if 'id' in params:
            del params['id']
    else:
        raise JsonRpcError(100, "Bad call. Request type used is not supported.")

    if method in JSONRPC_SERVICES:
        #log.debug("rpcController: calling '%s' with params: %s" % (method, params))
        try:
            resp = globals()[method](request, **params)
        except Exception, e:
            #log.error("rpcController: '%s' failed with: '%s: %s'. Parameters: %s." % (method, e.__class__.__name__, str(e), params))
            raise JsonRpcError(500, e.message)
    else:
        raise JsonRpcError(100, "Bad call. Unrecognized method '%s'." % method)
    return resp


def setCartItemParam(request, orderMode=False, **kwargs):
    f = forms.CartItemParamForm(kwargs)
    if not f.is_valid():
        raise Exception('Invalid arguments. %s' % str(f.errors))
    
    if orderMode:
        cart = m.Order.objects.temp().get(id=f.cleaned_data['order_id'], client=request.dshop.client)
    else:
        cart = request.dshop.cart

    item = cart.item_set.get(article_id=f.cleaned_data['article'])
    item.param_value = f.cleaned_data['param']
    item.save()

    return {
        "param" : f.cleaned_data['param'],
        "firstline" : utils.firstline(f.cleaned_data['param'])
    }


def getArticleParam(request, name='', id=None):
    if id:
        param = m.ArticleParam.objects.get(pk=id)
    else:
        param = m.ArticleParam.objects.get(name=name)
    return {'param' : serializers.serialize("json", [param]) }


def setOrderNotes(request, **kwargs):
    f = forms.OrderNotesForm(kwargs)
    if not f.is_valid():
        raise Exception('Invalid arguments. %s' % str(f.errors))
    
    try:
        order = m.Order.objects.temp().get(id=f.cleaned_data['id'], client=request.dshop.client)
    except:
        raise Exception('Order not found. id=%s' % f.cleaned_data['id'])

    order.comments = f.cleaned_data.get('notes', u'')
    order.save()
    return { 'notes' : order.comments }


# TODO this is a security hole - clients discounts can be fetched, should be possible
# only when current user is in staff.
def getArticle(request, pk, client=None):
    art = m.Article.objects.select_related('unit').get(id=int(pk))
    res = { 'article' : serializers.serialize("json", [art]) }

    abstr_article = art.get_abstr_article()
    if abstr_article:
        discount = art.get_abstr_article().inject_client(client).best_discount
        if discount.notNone:
            res['discount'] = serializers.serialize("json", [discount])
    return res


def getProperties(request, spec_id):
    prop_members = m.PropertyMembership.objects.filter(spec=int(spec_id)).select_related(depth=1)
    return { 
        'prop_members' : serializers.serialize("json", prop_members),
        # TODO this is a workaround of lack support for deep serialization, should we use Piston ?
        'properties'   : serializers.serialize("json", [p.prop for p in prop_members])
    }

def getArticleVariants(request, sarticle_id):
    try:
        sarticle = m.ShopArticle.objects.get(pk=sarticle_id)
    except m.ShopArticle.DoesNotExist:
        return { 'status' : 'not-found' }

    res = { 'sarticle' : serializers.serialize("json", [sarticle]) }
    if sarticle.variants:
         res['variants'] = serializers.serialize("json", [v for v in sarticle.variant_set.all()])
    return res

def reportOpinionAbuse(request, opinion_id):
    if m.SystemParam.get("opinions_abuse_reports") != "1":
        raise Exception("Abuse reporting is not supported.")
    
    opinion = m.Opinion.objects.get(id=int(opinion_id))
    opinion.abuse_count += 1
    opinion.save()
    return 'OK'