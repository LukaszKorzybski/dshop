# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('dshop.main.remote',
    # Remote services
    (r'^rpc/$', 'rpcController'),
    (r'^rpc/(?P<method>.+)/$', 'rpcController')
)


urlpatterns += patterns('',
    (r'^payment-status/$', 'dshop.main.views.paymentStatusUpdate'),
    (r'^b2b_sync/(?P<what>(.*))/(?P<who>(.*))/(?P<dt>(.*))/', 'dshop.main.views.b2b_sync'),
    (r'^b2b_sync/(?P<what>(.*))/(?P<who>(.*))/', 'dshop.main.views.b2b_sync'),
    # POST to PayPal view
    (r'^payment-paypal-post/(?P<control>.+)/(?P<id>\d+)/$', 'dshop.paypal.post_to_paypal_view'),
)

urlpatterns += patterns('dshop.main.views',

    
    # various article lists
    (r'^kat/(?P<group>\d+),(?P<slug>(.*))/(?P<page>\d+)/$', 'articles', {'view':'group'}, 'articles-group-p'),
    (r'^kat/(?P<group>\d+),(?P<slug>(.*))/$', 'articles', {'view':'group'}, 'articles-group'),

    (r'^prod/(?P<producer>\d+),(?P<slug>(.*))/(?P<group>\d+),(?P<gslug>(.*))/(?P<page>\d+)/$', 'articles', {'view':'prod'}, 'articles-prod-gp'),
    (r'^prod/(?P<producer>\d+),(?P<slug>(.*))/(?P<group>\d+),(?P<gslug>(.*))/$', 'articles', {'view':'prod'}, 'articles-prod-g'),
    (r'^prod/(?P<producer>\d+),(?P<slug>(.*))/(?P<page>\d+)/$', 'articles', {'view':'prod'}, 'articles-prod-p'),
    (r'^prod/(?P<producer>\d+),(?P<slug>(.*))/$', 'articles', {'view':'prod'}, 'articles-prod'),

    (r'^nowosci/(?P<group>\d+),(?P<slug>(.*))/(?P<page>\d+)/$', 'articles', {'view':'new'}, 'articles-new-gp'),
    (r'^nowosci/(?P<group>\d+),(?P<slug>(.*))/$', 'articles', {'view':'new'}, 'articles-new-g'),
    (r'^nowosci/(?P<page>\d+)/$', 'articles', {'view':'new'}, 'articles-new-p'),
    (r'^nowosci/$', 'articles', {'view':'new'}, 'articles-new'),

    (r'^promocje/(?P<group>\d+),(?P<slug>(.*))/(?P<page>\d+)/$', 'articles', {'view':'promo'}, 'articles-promo-gp'),
    (r'^promocje/(?P<group>\d+),(?P<slug>(.*))/$', 'articles', {'view':'promo'}, 'articles-promo-g'),
    (r'^promocje/(?P<page>\d+)/$', 'articles', {'view':'promo'}, 'articles-promo-p'),
    (r'^promocje/$', 'articles', {'view':'promo'}, 'articles-promo'),

    (r'^mp/(?P<mprod>\d+),(?P<slug>(.*))/(?P<group>\d+),(?P<gslug>(.*))/(?P<page>\d+)/$', 'articles', {'view':'mprod'}, 'articles-mprod-gp'),
    (r'^mp/(?P<mprod>\d+),(?P<slug>(.*))/(?P<group>\d+),(?P<gslug>(.*))/$', 'articles', {'view':'mprod'}, 'articles-mprod-g'),
    (r'^mp/(?P<mprod>\d+),(?P<slug>(.*))/(?P<page>\d+)/$', 'articles', {'view':'mprod'}, 'articles-mprod-p'),
    (r'^mp/(?P<mprod>\d+),(?P<slug>(.*))/$', 'articles', {'view':'mprod'}, 'articles-mprod'),

    # search related views
    (r'^szukaj/$', 'search', {}, 'dshop-search'),
    (r'^szukaj/(?P<text>.*)/(?P<group>\d+),(?P<slug>(.*))/(?P<page>\d+)/$', 'search', {}, 'dshop-search-gp'),
    (r'^szukaj/(?P<text>.*)/(?P<group>\d+),(?P<slug>(.*))/$', 'search', {}, 'dshop-search-g'),
    (r'^szukaj/(?P<text>.*)/(?P<page>\d+)/$', 'search', {}, 'dshop-search-p'),
    (r'^szukaj/(?P<text>.*)/$', 'search', {}, 'dshop-searchtxt'),
    
    # Common and content related views
    (r'^$', 'mainpage', {}, 'mainpage'),
    (r'^art/(?P<id>\d+),(?P<slug>(.*))/(?P<page>\d+)/$', 'article', {}, 'article-slug-p'),
    (r'^art/(?P<id>\d+),(?P<slug>(.*))/$', 'article', {}, 'article-slug'),
    (r'^art/(?P<id>\d+),(.*)/$', 'article'),
    (r'^producenci/$', 'producers'),
    (r'^koszyk/$', 'cart'),
    #(r'^aktualnosci/$', 'news'),
    
    (r'^s,(?P<id>\d+)/(?P<key>.+)/$', 'static', {}, 'dshop-static'),
    (r'^preview/s,(?P<id>\d+)/(?P<key>.+)/$', 'static', { 'preview' : True }, 'dshop-prev-static'),
    
    
    # Cart and order placing related views
    (r'^koszyk/$', 'cart'),
    (r'^utworz-zamowienie/$', 'createOrder'),
    (r'^nowe-zamowienie/(?P<id>\d+)/$', 'newOrderEdit'),
    (r'^nowe-zamowienie/(?P<id>\d+)/platnosc/$', 'newOrderPayment'),
    (r'^nowe-zamowienie/(?P<id>\d+)/podsumowanie/$', 'newOrderSummary'),
    (r'^nowe-zamowienie/uzupelnij-profil/$', 'completeProfile', { 'ref' : 'neworder' }, 'dshop-cprofile-neworder'),
    
    
    # Client registration and login related views
    (r'^logowanie/$', 'login', {}, 'login'),
    (r'^autoryzacja/$', 'login', {'auth' : True}, 'auth'),
    (r'^wyloguj/$', 'logout'),
    (r'^juz-zalogowany/$', 'alreadyLoggedIn'),
    #(r'^nowehaslo/$', 'resetPassword'),
    (r'^rejestracja/$', 'register'),
    (r'^dziekujemy/(?P<email>.+)/$', 'thankYou'),
    (r'^aktywacja/(?P<login>.+)/(?P<key>.+)/$', 'activate'),
    (r'^aktywacja-pomyslna/$', 'activated'),
    (r'^odzyskaj-haslo/$', 'recoverPassword'),
    (r'^odbierz-email/$', 'passwordRecovered'),
    
    
    # Client account and profile related views
    (r'^uzupelnij-profil/$', 'completeProfile', {}, 'dshop-cprofile'),
    (r'^mojekonto/$', 'myAccount'),
    (r'^mojezamowienia/$', 'myOrders', {}, 'dshop-myorders'),
    (r'^mojezamowienia/(?P<year>\d+)/$', 'myOrders', {}, 'dshop-myorders-year'),
    (r'^mojezamowienia/(?P<year>\d+)/(?P<order>\d+)/$', 'myOrder', {}, 'dshop-myorder'),
    (r'^mojerabaty/$', 'myDiscounts'),
    (r'^aktywacja/$', 'activateCard'),
    (r'^karta-aktywna/$', 'cardActivated'),

    # redirects from old URLs
    (r'^towar/(?P<ids>.+)/(?P<slug>.+)\.html$', 'oldurl', { 'url' : 'art' }),
    (r'^index/(?P<ids>.+)/(?P<slug>.+)\.html$', 'oldurl', { 'url' : 'cat' }),
    (r'^index.html$', 'oldurl', { 'url' : 'plain' }),

    # old category ids
    (r'^kat,(?P<group>\d+)/(?P<slug>(.*))/(?P<page>\d+)/$', 'oldcat'),
    (r'^kat,(?P<group>\d+)/(?P<slug>(.*))/$', 'oldcat')
)
