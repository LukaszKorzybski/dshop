# -*- coding: utf-8 -*-

from datetime import datetime
import re
from os import path

from django.http import Http404, HttpResponseNotFound, HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponsePermanentRedirect
from django.template import RequestContext
from django.template import loader
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.utils import http
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.validators import validate_email
from django.contrib.auth import models as auth_models

from dshop import settings
from dshop import dotpay
from dshop import paypal
from dshop.main import forms
from dshop.main import services
from dshop.main import models as m
from dshop.main import adapters
from dshop.main import fts
from dshop.main.decorators import login_required
from dshop.main.decorators import logout_required

old_category_map = {}

def load_oldcat_mapping():
    with open(path.join(settings.WEBAPP_ROOT_DIR, 'category_map.txt'), 'r') as f:
        for line in f:
            old_category_map[int(line.split(':')[0])] = int(line.split(':')[1])
load_oldcat_mapping()

def inclCommons(ctx, navData=True, randomArticles=False):
    '''Insert, into given dictionary, data needed by some of the pages.

       @param navData set to False if data for main navigation is not needed (for eg. login page).
       @param randomArticles set to True if you want to display random articles.
    '''
    if navData:
        ctx['mainGroups'] = m.Category.objects.main_categories()
        ctx['producers'] = m.Producer.publics.toplist()
    if randomArticles:
        ctx['randomArticles'] = []
    return ctx

def dologin(request, client, sessionAge=0, auth=False):
    '''login given client into dshop, client gets second level of authorization.'''
    request.session['login_time'] = datetime.now()
    request.session['client_id'] = client.id
    request.session['auth_level'] = 2
    request.session.set_expiry(sessionAge)

    # attach current cart to client or replace current, empty cart with client's cart.
    if not auth:
        cart = request.dshop.cart
        if cart.item_count():
            client.replace_cart(cart)
        else:
            cart.delete()
            client_cart = client.get_cart()
            client_cart.session_key = request.session.session_key
            client_cart.refresh_items()
            request.session['cart_id'] = client_cart.id


def getRefererPath(request):
    '''Return http referer path. Returns mainpage path if referer is external site.'''
    prefix = settings.HOST_NAME + settings.URL_PREFIX
    ref = request.META.get('HTTP_REFERER', '')
    idx = ref.find(prefix)
    if idx == -1:
        return reverse(mainpage)
    return ref[idx+len(prefix):]


def modifyCart(request, cart):
    '''Perform cart operations.'''
    action = request.POST.get('action', '')
    
    if action == "add":
        f = forms.Add2CartForm(request.POST)
        if f.is_valid():
            if f.cleaned_data['variant']:
                abstr_article = m.ArticleVariant.objects.get(pk=f.cleaned_data['variant'])
            else:
                abstr_article = m.ShopArticle.publics.get(pk=f.cleaned_data['article'])
            cart.add_item(abstr_article, f.cleaned_data['qty'])
    
    elif action == "remove":
        f = forms.RemoveFromCartForm(request.POST)
        if f.is_valid():
            cart.remove_item(f.cleaned_data['article'])
    
    elif action == "recalc":
        f = forms.RecalcCartForm(cart, request.POST)
        if f.is_valid():
            cart.recalc_items(f.cleaned_data)
    
    elif action == "clear":
        cart.clear()
    
    cart.save()


def setOrderPayment(request, order):
    '''Set payment method for given order, using data from POST data.'''
    payment = request.POST.get('payment', 'TR')
    if payment not in ('TR', 'ON', 'CA', 'DE'):
        return
    
    order.payment = payment
    order.save()
    if payment == "CA":
        shipment = order.shipment()
        m.Shipper.assign_to(shipment)
        shipment.save()
    return

def recoverPassword(request):
    if request.method == "POST":
        form = forms.PasswordRecoverForm(request.POST)
        try:
            if form.is_valid():
                email = form.cleaned_data['email']
                validate_email(email)
                client = m.Client.objects.get(login=email)
                password = auth_models.User.objects.make_random_password()
                client.set_password(password)
                client.save()
                services.send_password_recover_email(email, password)
        except Exception, e:
            pass 
        return HttpResponseRedirect(reverse(passwordRecovered))
    else:
        form = forms.PasswordRecoverForm()
        return render_to_response('recover_password.html', { 'form': form }, context_instance=RequestContext(request))

def passwordRecovered(request):
    return render_to_response('password_recovered.html', {}, context_instance=RequestContext(request))

def login(request, auth=False):
    ctx = {}
    def render_login(form):
        ctx['form'] = form
        request.session.set_test_cookie()
        return render_to_response('auth.html' if auth else 'login.html', ctx, context_instance=RequestContext(request))
    
    if request.method == "POST":
        form = forms.LoginForm(request.POST)
        if not form.is_valid():
            ctx['errmsg'] = 'login-invalid'
            return render_login(form)
        uname, passwd = form.cleaned_data['username'], form.cleaned_data['password']
        
        if not request.session.test_cookie_worked():
            # login failed, please turn on cookies
            ctx['errmsg'] = 'cookies-disabled'
            return render_login(form)

        try:
            client = m.Client.objects.get(login=uname)
        except m.Client.DoesNotExist:
            ctx['errmsg'] = 'login-invalid'
            return render_login(form)

        if client.check_password(passwd):
            if client.active:
                # login successful
                request.session.delete_test_cookie()
                if form.cleaned_data['remember']:
                    dologin(request, client, settings.SESSION_COOKIE_AGE, auth)
                else:
                    dologin(request, client, auth=auth)
                return HttpResponseRedirect(form.cleaned_data['next'])
            else:
                # login failed, account inactive
                ctx['errmsg'] = 'inactive'
                return render_login(form)
        else:
            # login failed, wrong password
            ctx['errmsg'] = 'login-invalid'
            return render_login(form)
    else:
        form = forms.LoginForm({
                'next' : request.GET.get('next', settings.LOGIN_REDIRECT_URL),
                'remember' : (not request.session.get_expire_at_browser_close()) if auth else True
        })
    
    return render_login(form)


def logout(request):
    cart = request.dshop.cart
    if not cart.client:
        cart.delete()
    
    request.session.clear()
    request.session.flush()
    return HttpResponseRedirect(reverse(mainpage))


def alreadyLoggedIn(request):
    return render_to_response('already_logged_in.html', {},
                                        context_instance=RequestContext(request))


@logout_required
def register(request):
    ctx = {}
    
    if request.method == "POST":
        form = forms.RegisterForm(request.POST)
        if form.is_valid():
            client = form.createClient()
            client.save()
            services.send_registration_email(client)
            return HttpResponseRedirect(reverse(thankYou, kwargs={ 'email' : client.email }))
    else:
        form = forms.RegisterForm()

    ctx['form'] = form
    return render_to_response('register.html', ctx,
                                        context_instance=RequestContext(request))


@logout_required
def activate(request, login, key):
    try:
        client = m.Client.objects.get(login=login)
    except m.Client.DoesNotExist:
        client = None

    if client and client.activation_code == key:
        client.active = True
        client.save()
        dologin(request, client)
        return HttpResponseRedirect(reverse(activated))
    
    return render_to_response('activation_failed.html', {},
                                        context_instance=RequestContext(request))



@login_required(1)
def activateCard(request):
    ctx = {}
    if request.method == "POST":
        form = forms.ActivateCardForm(request.POST, request.dshop.client)

        if form.is_valid():
            form.client.kartaAktywna = True
            form.client.numerKlienta = form.cleaned_data['clientNumber']
            form.client.kartaWydana = True
            slayer.AdministracjaKlient.updateKlient(form.client)

            card = m.ClientCard.objects.get(number=form.cleaned_data['clientNumber'])
            card.activated = datetime.now()
            card.save()
            return HttpResponseRedirect(reverse(cardActivated))
    else:
        form = forms.ActivateCardForm()

    ctx['form'] = form
    return render_to_response('activate_card.html', ctx,
                                    context_instance=RequestContext(request))



def cardActivated(request):
    return render_to_response('card_activated.html', {},
                                    context_instance=RequestContext(request))



@logout_required
def thankYou(request, email):
    ctx = { 'email' : email }
    return render_to_response('thank_you.html', ctx,
                                        context_instance=RequestContext(request))



@login_required(2)
def activated(request):
    return render_to_response('client_activated.html', {},
                                        context_instance=RequestContext(request))



@login_required(2)
def completeProfile(request, ref=""):
    if request.dshop.client.profile_complete:
        return HttpResponseRedirect(reverse(myAccount))
    
    ctx = {}
    if request.method == "POST":
        form = forms.CompleteProfileForm(request.POST)
        if form.is_valid():
            form.updateClient(request.dshop.client)
            request.dshop.client.save()
            if ref == 'neworder':
                return HttpResponseRedirect(reverse(createOrder))
            else:
                return HttpResponseRedirect(reverse(myAccount)+'?m=pcompleted')
    else:
        form = forms.CompleteProfileForm()
    ctx['msg'] = ref
    ctx['form'] = form
    ctx['areHere'] = [(u"moje konto", reverse(myAccount)), (u"uzupełnij profil", None)]
    return render_to_response('complete_profile.html', ctx,
                                        context_instance=RequestContext(request))



def mainpage(request):
    ctx = inclCommons({})
    ctx['news'] = m.News.publics.all()[:6]
    ctx['opinions'] = m.Opinion.objects\
            .filter(blocked=False)\
            .filter(abuse_count=0)\
            .exclude(content=u'')\
            .select_related('article')[:3]

    qs = m.ShopArticle.publics.select_related('article__promotion', 'r_main_photo')
    promo = qs.filter(frontpage=True, article__promotion__isnull=False)
    new = qs.filter(frontpage=True, new=True, article__promotion__isnull=True)
    week = qs.filter(frontpage=True, new=False, article__promotion__isnull=True)
    
    ctx['promoL'], ctx['promoR'] = [], []
    ctx['newL'], ctx['newR'] = [], []
    ctx['weekL'], ctx['weekR'] = [], []
    for i, p in enumerate(promo[:4]):
        if i%2 == 0:
            ctx['promoL'].append(p)
        else:
            ctx['promoR'].append(p)
    for i, p in enumerate(new[:4]):
        if i%2 == 0:
            ctx['newL'].append(p)
        else:
            ctx['newR'].append(p)
    for i, p in enumerate(week[:4]):
        if i%2 == 0:
            ctx['weekL'].append(p)
        else:
            ctx['weekR'].append(p)
    
    return render_to_response('main_page.html', ctx,
                                        context_instance=RequestContext(request))



def producers(request):
    ctx = inclCommons({})
    
    prods = m.Producer.publics.all()
    slice1 = len(prods)/3
    slice2 = (len(prods)/3)*2
    letter1 = prods[slice1].first_letter
    letter2 = prods[slice2].first_letter
    
    while slice1 < slice2:
        if prods[slice1].first_letter != letter1:
            break
        slice1 += 1
    while slice2 < len(prods):
        if prods[slice2].first_letter != letter2:
            break
        slice2 += 1
    ctx['prods1'], ctx['prods2'], ctx['prods3'] = prods[:slice1], prods[slice1:slice2], prods[slice2:]
    
    return render_to_response('producers.html', ctx,
                                context_instance=RequestContext(request))



def articles(request, view='', group=None, producer=None, mprod=None, page="1", slug='', gslug=''):
    ctx = inclCommons({})

    ctx['view'] = view
    group = get_object_or_404(m.Category.objects, id=int(group)) if group else None
    producer = int(producer) if producer else None    

    qs = m.ShopArticle.publics.all()

    if group:
        ctx['group'] = group
        ctx['showGPath'] = True
    else:
        ctx['showGPath'] = False

    if view =="group":
        title = group.name
        ctx['pagingPrefix'] = reverse('articles-group', args=[group.id, group.slug])
        if group.level == 0:
            ctx['showGPath'] = False;

    elif view == "prod":
        ctx['producer'] = get_object_or_404(m.Producer.objects, id=producer)
        title = ctx['producer'].name
        if group:
            title += (' / %s' % group.name)
            ctx['pagingPrefix'] = reverse('articles-prod-g', args=[producer, slug, group.id, group.slug])
        else:
            ctx['pagingPrefix'] = reverse('articles-prod', args=[producer, slug])
        qs = qs.filter(producer=producer)
    
    elif view == "mprod":
        ctx['mprod'] = get_object_or_404(m.MetaProducer.objects, id=mprod)
        title = ctx['mprod'].name
        if group:
            title += (' / %s' % group.name)
            ctx['pagingPrefix'] = reverse('articles-mprod-g', args=[mprod, slug, group.id, group.slug])
        else:
            ctx['pagingPrefix'] = reverse('articles-mprod', args=[mprod, slug])
        qs = qs.filter(producer__in=ctx['mprod'].prod_ids_list)
    
    elif view == 'new':
        title = u"Nowości"
        if group:
            title += (' / %s' % group.name)
            ctx['pagingPrefix'] = reverse('articles-new-g', args=[group.id, group.slug])
        else:
            ctx['pagingPrefix'] = reverse('articles-new')
        qs = qs.filter(new=True)

    elif view == 'promo':
        title = u"Promocje"
        if group:
            title += (' / %s' % group.name)
            ctx['pagingPrefix'] = reverse('articles-promo-g', args=[group.id, group.slug])
        else:
            ctx['pagingPrefix'] = reverse('articles-promo')
        qs = qs.filter(article__promotion__isnull=False)
    else:
        raise Http404()

    titlePage = " - Strona " + page if page != "1" else ""
    h1Page = " / " + page if page != "1" else ""
    
    ctx['headTitle'] = title + titlePage
    ctx['title'] = title + h1Page
    ctx['articles'], ctx['gtree'] = fts.get_articles(qs, group, page=int(page), sort='name')
    ctx['gpath'] = group.get_ancestors() if group else []
    
    return render_to_response('articles.html', ctx,
                                context_instance=RequestContext(request))



def search(request, text="", group=None, page="1", slug=''):
    ctx = inclCommons({})
    
    if not text:
        text = request.GET.get('text', '')
    ctx['searchText'] = re.sub('\s+', ' ', text).strip()
    
    phrase = re.sub('\s+', ' ', re.compile('[^\s\w]', re.UNICODE).sub(' ', text)).strip()

    group = get_object_or_404(m.Category.objects, id=int(group)) if group else None
    if group:
        ctx['group'] = group
        ctx['pagingPrefix'] = reverse('dshop-search-g', args=[text, group.id, group.slug])
    else:
        ctx['pagingPrefix'] = reverse('dshop-searchtxt', args=[text])

    
    if len(phrase) < 2:
        ctx['tooShort'] = True
    else:
        articles, gtree = fts.search_articles(phrase, group=group, page=int(page))
        ctx['articles'], ctx['gtree'] = articles, gtree

    ctx['gpath'] = group.get_ancestors() if group else []

    return render_to_response('search.html', ctx,
                                context_instance=RequestContext(request))


def article(request, id, slug='', page="1"):
    ctx = inclCommons({})
    opinions_active = True if m.SystemParam.get("opinions_active") == "1" else False
    article = get_object_or_404(m.ShopArticle.publics, id=int(id))

    if opinions_active:
        if request.method == "POST":
            f = forms.AddOpinionForm(request.POST, client=request.dshop.client)
            if f.is_valid():
                f.save()
                return HttpResponseRedirect(reverse('article-slug', args=[article.id, slug]) + '#opinions')
            else:
                ctx['opinions_form_invalid'] = True
        else:
            f = forms.AddOpinionForm(initial={ 'article': article.id  }, client=request.dshop.client)
        ctx['opinion_form'] = f
    
    ctx['article'] = article.inject_client(request.dshop.client)

    ctx['photos'] = article.neverempty_photo_set()
    ctx['many_photos'] = True if len(ctx['photos']) > 1 else False
    
    ctx['diff_price'] = article.diff_price_variants
    if ctx['diff_price']:
        ctx['main_variant'] = article.main_variant()

    if opinions_active:
        ctx['max_rating'] = int(m.SystemParam.get("opinions_max_rating"))

        if article.opinion_count:
            op_paginator = Paginator(article.active_opinions(), int(m.SystemParam.get("opinions_page_size")))
            page = int(page)
            try:
                opinions = op_paginator.page(page)
            except (EmptyPage, InvalidPage):
                opinions = op_paginator.page(op_paginator.num_pages)

            ctx['opinions'] = opinions
        

    return render_to_response('article.html', ctx,
                                context_instance=RequestContext(request))


@login_required(2)
def createOrder(request):
    if not request.dshop.client.profile_complete:
        return HttpResponseRedirect(reverse('dshop-cprofile-neworder'))
    order = m.Order.create_from(request.dshop.cart)
    return HttpResponseRedirect(reverse(newOrderEdit, args=[order.id]))


@login_required(2)
def newOrderEdit(request, id):
    ctx = {}
    order = get_object_or_404(m.Order.objects.temp(), id=int(id), client=request.dshop.client)
    postReturn = reverse(newOrderEdit, args=[order.id])

    if request.method == "POST":
        shipment = order.shipment()
        act = request.POST.get('action', '')
        if act == 'courier':
            shipper = m.Shipper.objects.get(name=request.POST.get('courier', ''))
            shipper.assign(shipment)
            shipment.save()
        else:
            orig_shipper = shipment.shipper_name;
            modifyCart(request, order)
            modifyCart(request, request.dshop.cart)
            if order.item_count():
                m.Shipper.assign_to(shipment)
                if orig_shipper != shipment.shipper_name:
                    postReturn = postReturn + '?nc='+http.urlquote(shipment.shipper_name)
                shipment.save()
            else:
                order.delete()
                postReturn = reverse(cart)+'?ret=/'
        
        return HttpResponseRedirect(postReturn)

    ctx['menu'] = 'new-order'
    ctx['areHere'] = [(u"Nowe zamówienie", None), (u'koszyk i dostawa', None)]
    ctx['newCourier'] = request.GET.get('nc', '')
    ctx['couriers'] = [s.evaluate_params(order) for s in m.Shipper.objects.all()]
    ctx['order'] = order
    ctx['baseCart'] = order
    ctx['paramForm'] = forms.CartItemParamForm()
    ctx['notesForm'] = forms.OrderNotesForm(initial={ 'id' : order.id })
    ctx['return_url'] = request.session.get('cart_return_url')
    return render_to_response('new_order.html', ctx,
                                context_instance=RequestContext(request))


@login_required(2)
def newOrderPayment(request, id):
    ctx = {}
    paymentFailed = False

    if request.GET.get('p', '') == 'failed' or request.POST.get('paymentFailed', '') == '1':
        order = get_object_or_404(m.Order.objects, id=int(id), client=request.dshop.client)
        paymentFailed = True
    else:
        order = get_object_or_404(m.Order.objects.temp(), id=int(id), client=request.dshop.client)
    
    if request.method == "POST":
        setOrderPayment(request, order)
        if not paymentFailed:
            order.submit()
            order.save()
            services.send_new_order_email(order)
            request.dshop.cart.clear()

        if order.payment == "ON":
            return HttpResponseRedirect(dotpay.getRedirectUrl(adapters.DotPayBuyer(request.dshop.client),
                                                              adapters.DotPayPayment(order),
                                                              reverse(newOrderSummary, args=[order.id])))
            #return HttpResponseRedirect(paypal.getRedirectUrl(None,
            #                                                  adapters.PayPalPayment(order),
            #                                                  reverse(newOrderSummary, args=[order.id])))

        else:
            return HttpResponseRedirect(reverse(newOrderSummary, args=[order.id]))
    
    ctx['paymentFailed'] = paymentFailed
    ctx['menu'] = 'new-order-payment'
    ctx['order'] = order
    ctx['courier'] = m.Shipper.objects.get(name=order.shipment().shipper_name)
    ctx['areHere'] = [(u"Nowe zamówienie", None), (u'wybór płatności', None)]
    return render_to_response('new_order_payment.html', ctx,
                                context_instance=RequestContext(request))


@login_required(2)
def newOrderSummary(request, id):
    if request.GET.get('status', '') == 'FAIL':
        order = get_object_or_404(m.Order.objects, id=int(id), client=request.dshop.client)
        return HttpResponseRedirect(reverse(newOrderPayment, args=[order.id])+'?p=failed')
    else:
        order = get_object_or_404(m.Order.objects, id=int(id), client=request.dshop.client)
    
    ctx = { 'menu' : 'new-order-summary' }
    ctx['order'] = order
    ctx['company'] = m.Company.objects.all()[0]
    ctx['baseCart'] = ctx['order']
    ctx['areHere'] = [(u"Nowe zamówienie", None), (u'podsumowanie', None)]
    return render_to_response('new_order_summary.html', ctx,
                                context_instance=RequestContext(request))


def cart(request):
    ctx = inclCommons({})
    scart = request.dshop.cart

    ref = getRefererPath(request)
    if not ref.startswith(reverse(cart)):
        if 'ret' in request.GET:
            request.session['cart_return_url'] = request.GET['ret']
        else:
            request.session['cart_return_url'] = ref
    
    if request.method == "POST":
        modifyCart(request, scart)
        return HttpResponseRedirect(reverse(cart))

    ctx['baseCart'] = scart
    ctx['paramForm'] = forms.CartItemParamForm()
    ctx['return_url'] = request.session.get('cart_return_url', '')

    return render_to_response('cart.html', ctx,
                                context_instance=RequestContext(request))


@login_required(2)
def myAccount(request):
    ctx = { 'menu' : 'myaccount' }
    client=request.dshop.client

    if request.method == "POST":
        action = request.POST.get('action', None)
        
        if action == "pwdchange":
            form = forms.MyProfileForm(initial=client)
            pwdForm = forms.ChangePasswdForm(request.POST)
            if pwdForm.is_valid():
                client.set_password(pwdForm.cleaned_data['password'])
                client.save()
                return HttpResponseRedirect(reverse(myAccount)+"?m=pchanged")
        else:
            form = forms.MyProfileForm(request.POST, type=client.type)
            pwdForm = forms.ChangePasswdForm()
            if form.is_valid():
                form.updateClient(client)
                client.save()
                return HttpResponseRedirect(reverse(myAccount)+"?m=dchanged")
    else:
        pwdForm = forms.ChangePasswdForm()
        form = forms.MyProfileForm(initial=client)

    ctx['form'] = form
    ctx['pwdForm'] = pwdForm
    return render_to_response('my_account.html', ctx,
                        context_instance=RequestContext(request))


@login_required(2)
def myOrders(request, year=None):
    client = request.dshop.client
    ctx = { 'menu' : 'myorders' }

    years = client.orders_year_list()
    if years and (not year or int(year) not in [y[0] for y in years]):
        return HttpResponseRedirect(reverse(myOrders, args=[years[0][0]]))
    if year:
        ctx['year'] = int(year)
        ctx['orders'] = m.Order.objects.filter(client=client, created__year=int(year))
    
    ctx['years'] = years
    return render_to_response('my_orders.html', ctx,
                        context_instance=RequestContext(request))


@login_required(2)
def myOrder(request, year, order):
    order = get_object_or_404(m.Order.objects, id=int(order), client=request.dshop.client)
    ctx = {
        'year'  : year,
        'menu' : 'myorders',
        'areHere' : [(u'moje zamówienia', reverse('dshop-myorders-year', args=[year])),
                     (u'zamówienie %s' % order.number, )],
        'order' : order,
        'baseCart' : order
    }
    return render_to_response('my_order.html', ctx,
                        context_instance=RequestContext(request))


@login_required(2)
def myDiscounts(request):
    ctx = {
        'menu' : 'mydiscounts',
        'discounts' : request.dshop.client.discount_set.all()
    }
    return render_to_response('my_discounts.html', ctx,
                        context_instance=RequestContext(request))


def static(request, key, id, preview=False):
    ctx = inclCommons({})
    if preview:
        spage = get_object_or_404(m.StaticPage.objects, id=id)
    else:
        spage = get_object_or_404(m.StaticPage.publics, id=id)
    ctx['spage'] = spage
    ctx['areHere'] = [(p.title, p.get_absolute_url()) for p in spage.get_ancestors()] + [(spage.title, spage.get_absolute_url())]
    return render_to_response('static_page.html', ctx,
                                context_instance=RequestContext(request))


def news(request):
    ctx = inclCommons({})
    ctx['news'] = m.News.publics.all()
    return render_to_response('news.html', ctx,
                                context_instance=RequestContext(request))


def paymentStatusUpdate(request):
    #return paypal.updatePaymentStatusView(request)
	return dotpay.updatePaymentStatusView(request)

def b2b_sync(request, what, who, dt=''):
    from datetime import datetime, timedelta
    from random import random
    
    if dt:
        dt = datetime.strptime(dt, '%d-%m-%Y %H:%M')
    else:
        dt = datetime.now()

    count = m.ShopArticle.objects.filter(producer__name=who).count()   
 
    if what in ['stock', 'price']:
        secs = round(random() * 59) + count/2 
        dt = dt + timedelta(0, secs)
    
    if what == 'stock':
        msg = u'Wykonano aktualizację stanów magazynowych. Dostawca: %s, liczba zaktualizowanych produktów: %d' % (who, count)
    elif what == 'price':
        msg = u'Wykonano aktualizację cen. Dostawca: %s, liczba zaktualizowanych produktów: %d' % (who, count)
    
    f = open(path.join(settings.WEBAPP_ROOT_DIR, 'log', 'sync.log'), 'a')
    f.write((u"%s - %s\n" % (dt.strftime('%Y-%m-%d %H:%M:%S'), msg)).encode('utf8'))
    f.close()
    
    log = m.LogEntry()
    log.category = what
    log.level = 'info'
    log.message = msg
    log.created = dt
    log.save()
    
    return HttpResponse("OK")
    

def resetPassword(request):
    pass


def view404(request):
    ctx = RequestContext(request)
    ctx['mainGroups'] = m.Category.objects.main_categories()
    t = loader.get_template('404.html')
    return HttpResponseNotFound(t.render(ctx))


def oldurl(request, url, ids='', slug=''):
    if url == 'cat':
        id = int(ids.split(',')[0])
        new_id = old_category_map.get(id, None)
        if new_id is None:
            raise Http404()
        slug = slug.replace('_','-')
        return HttpResponsePermanentRedirect(reverse('articles-group', args=[new_id, slug]))

    elif url == 'art':
        id = int(ids.split(',')[0])
        slug = slug.replace('_','-')
        return HttpResponsePermanentRedirect(reverse('article-slug', args=[id, slug]))

    elif url == 'plain':
        pid = request.GET.get('prod', 'n')
        gid = request.GET.get('gr', 'n')
        if pid != 'n':
            prod = get_object_or_404(m.Producer.publics, id=int(pid))
            return HttpResponsePermanentRedirect(reverse('articles-prod', args=[prod.id, prod.name]))
        if gid != 'n':
            cat = get_object_or_404(m.Category.objects, id=int(gid))
            return HttpResponsePermanentRedirect(reverse('articles-group', args=[cat.id, cat.name]))
        if not len(request.GET):
            return HttpResponsePermanentRedirect(reverse(mainpage))
        raise Http404()

def oldcat(request, group, slug='', page=''):
    new_id = old_category_map.get(int(group), None)
    if new_id is None:
        return HttpResponsePermanentRedirect(reverse('articles-group', args=[int(group), slug]))
    if page:
        return HttpResponsePermanentRedirect(reverse('articles-group-p', args=[new_id, slug, page]))
    else:
        return HttpResponsePermanentRedirect(reverse('articles-group', args=[new_id, slug]))

def redirect(request, src):
    rd = get_object_or_404(m.Redirect.objects, source='/'+src)
    return HttpResponseRedirect(rd.dest)
