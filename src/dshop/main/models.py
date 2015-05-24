# -*- coding: utf-8 -*-

from os import path
import datetime as dt
import hashlib
import copy
import decimal
import traceback
from decimal import Decimal
from xml.dom.minidom import getDOMImplementation

from django.db import models as m
from django.db import connection
from django.core.files.storage import default_storage
from django.core.urlresolvers import reverse
from django.db.models.signals import pre_delete, post_delete
from django.db.models.signals import post_save
from django.template import defaultfilters as filters
from django.core.mail import send_mail
from django.contrib.auth import models as auth_models

import mptt

from dshop import settings
from dshop import utils
from dshop.utils import money
from dshop.main import managers
from dshop.main.templatetags.utils import slugify_pl

from sorl.thumbnail import fields as sorl

def sort_by_list(qs, id_list):
    '''Sort given QS by list od ID's'''
    index = dict([(id, pos) for (pos, id) in enumerate(id_list)])
    result = [None] * len(id_list)
    for obj in qs:
        result[index[obj.id]] = obj
    return result

def round_if_need(price):
    if settings.ORDER_ROUND_PRICE_BEFORE_SUM:
        return money(price)
    else:
        return price

class PriceCalc:
    NET = 'N'
    GROSS = 'G'

PRICE_CALC_CHOICES = (
    (PriceCalc.NET, u'netto'),
    (PriceCalc.GROSS, u'brutto')
)

class UserProfile(m.Model):
    user = m.OneToOneField(auth_models.User)
    supplier = m.ForeignKey('Supplier', verbose_name=u'dostawca')
    
    @property
    def is_external(self):
        '''Return true if the user belongs to external supplier'''
        return not self.supplier.internal_supplier

class MetaInfo(m.Model):
    TYPE_CHOICES = (
        ('default', u'domyślny'),
        ('mpage', u'strona główna'),
        ('extra', u'dodatkowy')
    )

    name = m.CharField(u'nazwa', max_length=255)
    type = m.CharField(u'typ', max_length=255, choices=TYPE_CHOICES)
    content = m.TextField(u'wartość', blank=True)
    
    class Meta:
        verbose_name = u"meta informacja"
        verbose_name_plural = u"meta informacje"
        ordering = ["type"]

    def __unicode__(self):
        return self.name

    @property
    def default(self):
        return True if self.type == 'default' else False

    @property
    def mainpage(self):
        return True if self.type == 'mpage' else False

    @property
    def extra(self):
        return True if self.type == 'extra' else False


class StaticPage(m.Model):
    parent = m.ForeignKey('self', null=True, blank=True, related_name='children')
    title = m.CharField(u'tytuł', max_length=255)
    public = m.BooleanField(u'publiczna', default=True,
                            help_text=u"Odznacz jeśli nie chcesz jeszcze publikować tej strony.")
    display_index = m.BooleanField(u'spis treści', default=True,
                            help_text=u"Gdy włączone, na stronie zostanie wyświetlony spis treści.")
    backlink = m.BooleanField(u'link zwrotny', default=False,
                            help_text=u"Gdy włączone, wyświetlany jest link powrotny do strony poziom wyżej.")
    order = m.IntegerField(u'numer', help_text=u"Kolejność w indeksach i spisach.")

    objects = m.Manager()
    publics = managers.SPageManager()

    def __unicode__(self):
        return self.title

    @m.permalink
    def get_absolute_url(self):
        anc = [a for a in self.get_ancestors()] + [self]
        return ('dshop-static', (), { 'key' : '/'.join([slugify_pl(a.title) for a in anc]), 'id' : self.id })
    get_absolute_url.short_description = 'Adres URL'

    def preview_link(self):
        url = '/preview' + self.get_absolute_url()
        return '<a href="%s" target="_blank">%s</a>' % (url, u"podgląd")
    preview_link.short_description = 'Podgląd'
    preview_link.allow_tags = True

    class Meta:
        verbose_name = u"strona statyczna"
        verbose_name_plural = u"strony statyczne"
        ordering = ["order", "title"]

mptt.register(StaticPage, order_insertion_by=['order'])


class SPageContent(m.Model):
    owner = m.OneToOneField(StaticPage, verbose_name=u'właściciel')
    content = m.TextField(u'treść')

    class Meta:
        verbose_name = u'treść'
        verbose_name_plural = u'treść'


class SPageAttachment(m.Model):
    owner = m.ForeignKey(StaticPage, verbose_name=u'właściciel')
    name = m.CharField(u'nazwa', max_length=255)
    file = m.FileField(u'plik', upload_to='spages/%Y/%m')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u"Załącznik do stron statycznych"
        verbose_name_plural = u"Załączniki do stron statycznych"

    def save(self, force_insert=False, force_update=False):
        orig, need_remove = None, False
        if self.id:
            orig = SPageAttachment.objects.get(pk=self.id)
            if self.file.name != orig.file.name:
                need_remove = True

        super(SPageAttachment, self).save(force_insert, force_update)
        if orig and need_remove:
            try:
                default_storage.delete(orig.file.name)
            except OSError:
                # TODO log error/warning here (file is missing/wrong permissions)
                pass


class News(m.Model):
    title = m.CharField(u'tytuł', max_length=255)
    public = m.BooleanField(u'publiczny', default=True,
            help_text=u"Odznacz jeśli nie chcesz jeszcze publikować tego newsa.")
    created = m.DateField(u'data utworzenia',
            help_text=u"Data utworzenia. Newsy są wyświetlane w kolejności utworzenia.")
    sticky = m.BooleanField(u'przyklejony', default=False,
                                help_text=u"Widoczny zawsze na wierzchu (przyklejony), niezależnie od daty utworzenia.")
    more_link = m.CharField(u'więcej informacji pod', max_length=255, blank=True,
            help_text=u'Adres url do strony z obszerniejszą informacją.')
    summary = m.TextField(u'treść',
                                help_text=u"Skrót informacji, wyświetlany na głównej stronie.")
    
    objects = m.Manager()
    publics = managers.NewsManager()

    class Meta:
        verbose_name = u"aktualność"
        verbose_name_plural = u"aktualności"
        ordering = ['-sticky', '-created']

    def __unicode__(self):
        return self.title[:200]

    @m.permalink
    def get_absolute_url(self):
        return ('dshop.main.views.news',)


class HelpLink(m.Model):
    name = m.CharField(u'nazwa', max_length=255, unique=True)
    url = m.CharField(u'adres', max_length=255)

    class Meta:
        verbose_name = "link pomocy"
        verbose_name_plural = "linki pomocy"
        ordering = ['name']

    def __unicode__(self):
        return self.name


class AdditionalLink(m.Model):
    LOCATION_CHOICES = (
        ('header', u'nagłówek'),
        ('footer', u'stopka')
    )

    location = m.CharField(u'miejsce', max_length=255, choices=LOCATION_CHOICES,
            help_text=u'Linki dodatkowe mogą znajdować się w nagłówku oraz w stopce strony.')
    order = m.IntegerField(u'numer', default=1, help_text=u'Określa kolejność linków, mniejsze numery są pierwsze.')
    title = m.CharField(u'tytuł', max_length=255)
    url = m.CharField(u'adres', max_length=255)

    class Meta:
        verbose_name = u"link dodatkowy"
        verbose_name_plural = u"linki dodatkowe"
        ordering = ['location', 'order']


class SystemParam(m.Model):
    key = m.CharField(u'klucz', max_length=255, unique=True, db_index=True)
    value = m.CharField(u'wartość', max_length=255, blank=True)
    help_text = m.TextField(u'objaśnienie', blank=True)

    class Meta:
        verbose_name = u"parametr systemowy"
        verbose_name_plural = u"parametry systemowe"
        ordering = ['key']

    @staticmethod
    def get(key):
        return SystemParam.objects.get(key=key).value


class MainPageAd(m.Model):
    name = m.CharField(u'nazwa', max_length=255)
    order = m.IntegerField(u'numer')
    target = m.URLField(u'link docelowy', blank=True, help_text=u'Pełny adres \
            docelowy, np: http://sklep.optionall.pl/promocja/. Jest wczytywany po kliknięciu w baner.')
    file = m.FileField(u'plik', upload_to='ads', help_text=u'swf, jpg lub png.')

    class Meta:
        verbose_name = u"reklama na głównej stronie"
        verbose_name_plural = u"reklamy na głównej stronie"
        ordering = ['order']

    def save(self, force_insert=False, force_update=False):
        if self.id:
            orig = MainPageAd.objects.get(pk=self.id)
            if self.file.name != orig.file.name:
                default_storage.delete(orig.file.name)
        super(MainPageAd, self).save(force_insert, force_update)
        MainPageAd.dumpXML()

    @staticmethod
    def pre_delete(sender, instance, **kwargs):
        MainPageAd.dumpXML()

    @staticmethod
    def dumpXML():
        param_first = SystemParam.get('adslider_first')
        param_delay = SystemParam.get('adslider_delay')

        impl = getDOMImplementation()
        adsdoc = impl.createDocument(None, "data", None)
        
        root = adsdoc.documentElement
        root.setAttribute('first', param_first)
        root.setAttribute('delay', param_delay)

        ads = MainPageAd.objects.all()
        for ad in ads:
            el = adsdoc.createElement('ad')
            el.setAttribute('url', ad.file.url)
            el.setAttribute('target', ad.target)
            root.appendChild(el)
        
        f = open(path.join(settings.MEDIA_ROOT, 'slider/data.xml'), 'w')
        root.writexml(f, addindent='  ', newl='\n')
    
    def __unicode__(self):
        return self.name

pre_delete.connect(MainPageAd.pre_delete, sender=MainPageAd)


class Redirect(m.Model):
    source = m.CharField(u'adres źródłowy', max_length=255, unique=True,
                help_text=u'Ścieżka adresu źródłowego, np: /punkty-promocyjne/')
    dest = m.URLField(u'adres docelowy', max_length=255, verify_exists=False,
                help_text=u'Pełny adres docelowy, np: http://sklep.optionall.pl/aktywacja/')
    
    class Meta:
        verbose_name = u"przekierowanie adresu URL"
        verbose_name_plural = u"przekierowania adresów URL"
        ordering = ['source']

    def save(self, force_insert=False, force_update=False):
        if not self.source.startswith('/'):
            self.source = '/'+self.source
        super(Redirect, self).save(force_insert, force_update)


class MetaProducer(m.Model):
    name = m.CharField(u'nazwa', max_length=255)
    prod_ids = m.CharField(u'Id producentów', max_length=255,
                help_text=u'Podaj listę id producentów, oddziel id przecinkami.')
    
    class Meta:
        verbose_name = u"meta producent"
        verbose_name_plural = u"meta producenci"
        ordering = ['name']
    
    @m.permalink
    def get_absolute_url(self):
        return ('articles-mprod', [self.id, self.slug])

    @property
    def slug(self):
        return slugify_pl(self.name)[:55]

    @property
    def prod_ids_list(self):
        return [int(id) for id in self.prod_ids.split(',') if id]


# TODO Add ClientCartSet. Set will contain cards, Set can be created by looking for clients which have not cards yet
# or by entering number of unassigned (blank) cards. Such (blank - with numbers only) cards will be send/given
# to customers who don't have accounts yet. Such customer can enter card number when he is completing profile info?
# Card will have state: NEW, SENT_TO_PRINT, PRINTED, SENT, etc. State can be controlled from Set (for all cards) or per Card?
class ClientCard(m.Model):
    client = m.ForeignKey('Client', verbose_name=u'klient', blank=True, null=True)
    number = m.IntegerField(u'numer karty', unique=True)
    activated = m.DateTimeField(u'aktywowana', blank=True, null=True)
    activation_code = m.IntegerField(u'kod aktywacyjny')

    class Meta:
        verbose_name = u"karta klienta"
        verbose_name_plural = u"karty klienta"
        ordering = ['number']

    def is_active(self):
        return True if self.activated else False


class Producer(m.Model):
    name = m.CharField(u'nazwa', unique=True, max_length=255)
    toplist = m.BooleanField(u'na topliście', help_text=u'Producenci będący na topliście są \
            wyświetlani na głównej stronie.')
    public = m.BooleanField(u'publiczny', default=True,
            help_text=u'Odznacz jeśli chcesz ukryć producenta oraz wszystkie jego produkty.')
    exec_time = m.ForeignKey('ExecutionTime', blank=True, null=True, verbose_name=u'czas realizacji',
            help_text=u'Domyślny czas realizacji dla produktów producenta. Używany \
                    gdy produkt nie ma przypisanego własnego czasu realizacji.')

    objects = m.Manager()
    publics = managers.ProducerManager()

    class Meta:
        verbose_name = u"producent"
        verbose_name_plural = u"producenci"
        ordering = ['name']

    def __unicode__(self):
        return self.name

    @property
    def slug(self):
        return slugify_pl(self.name)[:55]

    def article_count(self):
        return self.article_set.count()
    article_count.short_description = u'ilość produktów'

    def first_letter(self):
        '''Upper cased first letter of producer's name.'''
        return self.name[0].upper() if self.name else u''

    def get_absolute_url(self):
        return reverse('articles-prod', args=[self.id, self.slug])

class ExecutionTime(m.Model):
    min = m.IntegerField(u'od (dni)')
    max = m.IntegerField(u'do (dni)', help_text=u'Czasy od, do mogą być równe.')

    class Meta:
        verbose_name = u"czas realizacji"
        verbose_name_plural = u"czasy realizacji"
        ordering = ['min']
        unique_together = (("min", "max"),)

    def isNone(self):
        return False

    def compare_to(self, et):
        '''Return -1, 0, 1. 1 - if is better than given exec time. 0 - equal, -1 - worse.'''
        if et is None or et.isNone():
            return 1
        if et.max > self.max:
            return 1
        if et.max == self.max:
            if et.min > self.min:
                return 1
            elif et.min == et.min:
                return 0
            else:
                return -1
        return -1
    
    @staticmethod
    def worse(e1, e2):
        '''Return worse execution time from given two. Return NoneExecutionTime if
           at least one of them is None.
        '''
        if e1 is None or e2 is None:
            return NoneExecutionTime()
        return e1 if e1.compare_to(e2) == -1 else e2


    def __unicode__(self):
        if self.min == self.max:
            if self.min == 1:
                return u'%d dzień' % self.min
            else:
                return u'%d dni' % self.min
        else:
            return u'%d-%d dni'% (self.min, self.max)

class NoneExecutionTime(ExecutionTime):
    class Meta:
        abstract = True
    
    def isNone(self):
        return True
    def save(self, force_insert=False, force_update=False):
        pass
    def delete(self):
        pass
    def __unicode__(self):
        return u'zapytaj'


class Category(m.Model):
    level_multiplier = 1000000

    name = m.CharField(u'nazwa', max_length=255, db_index=True)
    parent = m.ForeignKey('self', verbose_name=u'kategoria nadrzędna', null=True, blank=True, related_name='children')
    parent.main_category_filter = True

    # Leveled ids from root category down to self, separated by space. Leveling
    # is needed for sphinx search since MVA attributes are not ordered.
    r_lid_path = m.CharField(editable=False, blank=True, max_length=500)

    objects = managers.CategoryManager()

    class Meta:
        verbose_name = u'kategoria produktów'
        verbose_name_plural = u'kategorie produktów'
        ordering = ['name']

    def __unicode__(self):
        return self.name

    @classmethod
    def id_from_leveled_id(cls, lid, level):
        '''Retrieve category id from given leveled id and level.'''
        return lid % cls.level_multiplier

    @classmethod
    def leveled_to_ids(cls, lids):
        '''Convert list of leveled category ids to a list of plain ids.'''
        if isinstance(lids, basestring):
            lids = [int(l) for l in lids.split()]
        return [l % cls.level_multiplier for l in lids]

    def leveled_id(self):
        '''Return leveled id. Leveled id of a category that is lower in the tree is greater than
           Leveled id of a category that is higher in the tree hierarchy.

           It is used by full text search to generate articles view categories subtrees.
        '''
        return (self.level * self.level_multiplier) + self.id
    
    @property
    def slug(self):
        return slugify_pl(self.name)[:55]

    def save(self, force_insert=False, force_update=False):
        super(Category, self).save(force_insert, force_update)

        #update redundant field
        self.r_lid_path = ' '.join([unicode(c.leveled_id()) for c in self.get_ancestors()])
        if self.r_lid_path:
            self.r_lid_path += ' %d ' % self.leveled_id()
        else:
            self.r_lid_path += '%d ' % self.leveled_id()
        super(Category, self).save(force_insert, force_update)

    def get_absolute_url(self):
        return reverse('articles-group', args=[self.id, self.slug])

mptt.register(Category)


class BaseAddress(m.Model):
    class Type:
        PERSON = 'P'
        COMPANY = 'C'

    TYPE_CHOICES = (
        (Type.PERSON, u'osoba prywatna'),
        (Type.COMPANY, u'firma')
    )

    type = m.CharField(u'typ', max_length=1, blank=True, choices=TYPE_CHOICES)
    first_name = m.CharField(u'imię', max_length=80, db_index=True)
    last_name = m.CharField(u'nazwisko', max_length=80, db_index=True)
    company_name = m.CharField(u'nazwa firmy', blank=True, max_length=80, db_index=True)
    nip = m.CharField(u'NIP', blank=True, max_length=255)
    town = m.CharField(u'miasto', max_length=255)
    street = m.CharField(u'ulica', max_length=255)
    number = m.CharField(u'nr lokalu', max_length=255)
    code = m.CharField(u'kod pocztowy', max_length=255)
    phone = m.CharField(u'telefon', max_length=255)
    second_phone = m.CharField(u'drugi telefon', blank=True, max_length=255)

    class Meta:
        abstract = True

    def __unicode__(self):
        if self.type == BaseAddress.Type.PERSON:
            return u'%s %s' % (self.first_name, self.last_name)
        else:
            return self.company_name

    @property
    def name(self):
        if self.type == self.Type.COMPANY:
            return self.company_name
        else:
            return self.first_name + ' ' + self.last_name

    def inverse_name(self):
        if self.type == self.Type.COMPANY:
            return self.company_name
        else:
            return self.last_name + ' ' + self.first_name

    def is_company(self):
        return True if self.type == BaseAddress.Type.COMPANY else False

    def copy_from(self, address):
        '''Copy all (except id) BaseAddress fields from given address.'''
        fields = BaseAddress._meta.get_all_field_names()
        for f in fields:
            if f != 'id':
                setattr(self, f, getattr(address, f))


class Address(BaseAddress):
    client = m.ForeignKey('Client', verbose_name=u'klient')
    base = m.BooleanField(editable=False, default=False)

    class Meta:
        verbose_name = u'adres'
        verbose_name_plural = u'adresy'


class ClientNumber(m.Model):
    num = m.IntegerField(u'numer', primary_key=True)
    available = m.BooleanField(u'dostępny', db_index=True)
    date_taken = m.DateTimeField(u'data zajęcia', blank=True, null=True)

    objects = managers.ClientNumberManager()

    class Meta:
        verbose_name = u'numer klienta'
        verbose_name_plural = u'numery klienta'

    def __unicode__(self):
        return unicode(self.num)

    def take_by(self, client):
        '''Updates client with the number. Call save on client also after this method.'''
        client.client_num = self.num
        self.available = False
        self.date_taken = dt.datetime.now()


class Client(BaseAddress):
    profile_complete_label = u'Profil kompletny'
    acceptance_label = u'Zgoda na przetwarzanie danych'
    promo_multiplier_label = u'Przelicznik przyznawania punktów'

    profile_complete_help = u'Zaznacz jeśli profil klienta jest uzupełniony o dane adresowe, dopiero wtedy klient może składać zamówienia.'
    promo_multiplier_help = u'Np. 1 - jeden punkt za jedną wydaną złotówkę, 2 - dwa punkty za złotówkę. 0,5 - pół punkta za złotówkę.'

    client_num = m.IntegerField(u'numer klienta', unique=True)
    stock_id = m.IntegerField(editable=False, unique=True, blank=True, null=True)
    login = m.CharField(u'login', max_length=255, unique=True, db_index=True)
    password = m.CharField(u'hasło', max_length=255, blank=True)
    legacy_passwd_format = m.BooleanField(default=False)
    created = m.DateTimeField(u'data utworzenia', default=dt.datetime.now)
    last_login = m.DateTimeField(u'ostatnie logowanie', blank=True, null=True)
    active = m.BooleanField(u'aktywny', help_text=u'Jeśli ręcznie zakładasz konto klienta, wyślij mu link aktywacyjny'
            +u' lub zaznacz jego konto jako aktywne. Tylko aktywni klienci mają możliwość logowania się do sklepu.')
    activation_code = m.CharField(u'klucz aktywacyjny', max_length=255)
    profile_complete = m.BooleanField(profile_complete_label, help_text=profile_complete_help)
    newsletter = m.BooleanField(u'newsletter',
            help_text=u'Zaznacz jeśli klient zgadza się na otrzymywanie informacji handlowych drogą elektroniczną.')
    acceptance = m.BooleanField(acceptance_label)
    promo_card_active = m.BooleanField(u'Karta promocyjna aktywna', default=False)
    promo_points = m.IntegerField(u'punkty promocyjne', default=0,
            help_text=u'Ilość punktów promocyjnych na koncie klienta.')
    promo_multiplier = m.DecimalField(promo_multiplier_label, default=Decimal(1), max_digits=6, decimal_places=2,
            help_text=promo_multiplier_help)
    payment_deadline = m.IntegerField(u'termin płatności', default=0,
            help_text=u'X dni terminu płatności, 0 oznacza brak opcji terminu płatności.')
    req_for_opinion_sent = m.DateField(u'ostatnia prośba o opinie wysłana w dniu', blank=True, null=True, editable=False)
    client_hash = m.CharField(u'Unikalny hash', max_length=32, editable=False)

    r_client_num = m.CharField(u'numer klienta', max_length=20, unique=True, db_index=True, editable=False)

    class Meta:
        verbose_name = u'klient'
        verbose_name_plural = u'klienci'

    def __unicode__(self):
        return u'%s (%s)' % (super(Client, self).__unicode__(), self.client_num)

    def set_password(self, pwd):
        self.password = self._encode_passwd(pwd, legacy=False)
        self.legacy_passwd_format = False

    def check_password(self, pwd):
        if self.password == self._encode_passwd(pwd, self.legacy_passwd_format):
            return True
        else:
            return False

    @property
    def carts(self):
        '''Carts which are not Orders. Use this if you want to manipulate on
           carts only, instead of cart_set which also includes client's orders!!
        '''
        return self.cart_set.exclude(is_order=True)

    def has_payment_deadline(self):
        return True if self.payment_deadline > 0 else False

    def discount(self, sarticle):
        '''Return client discount for given AbstractShopArticle object, otherwise NoneDiscount.'''
        try:
            return self.discount_set.get(article=sarticle.article)
        except ClientDiscount.DoesNotExist:
            return NoneDiscount(sarticle.article)

    @property
    def email(self):
        return self.login
    
    def replace_cart(self, cart):
        '''Replace client's old cart with given cart.'''
        # we exclude given cart for a case if it would be already assigned to this client
        for c in self.carts.exclude(id=cart.id):
            c.delete()
        cart.set_client(self)
        cart.save()
    
    @property
    def base_address(self):
        return self.address_set.get(base=True)

    def get_cart(self):
        '''Return current cart or, if client doesn't have cart yet, create new cart and return it.'''
        try:
            cart = self.cart_set.all()[0]
        except IndexError:
            cart = Cart()
            cart.set_client(self)
            cart.save()
        return cart

    @property
    def card(self):
        '''Return client card or None if client doesn't have card yet.'''
        try:
            return self.clientcard_set.all()[0]
        except IndexError:
            return None

    def orders_year_list(self):
        '''Return list of tuples (year, order_count).'''
        cursor = connection.cursor()
        cursor.execute("SELECT cast(extract(year from o.created) as integer) as year, count(*) FROM "
                       "main_order o INNER JOIN main_cart c ON (o.cart_ptr_id = c.id) "
                       "WHERE c.client_id = %s GROUP BY year ORDER BY year DESC", [self.id])
        years = cursor.fetchall()
        return years

    def can_send_req_for_opinion(self):
        if self.req_for_opinion_sent is None or \
           dt.date.today() - self.req_for_opinion_sent > dt.timedelta(days=30):
            return True
        else:
            return False

    def save(self, force_insert=False, force_update=False):
        msec = dt.datetime.now().microsecond

        # reserve and set number for new client if not already set
        if self.client_num == None:
            cnum = ClientNumber.objects.get_next()
            cnum.take_by(self)
            cnum.save()

        # lowercase login
        self.login = self.login.lower()

        # generate activation code
        if not self.activation_code:
            self.activation_code = hashlib.sha1('&#(Sl_%d_$^,F~s_%s' % (msec,self.login)).hexdigest()

        # generate unique hash id
        if not self.client_hash:
            self.client_hash = hashlib.md5('%d,%s' % (msec,self.login)).hexdigest()

        # update redundant fields
        self.r_client_num = str(self.client_num)

        # save Client
        super(Client, self).save(force_insert, force_update)

        # create or update base shipping/invoice address
        if self.profile_complete:
            try:
                base_addr = self.address_set.get(base=True)
            except Address.DoesNotExist:
                base_addr = Address(client=self, base=True)
            base_addr.copy_from(self)
            base_addr.save()

    def _encode_passwd(self, pwd, legacy=False):
        if legacy:
            return hashlib.md5(pwd).hexdigest()
        else:
            return hashlib.sha1('_#(^%s&KlZt_' % pwd).hexdigest()

class File(m.Model):
    TYPE_CHOICES = (
        ('video', u'film'),
        ('photo', u'obraz'),
        ('sound', u'dźwięk'),
        ('doc', u'dokument'),
        ('archive', u'archiwum'),
        ('other', u'inne')
    )
    
    
    name = m.CharField(u'nazwa', unique=True, max_length=255)
    type = m.CharField(u'rodzaj', choices=TYPE_CHOICES, max_length=255,
            help_text=u'Ma jedynie wartość informacyjną, pomaga w katalogowaniu plików.')
    file = m.FileField(u'plik', upload_to='file/%Y/%m')

    class Meta:
        verbose_name = u'plik'
        verbose_name_plural = u'pliki'

    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.file.name)

    @property
    def url(self):
        return self.file.url

    def save(self, force_insert=False, force_update=False):
        orig, need_remove = None, False
        if self.id:
            orig = File.objects.get(pk=self.id)
            if self.file.name != orig.file.name:
                need_remove = True

        super(File, self).save(force_insert, force_update)
        if orig and need_remove:
            try:
                default_storage.delete(orig.file.name)
            except OSError:
                # TODO log error/warning here (file is missing/wrong permissions)
                pass


class Unit(m.Model):
    precision_help = u'Precyzja określa z jaką dokładnością dotyczącą ilości klient może zamawiać produkt. \
            przykładowe wartości: 1  0,1  0,5  0,01.'

    stock_id = m.IntegerField(editable=False, blank=True, null=True)
    name = m.CharField(u'nazwa', unique=True, max_length=255)
    name_accusative = m.CharField(u'nazwa w bierniku', max_length=255, blank=True,
            help_text=u'Nazwa jednostki w formie biernika (kogo?, co?). Np. sztukę, litr, kilogram.')
    short = m.CharField(u'skrót', unique=True, max_length=255)
    precision = m.DecimalField(u'precyzja', max_digits=8, decimal_places=4,
            help_text=precision_help)

    class Meta:
        verbose_name = u'jednostka'
        verbose_name_plural = u'jednostki'

    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.short)


class Property(m.Model):
    name = m.CharField(u'nazwa', unique=True, max_length=255)
    desc = m.TextField(u'opis', blank=True,
            help_text=u'Podaj jeśli cecha wymaga wyjaśnienia (dla pracowników).')

    class Meta:
        verbose_name = u'cecha'
        verbose_name_plural = u'cechy'
        ordering = ['name']

    def __unicode__(self):
        return self.name

    def spec_count(self):
        return self.specification_set.count()
    spec_count.short_description = u'w specyfikacjach'


class Specification(m.Model):
    properties = m.ManyToManyField('Property', through='PropertyMembership')
    name = m.CharField(u'nazwa', unique=True, max_length=255)

    class Meta:
        verbose_name = u'specyfikacja'
        verbose_name_plural = u'specyfikacje'
        ordering = ['name']

    def __unicode__(self):
        return self.name

    def properties_count(self):
        return self.properties.count()
    properties_count.short_description = u'ilość cech'

    def article_count(self):
        return self.article_set.count()
    article_count.short_description = u'w produktach'


class PropertyMembership(m.Model):
    prop = m.ForeignKey('Property', verbose_name=u'cecha')
    spec = m.ForeignKey('Specification', verbose_name=u'specyfikacja')
    order = m.IntegerField(u'pozycja', blank=True)

    class Meta:
        verbose_name = u'przypisanie cechy'
        verbose_name_plural = u'przypisania cech'
        ordering = ['order']

    def __unicode__(self):
        return u'%s (%s)' % (self.prop.name, self.spec.name)


class ArticleProperty(m.Model):
    order_label = u'kolejność'
    property_label = u'cecha'
    
    article = m.ForeignKey('ShopArticle', verbose_name=u'produkt', related_name='property_set')
    property = m.ForeignKey('PropertyMembership', verbose_name=property_label)
    value = m.CharField(u'wartość', blank=True, max_length=1000)

    class Meta:
        verbose_name = u'cecha produktu'
        verbose_name_plural = u'cechy produktów'
    
    def name(self):
        return self.property.prop.name

    def __unicode__(self):
        return self.property.prop.name


class Supplier(m.Model):
    name = m.CharField(u'nazwa', max_length=255, unique=True)
    phone = m.CharField(u'telefon', max_length=255, blank=True)
    fax = m.CharField(u'faks', max_length=255, blank=True)
    email = m.CharField(u'email', max_length=255, blank=True)
    internal_supplier = m.BooleanField(u'dostawca wewnętrzny', blank=True,
        help_text=u'Ustaw jeśli ten dostawca to twoja firma.')
    exec_time = m.ForeignKey('ExecutionTime', verbose_name=u'Czas realizacji', null=True, blank=True,
        help_text=u'Czas realizacji w przypadku gdy produktu nie ma w magazynie wewnętrznym \
                    ale jest w magazynie dostawcy.')

    # optimization fields
    has_stock_integration = m.BooleanField(u'integracja', editable=False)

    @property
    def stock_integration(self):
        try:
            return self.stockintegration_set.all()[0]
        except:
            return None

    class Meta:
        verbose_name = u'dostawca'
        verbose_name_plural = u'dostawcy'

    def __unicode__(self):
        return self.name[:200]

class Article(m.Model):
    name = m.CharField(u'nazwa', max_length=255)
    cat_index = m.CharField(u'numer katalogowy', max_length=255, unique=True)

    unit = m.ForeignKey('Unit', verbose_name=u'jednostka')
    supplier = m.ForeignKey(u'Supplier', verbose_name=u'dostawca', blank=True, null=True)

    stock_id = m.IntegerField(u'ID magazynowe', unique=True, blank=True, null=True, editable=False)
    vat = m.DecimalField(u'VAT (%)', max_digits=6, decimal_places=2)
    purchase_net = m.DecimalField(u'cena zakupu netto', max_digits=18, decimal_places=6, blank=True, null=True)
    purchase_gross = m.DecimalField(u'cena zakupu brutto', max_digits=18, decimal_places=6, blank=True, null=True)
    net = m.DecimalField(u'cena netto', max_digits=18, decimal_places=6)
    gross = m.DecimalField(u'cena brutto', max_digits=18, decimal_places=6)
    price_calc = m.CharField(u'obliczaj na podst. ceny', max_length=2, choices=PRICE_CALC_CHOICES, default=PriceCalc.NET)
    stock_lvl = m.DecimalField(u'stan na magazynie', max_digits=14, decimal_places=4, default=Decimal(0))
    supplier_stock_lvl = m.DecimalField(u'stan na magazynie u dostawcy', max_digits=14, decimal_places=4, default=Decimal(0))
    weight = m.DecimalField(u'waga (kg)', max_digits=14, decimal_places=4)
    
    stock_synced = m.BooleanField(u'w programie M-K', default=False, editable=False)
    stock_last_sync = m.DateTimeField(u'ostatni sync z programem M-K', blank=True, null=True, editable=False)
    supplier_synced = m.BooleanField(u'w programie M-K dostawcy', default=False, editable=False)
    supplier_last_sync = m.DateTimeField(u'ostatni sync z programem M-K dostawcy', blank=True, null=True, editable=False)
    
    # r_used fields are not so important now, since Article lifetime has been strictly connected
    # to ShopArticle/ArticleVariant lifetime.
    r_used = m.BooleanField(u'na sklepie', default=False, editable=False)
    
    # Can be used by shoparticle, variant, or by both (in case of shoparticle's main variant)
    r_used_shoparticle = m.BooleanField(u'użyty przez produkt', editable=False)
    r_used_variant = m.BooleanField(u'użyty przez wariant', editable=False)

    class Meta:
        verbose_name = u'produkt magazynowy'
        verbose_name_plural = u'produkty magazynowe'

    def __init__(self, *args, **kwargs):
        super(Article, self).__init__(*args, **kwargs)

    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.cat_index)    
    
    @property
    def promo(self):
        '''Return promotion or NonePromotion if no promotion is available.
           Return NonePromotion if promotion is available but is equal or more expensive than regular price (inactive).
        '''
        npromo = NonePromotion(self)
        try:
            return Discount.better(npromo, self.promotion)
        except Promotion.DoesNotExist:
            return npromo

    @property
    def has_promotion(self):
        '''Return True if promotion is set on this article, no matter if it is active or not.'''
        try:
            self.promotion
            return True
        except Promotion.DoesNotExist:
            return False

    def used(self):
        '''Return True if article is used.'''
        return self.r_used
    used.short_description = u'na sklepie'
    used.boolean = True

    def get_shoparticle(self):
        '''Return shoparticle, no matter if article is used by variant or shoparticle.
           If article is used by variant then return the variant's owner.
        '''
        if self.r_used_shoparticle:
            return self.shoparticle
        elif self.r_used_variant:
            return self.articlevariant.owner
        else:
            return None

    def get_variant(self):
        '''Return variant or None if not related to variant.'''
        if self.r_used_variant:
            return self.articlevariant
        else:
            return None

    def get_abstr_article(self):
        '''Return ArticleVariant in case of being used by variant or ShopArticle if not used by variant.'''
        if self.used_by_variant():
            return self.articlevariant
        elif self.used_by_shoparticle():
            return self.shoparticle
        else:
            return None

    def used_by_variant(self, variant=None):
        '''Return True if article is used by any or specific (if given) ArticleVariant.'''
        if variant:
            if variant.id and self.r_used_variant and self.id == variant.article.id:
                return True
            else:
                return False
        else:
            return self.r_used_variant
    used_by_variant.short_description = u'jako wariant'
    used_by_variant.boolean = True
    
    def used_by_shoparticle(self, sarticle=None):
        '''Return True if article is used by any or specific (if given) ShopArticle.'''
        if sarticle:
            if sarticle.id and self.r_used_shoparticle and self.id == sarticle.article.id:
                return True
            else:
                return False
        else:
            return self.r_used_shoparticle
    used_by_shoparticle.short_description = u'jako produkt'
    used_by_shoparticle.boolean = True
    
    def save(self, force_insert=False, force_update=False):
        # calculate prices
        if self.price_calc == PriceCalc.NET:
            if self.purchase_net:
                self.purchase_gross = self.purchase_net * (1 + self.vat/100)
            else:
                self.purchase_gross = None
            self.gross = self.net * (1 + self.vat/100)
        else:
            if self.purchase_gross:
                self.purchase_net = self.purchase_gross / (1 + self.vat/100)
            else:
                self.purchase_net = None
            self.net = self.gross / (1 + self.vat/100)
        super(Article, self).save(force_insert, force_update)


class AbstractShopArticle(m.Model):
    article = m.OneToOneField('Article', verbose_name=u'produkt', unique=True)
    exec_time = m.ForeignKey('ExecutionTime', verbose_name=u'czas realizacji', blank=True, null=True,
            help_text=u'Gdy niepodany użyty zostanie domyślny czas realizacji producenta.')
    
    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        self._client = None
        super(AbstractShopArticle, self).__init__(*args, **kwargs)

    @property
    def unit(self):
        return self.article.unit if self.article else None

    @property
    def stock_id(self):
        return self.article.stock_id if self.article else None
    
    @property
    def cat_index(self):
        return self.article.cat_index if self.article else ''

    @property
    def vat(self):
        return self.article.vat if self.article else None

    @property
    def purchase_net(self):
        return self.article.purchase_net if self.article else None

    @property
    def purchase_gross(self):
        return self.article.purchase_gross if self.article else None

    @property
    def net(self):
        return self.article.net if self.article else None

    @property
    def gross(self):
        return self.article.gross if self.article else None

    @property
    def stock_lvl(self):
        return self.article.stock_lvl if self.article else None

    @property
    def weight(self):
        return self.article.weight if self.article else None

    @property
    def promotion(self):
        '''Return article's promotion.'''
        return self.article.promo if self.article else None

    @property
    def supplier(self):
        return self.article.supplier if self.article else None

    @property
    def is_variant(self):
        return False

    @property
    def shoparticle(self):
        return self

    def same_price(self, art, incl_discounts=True):
        '''Return True net and gross prices are equal. By default takes discounts into account.'''
        if incl_discounts:
            return self.best_discount.same_price(art.best_discount)
        else:
            if self.net == art.net and self.gross == art.gross:
                return True
            else:
                return False
    
    @property
    def best_discount(self):
        '''Return best discount, uses also client discounts if client field is set.
           Return NoneDiscount if no discount is available for this article.
           Return NoneDiscount if best discount is equal or more expensive than regular price (inactive).
        '''
        ndiscount = NoneDiscount(self.article)
        if self._client:
            return Discount.better(ndiscount, Discount.better(self._client.discount(self), self.promotion))
        else:
            return Discount.better(ndiscount, self.promotion)

    def inject_client(self, client):
        self._client = client
        return self

    def real_exec_time(self):
        '''Compute actual execution time for article.'''
        in_stock = ExecutionTime(min=1, max=1)
        if self.article.stock_lvl > 0:
            return in_stock
        else:
            if self.article.supplier and self.article.supplier_stock_lvl > 0:
                supplier_exec_time = self.article.supplier.exec_time
                if supplier_exec_time:
                    return supplier_exec_time
            etime = self.exec_time if self.exec_time else self._inherited_exec_time()
            return etime if etime else NoneExecutionTime()
    
    def release_article(self):
        '''Release related Article object, it will be available to use by other ShopArticle/ArticleVariant.'''
        self.article.r_used = False

    def take_article(self):
        '''Take related Article object, it will be now considered as used by this ShopArticle/ArticleVariant.'''
        self.article.r_used = True

    def save(self, force_insert=False, force_update=False, forced_id_insert=False):
        # mark Article object as used (r_used is redundant field)
        self.take_article()
        self.article.save()

        return super(AbstractShopArticle, self).save(force_insert, force_update)

    @staticmethod
    def post_delete(sender, instance, **kwargs):
        # Remove related Article object
        instance.article.delete()

    def _inherited_exec_time(self):
        return self.producer.exec_time


class ArticleParam(m.Model):
    name = m.CharField(u'nazwa', max_length=255, unique=True)
    name_plural = m.CharField(u'nazwa w l. mnogiej', max_length=255, unique=True)
    explanation = m.TextField(u'wyjaśnienie', blank=True,
            help_text=u'Pojawia się w okienku umożliwiającym podanie wartości parametru dla pozycji w koszyku/zamówieniu.')

    class Meta:
        verbose_name = u'parametr produktu'
        verbose_name_plural = u'parametry produktów'
        ordering = ['name']

    def __unicode__(self):
        return self.name


class ShopArticle(AbstractShopArticle):
    main_variant_qty_label = u'ilość dla wariantu głównego'

    class VariantsType:
        QUANTITY = 'Q'
        KIND = 'K'

    VARIANTS_TYPE_CHOICES = (
        (VariantsType.KIND, u'rodzajowe'),
        (VariantsType.QUANTITY, u'ilościowe')
    )
    
    producer = m.ForeignKey('Producer', verbose_name=u'producent', related_name='article_set')
    category = m.ForeignKey('Category', verbose_name=u'kategoria', related_name='article_set')
    category.main_category_filter = True

    specification = m.ForeignKey('Specification', verbose_name=u'specyfikacja', related_name='article_set', blank=True, null=True)
    param = m.ForeignKey('ArticleParam', verbose_name=u'parametr', related_name='article_set', blank=True, null=True,
            help_text=u'Gdy wybrany klient będzie mógł podać parametr zamawianego produktu.')
    recc_articles = m.ManyToManyField('self', verbose_name=u'polecane', blank=True, symmetrical=False)

    name = m.CharField(u'nazwa', max_length=255)
    public = m.BooleanField(u'publiczny', default=True)
    new = m.BooleanField(u'nowy', db_index=True)
    recommended = m.BooleanField(u'polecany', db_index=True)
    frontpage = m.BooleanField(u'strona główna', db_index=True)
    created = m.DateTimeField(u'data utworzenia', default=dt.datetime.now)

    short_desc = m.TextField(u'opis na liście', blank=True)
    desc = m.TextField(u'opis', blank=True)

    variants = m.BooleanField(u'produkt z wariantami')
    variants_type = m.CharField(u'rodzaj wariantów', blank=True, max_length=1, choices=VARIANTS_TYPE_CHOICES, default=VariantsType.KIND)
    variants_name = m.CharField(u'nazwa wariantów', max_length=255, blank=True)
    main_variant_name = m.CharField(u'nazwa wariantu głównego', max_length=255, blank=True)
    variants_unit = m.ForeignKey('Unit', blank=True, null=True, verbose_name=u'jednostka',
            help_text=u'Nazwa jednostki jest używana przy wyświetlaniu ceny jednostkowej produktu przy wariantach ilościowych.')
    main_variant_qty = m.DecimalField(main_variant_qty_label, blank=True, null=True, max_digits=14, decimal_places=4)

    # redundant fields for more performance
    r_opinion_count = m.IntegerField(u'ilość opinii', editable=False, default=0)
    r_avg_rating = m.DecimalField(u'średnia ocena', editable=False, max_digits=3, decimal_places=1, default=0)
    r_category_path = m.CharField(max_length=500, editable=False, db_index=True)
    r_main_photo = m.ForeignKey('ArticlePhoto', editable=False, blank=True, null=True)

    objects = m.Manager()
    publics = managers.ShopArticleManager()

    class Meta:
        verbose_name = u'produkt'
        verbose_name_plural = u'produkty'

    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.cat_index)

    @property
    def quantity_variants(self):
        '''Return True if article have quantity variants, False otherwise.'''
        if self.variants and self.variants_type == self.VariantsType.QUANTITY:
            return True
        else:
            return False
    
    @property
    def diff_price_variants(self):
        '''Return True if variants have different prices, False otherwise or when no variants at all.
           Includes discounts (client, promos) in comparison.
        '''
        if self.variants:
            variants = list(self.variant_set.all().select_related('article__promotion'))
            if self._client:
                variants = [v.inject_client(self._client) for v in variants]

            for v in variants:
                if not variants[0].same_price(v):
                    return True
            return False
        else:
            return False

    @property
    def slug(self):
        return slugify_pl(self.name)[:55]
    
    def cheapest_variant(self):
        # TODO this should include promotions, so it's not so straightforward
        if not self.variants:
            raise Exception("%s doesn't have variants" % self)
        variant = self.variant_set.select_related('article').order_by('article__gross')[0]
        return variant.inject_client(self._client)

    def main_variant(self):
        '''Main variant with client object injected.'''
        if not self.variants:
            raise Exception("%s doesn't have variants." % self)
        variant = self.variant_set.get(main=True)
        return variant.inject_client(self._client)

    def sorted_variant_set(self):
        '''Return appropriately sorted list of variants with client object injected.'''
        if self.variants_type == self.VariantsType.KIND:
            variants = self.variant_set.order_by('variant').select_related('owner__exec_time', 'exec_time', 'article__promotion')
        else:
            variants = self.variant_set.order_by('qty').select_related('owner__exec_time', 'exec_time','article__promotion')
        
        if self._client:
            variants = [v.inject_client(self._client) for v in variants]
        return variants

    def neverempty_photo_set(self):
        '''Return photo list which always have at least one photo. Main photo is always first.
           Adds default photo to the list if no photos are available.
        '''
        photos = self.photo_set.order_by('-main')
        if photos:
            return photos
        else:
            return [ArticlePhoto.Default]
    
    def main_photo(self):
        if self.r_main_photo:
            return self.r_main_photo
        else:
            return ArticlePhoto.Default

    def get_absolute_url(self):
        return reverse('article-slug', args=[self.id, self.slug])

    def category_path(self):
        '''Return list of categories. Beginning with root up to and including containing category.'''
        return list(self.category.get_ancestors()) + [self.category]

    def listed_attachments(self):
        '''Return attachments that should be displayed on attachment list.'''
        return self.attachment_set.filter(listed=True).select_related('type')

    def filled_properties(self):
        '''Return queryset of properties which have their values set.'''
        return self.property_set.exclude(value='').order_by('property__order').select_related('property__prop')

    def active_opinions(self):
        '''Return set of non-blocked article opinions.'''
        return self.opinion_set.filter(blocked=False)

    def recalc_opinion_stats(self):
        '''Recalculate and update redundant fields holding opinion stats. Called by Opinion.save and delete.'''
        opinions = self.active_opinions()
        if opinions:
            avg = (sum([o.rating for o in opinions]) /
                Decimal(len(opinions))).quantize(Decimal('0.1'), rounding=decimal.ROUND_HALF_UP)
            self.r_opinion_count = len(opinions)
            self.r_avg_rating = avg
        else:
            self.r_opinion_count = 0
            self.r_avg_rating = 0

    @property
    def avg_rating(self):
        return self.r_avg_rating

    @property
    def opinion_count(self):
        return self.r_opinion_count or 0

    @property
    def avg_rating_tuple(self):
        '''Average rating as a tuple of number and fraction.'''
        return (int(self.r_avg_rating), int((self.r_avg_rating - int(self.r_avg_rating))*10))

    def release_article(self):
        self.article.r_used_shoparticle = False
        super(ShopArticle, self).release_article()

    def take_article(self):
        self.article.r_used_shoparticle = True
        super(ShopArticle, self).take_article()

    def _update_main_variant(self):
        '''Create/update main variant. Doesn't save. Return the new/updated variant.'''
        if not self.variants:
            raise Exception(u'%s: cannot update main variant for article with variants turned off.' % self)
        
        try:
            variant = self.main_variant()
        except ArticleVariant.DoesNotExist:
            variant = ArticleVariant()

        variant.main = True
        variant.owner = self
        variant.article = self.article
        variant.variant = self.main_variant_name
        variant.qty = self.main_variant_qty
        return variant

    def save(self, force_insert=False, force_update=False, forced_id_insert=False):
        if not self.name:
            self.name = self.article.name
        self.r_category_path = self.category.r_lid_path
        
        super(ShopArticle, self).save(force_insert, force_update, forced_id_insert)

        # create or update main variant
        if self.variants:
            self._update_main_variant().save()
        else:
            for v in self.variant_set.all():
                v.delete()
        

post_delete.connect(AbstractShopArticle.post_delete, sender=ShopArticle)


class ArticleVariant(AbstractShopArticle):
    qty_label = u'ilość'

    owner = m.ForeignKey('ShopArticle', verbose_name=u'produkt', related_name=u'variant_set')
    main = m.BooleanField(u'główny', default=False, editable=False)
    variant = m.CharField(u'wariant', max_length=255, help_text=u'np. 10L, lub "biały"')
    qty = m.DecimalField(qty_label, blank=True, null=True, max_digits=14, decimal_places=4)

    class Meta:
        verbose_name = u'wariant'
        verbose_name_plural = u'warianty'

    def __unicode__(self):
        return u'%s (%s)' % (self.variant, self.article.cat_index)

    @property
    def unit_gross(self):
        return self.gross / self.qty if self.qty else self.gross

    @property
    def unit_net(self):
        return self.net / self.qty if self.qty else self.net

    @property
    def is_variant(self):
        return True

    @property
    def shoparticle(self):
        return self.owner

    @property
    def producer(self):
        return self.owner.producer

    @property
    def name(self):
        return self.owner.name

    @property
    def variants_name(self):
        return self.owner.variants_name

    @property
    def promotion(self):
        '''Overridden. If no own promo, get promo from owner (if owner's promo is set to cover all variants).'''
        if self.article.has_promotion:
            return AbstractShopArticle.promotion.fget(self)
        else:
            if self.owner.promotion.cover_variants:
                return self.owner.promotion.adapted_clone(self.article)

        return NonePromotion(self.article)

    @property
    def best_discount(self):
        '''Overridden. If no own promo/discount, inherit promo/discount from owner.'''
        if self.article.has_promotion or (self._client and self._client.discount(self).notNone): # TODO put to has_own_discount ?
            return AbstractShopArticle.best_discount.fget(self)
        else:
            if self.owner.promotion.cover_variants:
                return self.owner.best_discount.adapted_clone(self.article)
            else:
                return NoneDiscount(self.article)

    def release_article(self):
        self.article.r_used_variant = False
        if not self.main:
            super(ArticleVariant, self).release_article()

    def take_article(self):
        self.article.r_used_variant = True
        if not self.main:
            super(ArticleVariant, self).take_article()

    def _inherited_exec_time(self):
        return self.owner.exec_time if self.owner.exec_time else self.producer.exec_time

post_delete.connect(AbstractShopArticle.post_delete, sender=ArticleVariant)


class ArticleAttachment(m.Model):
    def get_upload_to(inst, fname):
        root, ext = path.splitext(fname)
        return utils.get_upload_to(settings.MEDIA_ROOT, 'attachment/',
                    slugify_pl(inst.article.name[:35] + '-' + inst.name)[:50] + ext)

    article = m.ForeignKey('ShopArticle', related_name='attachment_set')
    type = m.ForeignKey('FileType', verbose_name=u'typ pliku')
    name = m.CharField(u'nazwa', max_length=255)
    file = m.FileField(u'plik', upload_to=get_upload_to)
    listed = m.BooleanField(u'na liście', default=True,
            help_text=u'zaznacz jeśli ma być widoczny jako załącznik na stronie produktu')

    class Meta:
        verbose_name = u'załącznik'
        verbose_name_plural = u'załączniki'

    def __unicode__(self):
        return self.name

    def save(self, force_insert=False, force_update=False):
        orig, need_remove = None, False
        if self.id:
            orig = ArticleAttachment.objects.get(pk=self.id)
            if self.file.name != orig.file.name:
                need_remove = True

        super(ArticleAttachment, self).save(force_insert, force_update)
        if orig and need_remove:
            try:
                default_storage.delete(orig.file.name)
            except OSError:
                # TODO log error/warning here (file is missing/wrong permissions)
                pass


class ArticlePhoto(m.Model):
    
    def get_upload_to(inst, fname):
        root, ext = path.splitext(fname)
        fname = u'%s%s' % (inst.article.slug[:55], ext)
        return utils.get_upload_to(settings.MEDIA_ROOT, 'photo/', fname)

    article = m.ForeignKey('ShopArticle', related_name='photo_set')
    main = m.BooleanField(u'główne')
    large = m.BooleanField(u'powiększenie', default=True)
    alt = m.CharField(u'opis', max_length=255, blank=True, help_text=u'Domyślnie użyta zostanie nazwa produktu.')

    photo = sorl.ImageWithThumbnailsField(u'zdjęcie', upload_to=get_upload_to,
        thumbnail = { 'size': (300,300), 'quality': int(SystemParam.get('media_photo_quality')),
                      'options': []},
        extra_thumbnails = {
            'sthumb' : { 'size': (50,50), 'quality': int(SystemParam.get('media_thumb_quality')),
                        'options': []},
            'thumb' : { 'size': (100,100), 'quality': int(SystemParam.get('media_thumb_quality')),
                        'options': []},
            'large' : { 'size': (900,650), 'quality': int(SystemParam.get('media_large_photo_quality')) }
        },
        generate_on_save=True,
        help_text=u'Zdjęcie zostanie automatycznie zmniejszone do odpowiednich rozmiarów. Oryginał będzie również przechowywany.')

    def __unicode__(self):
        return self.alt

    class Meta:
        verbose_name = u'zdjęcie'
        verbose_name_plural = u'zdjęcia'

    @staticmethod
    def _get_default_photo():
        default_photo = ArticlePhoto({ 'id' : -1 })
        default_photo.photo = { 'thumbnail' : path.join(settings.MEDIA_URL,'img/art-default.jpg') }
        default_photo.photo['extra_thumbnails'] = { 'thumb' : path.join(settings.MEDIA_URL,'img/art-sdefault.jpg') }
        default_photo.main = True
        default_photo.large = False
        return default_photo
    
ArticlePhoto.Default = ArticlePhoto._get_default_photo()


class ArticleVideo(m.Model):
    pass


class Opinion(m.Model):
    article = m.ForeignKey('ShopArticle', verbose_name=u'produkt')

    author = m.CharField(u'autor', max_length=255, blank=True)
    client_login = m.CharField(u'klient', max_length=255, blank=True, editable=False)
    rating = m.IntegerField(u'ocena')
    content = m.TextField(u'treść', blank=True)
    created = m.DateTimeField(u'data utworzenia', default=dt.datetime.now)
    blocked = m.BooleanField(u'zablokowana')
    abuse_count = m.IntegerField(u'zgłoszenia nadużycia', default=0,
        help_text=u'Ilość zgłoszeń nadużycia regulaminu przez użytkowników.')

    class Meta:
        verbose_name = u'opinia o produkcie'
        verbose_name_plural = u'opinie o produktach'
        ordering = ['-created']

    @staticmethod
    def post_delete(sender, instance, **kwargs):
        instance.article.recalc_opinion_stats()
        instance.article.save()

    @staticmethod
    def post_order_close(order):
        from dshop.main import services
        if SystemParam.get(key='opinions_active') == "1" and \
           SystemParam.get(key='opinions_email_notif') == "1":
               
            if order.client.can_send_req_for_opinion():
                services.send_request_for_opinion(order)
                order.client.req_for_opinion_sent = dt.date.today()
                order.client.save()

    def __unicode__(self):
        return u'%s (%d)' % (self.author, self.rating)

    def is_anonymous(self):
        return False if self.client_login else True

    def snippet(self):
        if len(self.content) > 100:
            return self.content[:100] + ' ...'
        else:
            return self.content
    snippet.short_description = u'treść'

    def short_snippet(self):
        return filters.truncatewords(self.content, 8)

    def save(self, force_insert=False, force_update=False):
        super(Opinion, self).save(force_insert, force_update) # cover case when article is changed
        self.article.recalc_opinion_stats()
        self.article.save()

post_delete.connect(Opinion.post_delete, sender=Opinion)

class FileType(m.Model):
    def get_upload_to(inst, fname):
        return u'file_type/' + inst.slug + path.splitext(fname)[1]
    
    name = m.CharField(u'nazwa', unique=True, max_length=255)
    icon = m.FileField(u'ikona', blank=True, upload_to=get_upload_to,
            help_text=u'Ikona zostanie przeskalowana do roździelczości 16x16 pikseli.')

    class Meta:
        verbose_name = u'typ pliku'
        verbose_name_plural = u'typy plików'

    def __unicode__(self):
        return self.name

    @property
    def slug(self):
        return slugify_pl(self.name)[:55]

    def save(self, force_insert=False, force_update=False):
        if self.id:
            orig = FileType.objects.get(pk=self.id)
            if self.icon.name != orig.icon.name:
                try:
                    default_storage.delete(orig.icon.name)
                except OSError:
                    # TODO log error/warning here (file is missing/wrong permissions)
                    pass
        if self.icon:
            self.icon._name = utils.img_resize(self.icon.name,
                        16, 16,
                        85,
                        rename=False,
                        modifier='!',
                        ext='.png')

        super(FileType, self).save(force_insert, force_update)


class Discount(m.Model):
    class Nature:
        FIXED = 'F'
        PERCENT = 'P'

    TYPE = None

    NATURE_CHOICES = (
        (Nature.FIXED, u'stały'),
        (Nature.PERCENT, u'procentowy')
    )
    
    nature = m.CharField(u'typ', max_length=16, default=Nature.PERCENT, choices=NATURE_CHOICES)
    cover_variants = m.BooleanField(u'Obejmij warianty produktu', default=False,
            help_text=u'Dotyczy produktów posiadających warianty. Gdy zaznaczone, obniżka obejmie wszystkie warianty wybranego produktu.')
    net = m.DecimalField(u'cena netto', max_digits=18, decimal_places=6)
    gross = m.DecimalField(u'cena brutto', max_digits=18, decimal_places=6)
    price_calc = m.CharField(u'obliczaj na podst. ceny', max_length=2, choices=PRICE_CALC_CHOICES, default=PriceCalc.NET)
    percent = m.DecimalField(u'procent', max_digits=6, decimal_places=2)
    created = m.DateTimeField(u'data utworzenia', default=dt.datetime.now)
    
    class Meta:
        abstract = True    
    
    @staticmethod
    def better(d1, d2):
        '''Return better discount from given two. Return None if d1 and d2 are None.
           For different articles compare percentages. If discounts are equal then return d1.
        '''
        if not d1:
            return d2
        if not d2:
            return d1
        return d1 if d1.better_than(d2) else d2
    
    def better_than(self, d):
        '''Return True if self is better than given discount. For different articles compare percentages.'''
        if not d:
            return True
        if self.article == d.article:
            # we compare net prices because with minimal price differences percent value can be equal (percent field has precision 2)
            return True if self.net < d.net else False
        else:
            return True if self.percent > d.percent else False

    def same_price(self, d):
        '''Compare net and gross prices of both discounts. Return True if equal, False otherwise.'''
        if self.net == d.net and self.gross == d.gross:
            return True
        else:
            return False

    @property
    def orig_net(self):
        return self.article.net

    @property
    def orig_gross(self):
        return self.article.gross

    @property
    def unit_gross(self):
        '''Per unit gross price in case of quantity variant discount. Gross price otherwise.'''
        if self.article.used_by_variant():
            variant = self.article.articlevariant
            return self.gross / variant.qty if variant.qty else self.gross
        else:
            return self.gross

    @property
    def unit_net(self):
        '''Per unit net price in case of quantity variant discount. Net price otherwise.'''
        if self.article.used_by_variant():
            variant = self.article.articlevariant
            return self.net / variant.qty if variant.qty else self.net
        else:
            return self.net

    @property
    def isNone(self):
        return False

    @property
    def notNone(self):
        return True

    @property
    def is_promo(self):
        raise NotImplementedError()

    @property
    def is_discount(self):
        raise NotImplementedError()

    def active(self):
        '''True if discount price is lower than article's regular price. False otherwise.'''
        return True if self.better_than(NoneDiscount(self.article)) else False
    active.short_description = u'aktywny'
    active.boolean = True

    def shoparticle(self):
        return self.article.get_shoparticle()
    shoparticle.short_description = u'produkt'
    shoparticle.admin_order_field = u'article'

    def adapted_clone(self, article):
        disc = copy.copy(self)
        disc.id = None
        disc.article = article
        disc._recalc()
        return disc

    def save(self, force_insert=False, force_update=False):
        # calculate prices and percentages
        self._recalc()
        super(Discount, self).save(force_insert, force_update)

    def _recalc(self):
        '''Recalculate prices/percentages'''
        if self.nature == Discount.Nature.FIXED:
            if self.price_calc == PriceCalc.NET:
                self.gross = self.net * (1 + self.article.vat/100)
            else:
                self.net = self.gross / (1 + self.article.vat/100)

            self.percent = (1 - self.net/self.orig_net) * 100
        else:
            self.net = self.orig_net * (1 - self.percent / 100)
            self.gross = self.net * (1 + self.article.vat/100)


class NoneDiscount(Discount):
    TYPE = 'none'

    class Meta:
        abstract = True
    
    def __init__(self, article):
        self.id = -1
        self.article = article
        self.cover_variants = False

    @property
    def isNone(self):
        return True
    @property
    def notNone(self):
        return False
    def save(self):
        pass
    def delete(self):
        pass
    @property
    def price_calc(self):
        return self.article.price_calc
    @property
    def net(self):
        return self.article.net
    @property
    def gross(self):
        return self.article.gross
    @property
    def percent(self):
        return Decimal(0)
    @property
    def is_promo(self):
        return False
    @property
    def is_discount(self):
        return False


class ClientDiscount(Discount):
    TYPE = 'discount'
    client = m.ForeignKey('Client', verbose_name=u'klient', related_name=u'discount_set')
    article = m.ForeignKey('Article', verbose_name=u'produkt magazynowy', related_name=u'discount_set')

    class Meta:
        verbose_name = u'rabat'
        verbose_name_plural = u'rabaty'
        unique_together = ('client', 'article')

    def __unicode__(self):
        return u'%s - %s' % (self.client.login, self.article.cat_index)

    @property
    def is_promo(self):
        return False

    @property
    def is_discount(self):
        return True


class Promotion(Discount):
    TYPE = 'promo'
    article = m.OneToOneField('Article', verbose_name=u'produkt magazynowy', related_name=u'promotion')
    short_desc = m.TextField(u'opis promocyjny', blank=True,
            help_text=u'Jeśli podany, zastępuje krótki opis produktu.')

    class Meta:
        verbose_name = u'promocja'
        verbose_name_plural = u'promocje'

    def __unicode__(self):
        return u'%s (%s%%)' % (self.article.cat_index, self.percent)

    @property
    def is_promo(self):
        return True

    @property
    def is_discount(self):
        return False


class NonePromotion(NoneDiscount):
    class Meta:
        abstract = True
    
    @property
    def short_desc(self):
        return self.article.short_desc


class Cart(m.Model):
    client = m.ForeignKey('Client', verbose_name=u'klient', blank=True, null=True)
    is_order = m.BooleanField(u'jest zamówieniem', editable=False)
    session_key = m.CharField(u'Id sesji', max_length=40, editable=False, null=True)

    class Meta:
        verbose_name = u'koszyk'
        verbose_name_plural = u'koszyki'

    def item_count(self):
        return self.item_set.count()

    def item_count_even(self):
        return True if self.item_set.count() % 2 == 0 else False

    @property
    def item_set(self):
        return self.cartitem_set

    def orig_net(self):
        return self._sum_items('sum_orig_net')

    def orig_gross(self):
        return self._sum_items('sum_orig_gross')

    def discount_net(self):
        return self._sum_items('sum_discount_net')

    def discount_gross(self):
        return self._sum_items('sum_discount_gross')

    def items_discount_net(self):
        '''Net sum cost of items (without delivery cost in case of order).'''
        return self._sum_items('sum_discount_net')

    def items_discount_gross(self):
        '''Gross sum cost of items (without delivery cost in case of order).'''
        return self._sum_items('sum_discount_gross')

    def savings_net(self):
        return self.orig_net() - self.discount_net()

    def savings_gross(self):
        return self.orig_gross() - self.discount_gross()

    def is_discount(self):
        return True if money(self.orig_net()) > money(self.discount_net()) else False

    def promo_points(self):
        '''Promo points that this cart is worth. Take into account client's points multiplier.'''
        gross = self.items_discount_gross()
        if self.client:
            points = gross
        else:
            points = gross * self.client.promo_multiplier
        return points.quantize(Decimal(1), decimal.ROUND_UP)

    def add_item(self, abstr_article, qty):
        '''Adds given AbstractShopArticle to cart items. Do nothing if qty is <= 0.'''
        if qty <= 0:
            return
        try:
            item = self.item_set.get(article_id=abstr_article.article.id)
            item.add_qty(qty)
        except CartItem.DoesNotExist:
            item = CartItem(owner=self)
            item.set_abstr_article(abstr_article.inject_client(self.client))
            item.set_qty(qty)
        item.save()

    def remove_item(self, article_id):
        '''Remove item from cart. Return True if item was found and removed, False otherwise.'''
        items = list(self.item_set.filter(article_id=article_id))
        if len(items) == 0:
            return False
        else:
            for item in items:
                item.delete()
            return True

    def recalc_items(self, qty_dict):
        '''Update item quantities using given dictionary ['qty-<article_id>' -> qty].'''
        for item in self.item_set.all():
            qty = qty_dict.get('qty-%d' % item.article_id, None)
            if qty is not None:
                self.set_qty(item, qty)

    def set_client(self, client):
        '''Attach cart to the client and calculate new discounts for cart items.'''
        self.client = client
        self.refresh_items()

    def refresh_items(self):
        '''Recalculate discounts for cart items. Items for which their article is missing will be deleted.'''
        for ci in self.item_set.all():
            if ci.article_if_published:
                ci.recalc_discount(self.client)
                ci.save()
            else:
                ci.delete()
        

    def set_qty(self, item, qty):
        '''Set quantity on cart item. Remove item if quantity is <= 0.'''
        if qty <= 0:
            item.delete()
        else:
            item.set_qty(qty)
            item.save()

    def clear(self):
        for item in self.item_set.all():
            item.delete()

    def exec_time(self):
        '''Estimated execution time. Estimation is based on item's execution times.
           Worst item's time is taken as cart's execution time.
        '''
        exec_times = [ci.exec_time for ci in self.item_set.all()]
        return reduce(lambda x,y: ExecutionTime.worse(x,y), exec_times)

    def delivery_half_refund(self):
        refund_level = int(SystemParam.get('delivery_half_refund_level'))
        if self.items_discount_gross() >= refund_level:
            return { 'granted' : True, 'level' : refund_level }
        else:
            return { 'granted' : False, 'level' : refund_level }

    def delivery_full_refund(self):
        refund_level = int(SystemParam.get('delivery_full_refund_level'))
        if self.items_discount_gross() >= refund_level:
            return { 'granted' : True, 'level' : refund_level }
        else:
            return { 'granted' : False, 'level' : refund_level }

    def producers(self):
        '''Set of items' producers (distinct). Items related to deleted articles are not included.'''
        return set(
                [ci.article.get_shoparticle().producer
                for ci in self.item_set.all() if ci.article_if_published])

    def suppliers(self):
        '''Set of items' suppliers (distinct). Items related to deleted articles are not included.
           If article does not have supplier, it will be represented as None in the set.
        '''
        return set(
                [ci.article.supplier
                for ci in self.item_set.all() if ci.article])

    def params(self):
        '''Set of items' parameter names (distinct).'''
        return set([ci.param_name for ci in self.item_set.all() if ci.param])

    def weight(self):
        '''Return weight of this cart (in kg).'''
        sum = Decimal(0)
        for item in self.item_set.all():
            sum += item.total_weight()
        return sum
    
    def __unicode__(self):
        return u'%d (%s)' % (self.id, self.client if self.client else u'')

    def _sum_items(self, field):
        sum = Decimal(0)
        for item in self.item_set.all():
            sum += round_if_need(getattr(item, field))
        return sum

    def delete(self, *args, **kwargs):
        if self.is_order:
            send_mail(u'dshop-opt: order deletion detected', str(self) + ''.join(traceback.format_stack()), 'sklep@optionall.pl',
                     ['it@optionall.pl'], fail_silently=True)
        else:
            return super(Cart, self).delete(*args, **kwargs)


class AbstractCartItem(m.Model):

    # It's not a foreign key because we don't want to depend on article objects.
    article_id = m.IntegerField(u'id produktu', editable=False)
    qty = m.DecimalField(u'ilość', default=1, max_digits=10, decimal_places=4)
    param_value = m.TextField(u'wartość parametru', blank=True)
    created = m.DateTimeField(u'data utworzenia', default=dt.datetime.now, editable=False)

    # Following fields are redundant to fields related with article. They are used
    # because CartItem and OrderItem need to work even when original article has been deleted.
    cat_index = m.CharField(u'numer katalogowy', max_length=255, editable=False)
    stock_id = m.IntegerField(u'ID magazynowe', blank=True, null=True, editable=False)
    name = m.CharField(u'nazwa', max_length=255, editable=False)

    variant = m.BooleanField(u'wariant', editable=False)
    variants_name = m.CharField(u'nazwa wariantów', max_length=255, blank=True, editable=False)
    variant_name = m.CharField(u'nazwa wariantu', max_length=255, blank=True, editable=False)

    unit_short = m.CharField(u'nazwa jednostki', max_length=255, editable=False)
    unit_precision = m.DecimalField(u'precyzja jednostki', max_digits=8, decimal_places=4, editable=False)

    param = m.BooleanField(u'parametr', editable=False)
    param_name = m.CharField(u'nazwa parametru', max_length=255, blank=True, editable=False)
    param_name_plural = m.CharField(u'nazwa parametru w l. mnogiej', max_length=255, blank=True, editable=False)
    weight = m.DecimalField(u'waga (kg)', max_digits=14, decimal_places=4)
    
    # Following fields are also redundant but there is an additional reason behind it. These values,
    # after CartItem has been created, should not change even when respective values in related
    # article have been changed.
    orig_net = m.DecimalField(u'cena netto', max_digits=18, decimal_places=6, editable=False)
    orig_gross = m.DecimalField(u'cena brutto', max_digits=18, decimal_places=6, editable=False)
    discount_price_calc = m.CharField(u'obliczaj na podst.', max_length=2, choices=PRICE_CALC_CHOICES, default=PriceCalc.NET)
    discount_net = m.DecimalField(u'cena netto', max_digits=18, decimal_places=6)
    discount_gross = m.DecimalField(u'cena brutto', max_digits=18, decimal_places=6)

    class Meta:
        abstract = True
        ordering = ['created']

    def set_qty(self, qty):
        '''Set quantity. Round UP to article's precision. Prevent from setting to 0 or less.'''
        assert self.unit_precision, u'unit_precision is unknown, set article first.'
        qty = qty if qty > 0 else 1
        
        mult = qty / self.unit_precision
        self.qty = self.unit_precision * mult.quantize(Decimal(1), decimal.ROUND_UP)
        return self.qty

    def add_qty(self, qty):
        '''Add quantity. Round UP to article's precision. Prevent from setting to 0 or less.'''
        return self.set_qty(self.qty + qty)

    @property
    def vat(self):
        return ((self.orig_gross / self.orig_net) - 1) * 100

    @property
    def sum_discount_gross(self):
        return self.discount_gross * self.qty

    @property
    def sum_discount_net(self):
        return self.discount_net * self.qty

    @property
    def sum_orig_gross(self):
        return self.orig_gross * self.qty

    @property
    def sum_orig_net(self):
        return self.orig_net * self.qty

    @property
    def is_discount(self):
        return True if money(self.orig_net) > money(self.discount_net) else False

    @property
    def article(self):
        '''Return associated article or None if associated article doesn't exist.'''
        try:
            return Article.objects.get(pk=self.article_id)
        except Article.DoesNotExist:
            return None

    @property
    def article_if_published(self):
        '''Return article if related article exist and is published on the shop as ShopArticle or Variant.'''
        art = self.article
        if art and art.get_shoparticle():
            return art
        else:
            return None

    @property
    def exec_time(self):
        '''Calculate execution time. If article is missing return NoneExecutionTime.'''
        article = self.article_if_published
        if article:
            return article.get_abstr_article().real_exec_time()
        else:
            return NoneExecutionTime()

    def total_weight(self):
        return self.weight * self.qty

    def recalc_discount(self, client):
        '''Recalculate discounts for given client. If article is missing, do nothing.'''
        article = self.article_if_published
        if article:
            best_discount = article.get_abstr_article().inject_client(client).best_discount
            self.discount_net = best_discount.net
            self.discount_gross = best_discount.gross
        else:
            pass

    def set_abstr_article(self, abstr_art):
        '''Fill cart item with given abstract article (shoparticle or articlevariant) values.
           Calculates best discount (client should be injected to abstr_article before).
        '''
        self.article_id = abstr_art.article.id
        self.cat_index = abstr_art.cat_index
        self.stock_id = abstr_art.stock_id
        self.name = abstr_art.name

        self.variant = abstr_art.is_variant
        if self.variant:
            self.variants_name = abstr_art.variants_name
            self.variant_name = abstr_art.variant
        else:
            self.variants_name = u''
            self.variant_name = u''

        self.unit_short = abstr_art.unit.short
        self.unit_precision = abstr_art.unit.precision
        
        if abstr_art.shoparticle.param:
            self.param = True
            self.param_name = abstr_art.shoparticle.param.name
            self.param_name_plural = abstr_art.shoparticle.param.name_plural
        else:
            self.param = False
            self.param_name = u''
            self.param_name_plural = u''
            self.param_value = u''
        self.weight = abstr_art.weight

        self.orig_net = abstr_art.net
        self.orig_gross = abstr_art.gross

        best_discount = abstr_art.best_discount
        self.discount_price_calc = best_discount.price_calc
        self.discount_net = best_discount.net
        self.discount_gross = best_discount.gross

    @classmethod
    def create_from(cls, item, **kwargs):
        '''Create item as a copy of other item.'''
        return cls(**kwargs).copy_from(item)
    
    def copy_from(self, item):
        '''Copy all (except id) AbstractCartItem fields from given item. Return self.'''
        fields = AbstractCartItem._meta.get_all_field_names()
        for f in fields:
            if f != 'id':
                setattr(self, f, getattr(item, f))
        return self

    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.cat_index)

    def save(self, *args, **kwargs):
        if self.discount_price_calc == PriceCalc.NET:
            self.discount_gross = self.discount_net * (1 + self.vat/100)
        else:
            self.discount_net = self.discount_gross / (1 + self.vat/100)
        super(AbstractCartItem, self).save(*args, **kwargs)


class CartItem(AbstractCartItem):
    owner = m.ForeignKey('Cart', verbose_name=u'koszyk')

    class Meta:
        verbose_name = u'element koszyka'
        verbose_name_plural = u'elementy koszyka'


class Company(m.Model):
    name = m.CharField(u'nazwa', max_length=255)
    addr_street = m.CharField(u'ulica i nr', max_length=255)
    addr_town = m.CharField(u'miejscowość', max_length=255)
    addr_code = m.CharField(u'kod pocztowy', max_length=255)
    account_bank = m.CharField(u'bank', max_length=255)
    account_no = m.CharField(u'numer konta', max_length=255)

    class Meta:
        verbose_name = u'dane firmy'
        verbose_name_plural = u'dane firmy'

    def __unicode__(self):
        return self.name


class Counter(m.Model):
    ORDERS = 'orders' # ilość zamówień w aktualnym roku kalendarzowym

    name = m.CharField(u'nazwa', max_length=255, unique=True)
    value = m.IntegerField(u'wartość')

    class Meta:
        verbose_name = u'licznik'
        verbose_name_plural = u'liczniki'

    def __unicode__(self):
        return self.name


class Order(Cart):
    class Status:
        NEW = 'NE'
        ACCEPTED = 'AC'
        READY_TO_SEND = 'RE'
        SENT = 'SE'

        # Final statuses
        REJECTED = 'RJ'
        CANCELLED = 'CA'
        CLOSED = 'CL'
        RETURNED = 'RT'

        # Sets
        BEFORE_SEND = set([NEW, ACCEPTED, READY_TO_SEND])
        NOT_FINAL = set([NEW, ACCEPTED, READY_TO_SEND, SENT])
        FINAL = set([REJECTED, CANCELLED, CLOSED, RETURNED])

    class Payment:
        TRANSFER = 'TR'
        ONLINE = 'ON'
        CASH = 'CA'
        DELAYED = 'DE'

    class PaymentStatus:
        NONE = '0'
        NEW = '1'
        CONFIRMED = '2'
        REJECTED = '3'
        CANCELLED = '4'
        COMPLAINT = '5'

    STATUS_CHOICES = (
        (Status.NEW, u'nowe'),
        (Status.ACCEPTED, u'w realizacji'),
        (Status.READY_TO_SEND, u'gotowe do wysyłki'),
        (Status.SENT, u'wysłane'),
        (Status.REJECTED, u'odrzucone'),
        (Status.CANCELLED, u'anulowane'),
        (Status.CLOSED, u'zamknięte'),
        (Status.RETURNED, u'zwrócone')
    )

    PAYMENT_CHOICES = (
        (Payment.TRANSFER, u'przelew'),
        (Payment.ONLINE, u'online'),
        (Payment.CASH, u'przy odbiorze'),
        (Payment.DELAYED, u'termin płatności')
    )

    PAYMENT_STATUS_CHOICES = (
        (PaymentStatus.NONE, u'brak'),
        (PaymentStatus.NEW, u'nowa'),
        (PaymentStatus.CONFIRMED, u'wykonana'),
        (PaymentStatus.REJECTED, u'odmowna'),
        (PaymentStatus.CANCELLED, u'anulowana'),
        (PaymentStatus.COMPLAINT, u'reklamacja')
    )
    
    invoice_address = m.OneToOneField('InvoiceAddress', verbose_name=u'dane do faktury')
    sent_to_supplier = m.ForeignKey('Supplier', editable=False, blank=True, null=True, db_index=True)

    submitted = m.BooleanField(u'złożone', default=True, editable=False, db_index=True)
    number = m.CharField(u'numer', max_length=80, blank=True, unique=True, db_index=True)
    stock_id = m.IntegerField(u'ID magazynowe', unique=True, db_index=True, blank=True, null=True, editable=False)
    stock_number = m.CharField(u'numer magazynowy', max_length=255, blank=True, db_index=True)
    status = m.CharField(u'status', max_length=2, default=Status.NEW, choices=STATUS_CHOICES, db_index=True)
    created = m.DateTimeField(u'data utworzenia', default=dt.datetime.now, db_index=True)
    execution_date = m.DateField(u'termin realizacji', blank=True, null=True,
            help_text=u'Podaj przewidywany termin realizacji (dzień wysyłki).')

    payment = m.CharField(u'forma płatności', max_length=2, db_index=True, choices=PAYMENT_CHOICES, default=Payment.TRANSFER)
    payment_amount = m.DecimalField(u'kwota płatności', max_digits=18, decimal_places=2, blank=True, null=True)
    payment_status = m.CharField('status płatności', max_length=2, db_index=True, default=PaymentStatus.NONE, choices=PAYMENT_STATUS_CHOICES)
    payment_trans_num = m.CharField('numer transakcji', max_length=255, blank=True,
            help_text=u'W przypadku przelewu możesz wpisać tytuł i/lub datę przelewu.')
    payment_deadline = m.DateField(u'termin płatności', blank=True, null=True)

    suspended = m.BooleanField(u'wstrzymane',
        help_text=u'Wstrzymaj przed wysłaniem, używaj gdy zamówienie wymaga konsultacji, zmian, etc.')
    comments = m.TextField(u'uwagi', blank=True)
    inv_client = m.FileField(u'faktura dla odbiorcy', blank=True, upload_to='invoices/%Y/%m', help_text=u'Faktura dla klienta')
    inv_perfekt = m.FileField(u'faktura od dostawcy', blank=True, upload_to='invoices/%Y/%m', help_text=u'Faktura dla PERFEKT')
    
    objects = managers.OrderManager()

    class Meta:
        verbose_name = u'zamówienie'
        verbose_name_plural = u'zamówienia'

    def __unicode__(self):
        return self.number

    def get_absolute_url(self):
        return reverse('dshop-myorder', args=[self.created.year, self.id])

    @property
    def item_set(self):
        return self.orderitem_set

    @classmethod
    def create_from(cls, cart):
        '''Create new order from given cart (or order since order is a cart).
           Order will not be submitted (will be non existent in admin).

           Non submitted order have temporary order number (prefixed with "TEMP-").
           Order should be marked as submitted after client will go through whole
           order placement process and ultimately will approve the order.
        '''
        order = cls(client=cart.client, submitted=False)
        order.assign_number(submitted=False)
        order.set_shipment_and_invoice_addr(cart.client.base_address, cart.client.base_address)

        for citem in cart.item_set.all():
            item = OrderItem.create_from(citem)
            order.item_set.add(item)

        shipment = order.shipment()
        Shipper.assign_to(shipment)
        shipment.save()
        
        return order

    @classmethod
    def create_submitted(cls, client):
        order = cls(client=client, submitted=True)
        order.assign_number(submitted=True)
        order.set_shipment_and_invoice_addr(client.base_address, client.base_address)
        return order

    def assign_number(self, submitted):
        '''Assign new order number.'''
        self.number = Order.objects.get_next_number(submitted)

    def set_shipment_and_invoice_addr(self, invoice_addr, shipment_addr):
        '''Set invoice and shipping address, create new shimpent object. Order is saved. Shipper is not assigned here.'''
        addr = InvoiceAddress()
        addr.copy_from(invoice_addr)
        addr.save()

        self.invoice_address = addr
        self.save()

        shipment = Shipment(order=self)
        shipment.copy_from(shipment_addr)
        shipment.save()

    def submit(self):
        '''Submit order. Assigns new, permanent order number. Do some other stuff.'''
        self.number = Order.objects.get_next_number(submitted=True)
        self.created = dt.datetime.now()
        self.submitted = True

        if self.payment == Order.Payment.DELAYED:
            self.payment_deadline = dt.datetime.now() + dt.timedelta(days=self.client.payment_deadline)

    def send(self):
        '''Set status to SENT and set shipment sent date. Shipment is saved. Return shipment.'''
        self.status = Order.Status.SENT
        shipment = self.shipment()

        assert Shipment, "Can't send order %s cause shipment is missing" % self
        shipment.sent = dt.datetime.now()
        shipment.save()
        return shipment

    @property
    def full_payment_done(self):
        '''True if payment status is CONFIRMED and payment amount is equal or exceed order amount.
           If payment_amount is None then it is considered as it would be equal to order amount (full paid).
        '''
        if self.payment_status == Order.PaymentStatus.CONFIRMED:
            gross = self.discount_gross().quantize(Decimal("1.00"));
            if not self.payment_amount or self.payment_amount >= gross:
                return True
        return False

    def shipment(self):
        '''Return shipment or None if no shipment is available.'''
        try:
            return self.shipment_set.all()[0]
        except IndexError:
            return None

    def orig_net(self):
        return self._sum_items('sum_orig_net') + round_if_need(self.shipment().net)

    def orig_gross(self):
        return self._sum_items('sum_orig_gross') + round_if_need(self.shipment().gross)

    def discount_net(self):
        return self._sum_items('sum_discount_net') + round_if_need(self.shipment().discount_net)

    def discount_gross(self):
        return self._sum_items('sum_discount_gross') + round_if_need(self.shipment().discount_gross)

    def execution_today(self):
        '''Return True if execution date is today.'''
        assert self.execution_date, "Order %s, execution_date is None." % self

        if dt.date.today() == self.execution_date:
            return True
        else:
            return False

    def execution_passed(self):
        '''Return true if order's execution date has passed and order is still not send.'''
        assert self.execution_date, "Order %s, execution_date is None." % self
        
        if self.status in ['NE', 'AC', 'RE']:
            if self.execution_date < dt.date.today():
                return True
        return False
    
    def can_be_sent_to_supplier(self):
        '''Return supplier whether order can be sent for processing to the external supplier.
           None otherwise.
        '''
        suppliers = self.suppliers()
        if None not in suppliers and len(suppliers) == 1:
            return suppliers.pop()
        return None
    
    def save(self, *args, **kwargs):
        super(Order, self).save(*args, **kwargs)
        self.cart_ptr.is_order = True
        self.cart_ptr.save()

    def delete(self, *args, **kwargs):
        send_mail(u'dshop-opt: order deletion detected', str(self) + ''.join(traceback.format_stack()), 'sklep@optionall.pl',
        ['it@optionall.pl'], fail_silently=True)

    @staticmethod
    def pre_delete(sender, instance, **kwargs):
        send_mail(u'dshop-opt: order deletion detected', str(instance) + ''.join(traceback.format_stack()), 'sklep@optionall.pl',
        ['it@optionall.pl'], fail_silently=True)

pre_delete.connect(Order.pre_delete, sender=Order)

class InvoiceAddress(BaseAddress):
    class Meta:
        verbose_name = u'dane do faktury'
        verbose_name_plural = u'dane do faktury'


class OrderItem(AbstractCartItem):
    owner = m.ForeignKey('Order', verbose_name=u'zamówienie')

    class Meta:
        verbose_name = u'pozycja zamówienia'
        verbose_name_plural = u'pozycje zamówienia'


class OrderNote(m.Model):
    order = m.ForeignKey('Order', verbose_name=u'zamówienie')
    created = m.DateTimeField(u'data utworzenia', default=dt.datetime.now)
    content = m.TextField(u'treść', blank=True)

    class Meta:
        verbose_name = u'notatka'
        verbose_name_plural = u'notatki'

    def __unicode__(self):
        return u'%s' % unicode(self.created)


class Shipment(BaseAddress):
    
    class PkgType:
        PACKAGE = 'PKG'
        PALLET = 'PAL'

    PKG_TYPE_CHOICES = (
        (PkgType.PACKAGE, u'paczka'),
        (PkgType.PALLET, u'paleta')
    )

    order = m.ForeignKey('Order', verbose_name=u'zamówienie')

    auto_shipper = m.BooleanField(u'auto kurier', default=True)
    auto_params = m.BooleanField(u'auto parametry', default=True)
    pkg_type = m.CharField(u'rodzaj pakowania', max_length=6, choices=PKG_TYPE_CHOICES, default=PkgType.PACKAGE)
    pkg_count = m.IntegerField(u'ilość pakunków', default=0)

    shipper_name = m.CharField(u'kurier', max_length=255, default='nie przydzielono')
    identifier = m.CharField(u'numer listu przewozowego', max_length=255, blank=True)
    sent = m.DateTimeField(u'data wysłania', blank=True, null=True)

    net = m.DecimalField(u'cena netto', max_digits=18, decimal_places=6, default=Decimal(0))
    gross = m.DecimalField(u'cena brutto', max_digits=18, decimal_places=6, default=Decimal(0))
    discount_net = m.DecimalField(u'cena netto', max_digits=18, decimal_places=6, default=Decimal(0))
    discount_gross = m.DecimalField(u'cena brutto', max_digits=18, decimal_places=6, default=Decimal(0))
    price_calc = m.CharField(u'obliczaj na podst. ceny', max_length=2, choices=PRICE_CALC_CHOICES, default=PriceCalc.NET)

    class Meta:
        verbose_name = u'przesyłka'
        verbose_name_plural = u'przesyłki'

    def shipper(self):
        '''Return associated shipper object or None if no shipper is set or shipper doesn't exist.'''
        if self.shipper_name:
            try:
                return Shipper.objects.get(name=self.shipper_name)
            except Shipper.DoesNotExist:
                return None
        else:
            return None

    def apply_shipper_eval_if_auto(self, seval):
        '''Apply shipment evaluation results. Set shipper and shipment params.
           If auto_params is false, only shipper will be set.
        '''
        assert seval.banned == False, "Cannot assign banned shipper to shipment!"
        
        self.shipper_name = seval.shipper.name
        if self.auto_params:
            self.pkg_type = seval.pkg_type
            self.pkg_count = seval.pkg_count

            self.net = seval.net
            self.gross = seval.gross
            self.discount_net = seval.discount_net
            self.discount_gross = seval.discount_gross


class Shipper(m.Model):
    class BanReason:
        WEIGHT = 'W'  # Weight too high or too low
        LIMITS = 'L'  # Shipping limits like banned producer or whole article category
        ABILITY = 'A' # Lack of shipper's ability to ship order as a package or pallet

    class Category:
        POST        = 'post'
        SHIPPER     = 'shipper'
        PLT_SHIPPER = 'plt-shipper'

    CATEGORY_CHOICES = (
        (Category.POST, u'Poczta - paczki i koperty'),
        (Category.SHIPPER, u'Spedytor - paczki'),
        (Category.PLT_SHIPPER, u'Spedytor - palety, duże ładunki')
    )

    name = m.CharField(u'spedytor', max_length=255, unique=True)
    invoice_name  = m.CharField(u'nazwa na fakturze', max_length=255)
    order = m.IntegerField(u'kolejność', blank=True, null=True)
    vat = m.DecimalField(u'VAT (%)', max_digits=6, decimal_places=2)
    shipment_tracking_url = m.URLField(u'adres url do śledzenia przesyłek', blank=True)

    category = m.CharField(u'kategoria', max_length=255, choices=CATEGORY_CHOICES)
    packages = m.BooleanField(u'obsługuje paczki')
    package_wrapping_weight = m.DecimalField(u'waga opakowania paczki (kg)', blank=True, null=True,
            max_digits=8, decimal_places=4)

    pallets = m.BooleanField(u'obsługuje palety')
    pallet_capacity = m.DecimalField(u'ładowność palety (kg)', blank=True, null=True, max_digits=8, decimal_places=2)
    
    cash_on_delivery = m.BooleanField(u'płatność przy odbiorze')
    cash_on_delivery_net = m.DecimalField(u'Opłata za płatność przy odbiorze (netto)',
            blank=True, null=True, max_digits=18, decimal_places=6)

    excluded_producers = m.ManyToManyField('Producer', blank=True, verbose_name=u'wykluczeni producenci')
    excluded_categories = m.ManyToManyField('Category', blank=True, verbose_name=u'wykluczone kategorie produktów')

    objects = managers.ShipperManager()

    class Meta:
        verbose_name = u'spedytor'
        verbose_name_plural = u'spedytorzy'
        ordering = ['order']

    def __unicode__(self):
        return self.name

    @classmethod
    def assign_to(cls, shipment):
        '''If shipment.auto_shipper is True assign best shipper to shipment.
           Otherwise recalculate shipment parameters using current shipment's shipper.

           If auto_shipper is False and evaluation for current shipper results in 'banned'
           then auto_shipper is set to True and evaluation is done again to assign valid shipper.

           If auto_shipper is False but current shipper is missing (has been deleted)
           then auto_shipper is set to True and evaluation is done again to assign new shipper.
        '''
        if shipment.auto_shipper:
            seval = cls.best_evaluation(shipment.order)
        else:
            try:
                seval = cls.objects.get(name=shipment.shipper_name).evaluate_params(shipment.order)
                if seval.banned:
                    shipment.auto_shipper = True
                    seval = cls.best_evaluation(shipment.order)
            except Shipper.DoesNotExist:
                # TODO log notce here that order's current shipper has been removed
                shipment.auto_shipper = True
                seval = cls.best_evaluation(shipment.order)
        
        shipment.apply_shipper_eval_if_auto(seval)

    def assign(self, shipment):
        '''Assign this shipper to given shipment. Set auto_shipper to False in shipment.'''
        seval = self.evaluate_params(shipment.order)
        shipment.auto_shipper = False
        shipment.apply_shipper_eval_if_auto(seval)

    @classmethod
    def best_evaluation(cls, order):
        '''Return best evaluation result. Best means cheapest, other strategies can be implemented in future.'''
        best = reduce(lambda x,y: ShipmentEvalRes.cheaper(x,y), [s.evaluate_params(order) for s in cls.objects.all()])
        return best

    def cash_on_delivery_paid(self):
        '''True if cash on delivery option is additionally charged.'''
        if self.cash_on_delivery:
            if self.cash_on_delivery_net > 0:
                return True
        return False

    @property
    def cash_on_delivery_gross(self):
        return self.cash_on_delivery_net * (1 + (self.vat/100))

    def set_packages(self, pkgs):
        if not pkgs:
            for pth in self.package_set.all():
                pth.delete()
        self.packages = pkgs

    def set_pallets(self, plts):
        if not plts:
            for pth in self.pallet_set.all():
                pth.delete()
        self.pallets = plts

    def max_weight(self):
        '''Maximum supported weight. If shipper supports pallets then None is returned since
           then max weight is unlimited.
        '''
        if self.pallets:
            return None
        if self.packages:
            return self.package_set.order_by('-max_weight')[0].max_weight

    def evaluate_params(self, order):
        '''Evaluate shipment parameters for given order. Cheapest option is used (packages vs pallets).
           Assign discount if available.
        '''
        prods = order.producers()
        if not prods.isdisjoint(self.excluded_producers.all()):
            return ShipmentEvalRes(self, ban_reason=self.BanReason.LIMITS)

        if self._is_category_banned(order):
            return ShipmentEvalRes(self, ban_reason=self.BanReason.LIMITS)

        pkg_params = self._eval_package(order)
        pallet_params = self._eval_pallet(order)

        res = ShipmentEvalRes.cheaper(pkg_params, pallet_params)

        if not res.banned:
            if order.payment == Order.Payment.CASH and self.cash_on_delivery_paid():
                res.net += self.cash_on_delivery_net
                res.gross += self.cash_on_delivery_gross

            res.assign_discount(order)
        return res

    def _is_category_banned(self, order):
        cats = set(self.excluded_categories.all())
        for item in order.item_set.all():
            article = item.article_if_published
            if not article:
                return False
            cpath = article.get_shoparticle().category_path()
            if not cats.isdisjoint(cpath):
                return True
        return False
    
    def _eval_package(self, order):
        if not self.packages:
            return ShipmentEvalRes(self, ban_reason=self.BanReason.ABILITY)
        
        weight = order.weight() + self.package_wrapping_weight
        thresh = self._find_threshold(weight, self.package_set.all())
        
        if thresh:
            res = ShipmentEvalRes(self, Shipment.PkgType.PACKAGE, thresh.net, thresh.gross)
            return res
        else:
            return ShipmentEvalRes(self, ban_reason=self.BanReason.WEIGHT)
    
    def _eval_pallet(self, order):
        if not self.pallets:
            return ShipmentEvalRes(self, ban_reason=self.BanReason.ABILITY)

        res = ShipmentEvalRes(self, pkg_type=Shipment.PkgType.PALLET)
        max_thresh = self.pallet_set.order_by('-max_weight')[0]
        weight = order.weight()

        pallet_count = (weight / max_thresh.max_weight).quantize(Decimal(1), decimal.ROUND_UP)
        res.pkg_count = pallet_count
        # if zero then all pallets are full loaded
        last_pallet_weight = weight % max_thresh.max_weight
        
        if last_pallet_weight:
            thresh = self._find_threshold(last_pallet_weight, self.pallet_set.all())
            res.net = ((pallet_count - 1) * max_thresh.net) + thresh.net
            res.gross = ((pallet_count - 1) * max_thresh.gross) + thresh.gross
        else:
            res.net = pallet_count * max_thresh.net
            res.gross = pallet_count * max_thresh.gross
        
        return res
    
    def _find_threshold(self, weight, thresh_qset):
        for thrl in thresh_qset:
            if weight <= thrl.max_weight:
                return thrl
        return None


class ShipmentEvalRes(object):
    '''Result of shipper evaluation on particular order.'''

    def __init__(self, shipper, pkg_type='', net=None, gross=None, ban_reason=''):
        self.shipper = shipper
        self.pkg_type = pkg_type
        self.pkg_count = 1

        self.net = net
        self.gross = gross
        self.discount_net = None
        self.discount_gross = None

        self.banned = True if ban_reason else False
        self.ban_reason = ban_reason

    def __unicode__(self):
        return u'%s, %s, %s, %s, %s' % (self.shipper, self.banned, self.ban_reason, self.pkg_type, self.pkg_count)

    def __repr__(self):
        return u'<ShipmentEvalRes: %s>' % self.__unicode__()

    def is_discount(self):
        return True if self.net > self.discount_net else False

    @staticmethod
    def cheaper(res1, res2):
        '''Return cheaper shipment option. If one of the options is banned return the other one.
           Compare regular price, not discount price.
        '''
        if res1.banned and res2.banned:
            return res1 if res1.ban_reason == Shipper.BanReason.WEIGHT else res2
        if res1.banned:
            return res2
        if res2.banned:
            return res1

        return res1 if res1.net <= res2.net else res2

    def assign_discount(self, order):
        assert self.banned == False, "Cannot assign discount on banned shipper."
        half = order.delivery_half_refund()
        full = order.delivery_full_refund()

        if full['granted']:
            self.discount_net = Decimal(0)
            self.discount_gross = Decimal(0)
        elif half['granted']:
            self.discount_net = self.net / 2
            self.discount_gross = self.gross / 2
        else:
            self.discount_net = self.net
            self.discount_gross = self.gross


class ShipperThrl(m.Model):
    '''Shipper threshold model'''
    max_weight = m.DecimalField(u'maks. waga (kg)', max_digits=8, decimal_places=2)
    net = m.DecimalField(u'cena netto', max_digits=18, decimal_places=6)
    gross = m.DecimalField(u'cena brutto', max_digits=18, decimal_places=6)
    price_calc = m.CharField(u'obliczaj na podst. ceny', max_length=2, choices=PRICE_CALC_CHOICES, default=PriceCalc.NET)
    
    class Meta:
        abstract = True
        ordering = ['max_weight']

    def __unicode__(self):
        return u'(%s, %s)' % (self.max_weight, self.net)

    def save(self, force_insert=False, force_update=False):
        # calculate prices
        if self.price_calc == PriceCalc.NET:
            self.gross = self.net * (1 + self.shipper.vat/100)
        else:
            self.net = self.gross / (1 + self.shipper.vat/100)
        super(ShipperThrl, self).save(force_insert, force_update)


class ShipperPackageThrl(ShipperThrl):
    shipper = m.ForeignKey('Shipper', verbose_name=u'spedytor', related_name=u'package_set')
    
    class Meta:
        verbose_name = u'próg wagowy dla paczki'
        verbose_name_plural = u'progi wagowe dla paczek'
        unique_together = ('shipper', 'max_weight')


class ShipperPalletThrl(ShipperThrl):
    shipper = m.ForeignKey('Shipper', verbose_name=u'spedytor', related_name=u'pallet_set')
    
    class Meta:
        verbose_name = u'próg wagowy dla palety'
        verbose_name_plural = u'progi wagowe dla palet'
        unique_together = ('shipper', 'max_weight')


class PageFragment(m.Model):
    class Location:
        FOOTER = "footer"
        MPAGE_SIDEBAR_TOP = "mpage_st"
        MPAGE_SIDEBAR_BOTTOM = "mpage_sb"

    LOCATION_CHOICES = (
        (Location.FOOTER, u'stopka'),
        (Location.MPAGE_SIDEBAR_TOP, u'strona gł, boczny pasek, góra'),
        (Location.MPAGE_SIDEBAR_BOTTOM, u'strona gł, boczny pasek, dół')
    )

    name = m.CharField(u'nazwa', max_length=255, unique=True)
    location = m.CharField(u'położenie', max_length=50, choices=LOCATION_CHOICES, db_index=True)
    order = m.IntegerField(u'kolejność', blank=True, null=True)
    content = m.TextField(u'treść html', blank=True)

    class Meta:
        verbose_name = u'fragment strony'
        verbose_name_plural = u'fragmenty stron'
        ordering = ['location', 'order']

    def __unicode__(self):
        return self.name[:200]


class PageFragmentAttachment(m.Model):
    owner = m.ForeignKey('PageFragment', verbose_name=u'fragment strony')
    file = m.FileField(u'plik', upload_to='page_fragment')

    class Meta:
        verbose_name = u'załącznik fragmentu strony'
        verbose_name_plural = u'załączniki fragmentów stron'

    def __unicode__(self):
        return self.file.name[:200]
        

class StockIntegration(m.Model):

    class StockProviders:
        WF_MAG = 'wfmag'
        SYMFONIA = 'symfonia'
        TOM_SOFT = 'tomsoft'
        OPTIMA = 'optima'
        CDNXL = 'cdnxl'

    STOCK_INT_CHOICES = (
        (StockProviders.WF_MAG, u'WF Mag'),
        (StockProviders.SYMFONIA, u'Symfonia'),
        (StockProviders.TOM_SOFT, u'Tomsoft'),
        (StockProviders.OPTIMA, u'Optima'),
        (StockProviders.CDNXL, u'CDNXL')
    )

    supplier = m.ForeignKey('Supplier', verbose_name=u'dostawca')
    provider = m.CharField('Oprogramowanie magazynowe', choices=STOCK_INT_CHOICES, max_length=50)
    provider_ver = m.CharField(u'wersja oprogramowania magazynowego', max_length=255)
    integrator_host = m.CharField(u'Host i numer portu integratora', max_length=50,
        help_text=u'Np. localhost:8082')

    class Meta:
        verbose_name = u'integracja z magazynem'
        verbose_name_plural = u'integracje z magazynem'

    def __unicode__(self):
        return u'Integracja z magazynem'

    @staticmethod
    def post_save(sender, instance, **kwargs):
        supplier = instance.supplier
        
        if not supplier.has_stock_integration:
            supplier.has_stock_integration = True
            supplier.save()
    
    @staticmethod
    def post_delete(sender, instance, **kwargs):
        supplier = instance.supplier
        if supplier.has_stock_integration:
            if not supplier.stockintegration_set.all().count():
                supplier.has_stock_integration = False
                supplier.save()

post_save.connect(StockIntegration.post_save, StockIntegration)
post_delete.connect(StockIntegration.post_delete, StockIntegration)

class LogEntry(m.Model):
    class Cat:
        STOCK_SYNC = 'stock'
        PRICE_SYNC = 'price'
        ORDER_SYNC = 'order'
        INV_SYNC = 'inv'
        GENERAL = 'general'

    class Level:
        INFO = 'info'
        WARNING = 'warn'
        ERROR = 'error'

    CATEGORY_CHOICES = (
        (Cat.STOCK_SYNC, u'Aktualizacja stanów magazynowych'),
        (Cat.PRICE_SYNC, u'Aktualizacja oferty handlowej'),
        (Cat.ORDER_SYNC, u'Przesłanie zamówienia'),
        (Cat.INV_SYNC, u'Przesłanie faktury'),
        (Cat.GENERAL, u'ogólne')
    )

    LEVEL_CHOICES = (
        (Level.INFO, u'Informacja'),
        (Level.WARNING, u'Ostrzeżenie'),
        (Level.ERROR, u'Błąd')
    )
    
    CATEGORIES = dict(CATEGORY_CHOICES)
    
    category = m.CharField(u'kategoria', choices=CATEGORY_CHOICES, max_length=50, db_index=True)
    level = m.CharField(u'poziom', choices=LEVEL_CHOICES, max_length=50, db_index=True)
    message = m.TextField(u'treść', blank=True)
    created = m.DateTimeField(u'czas utworzenia')

    class Meta:
        verbose_name = u'dziennik systemowy'
        verbose_name_plural = u'dzienniki systemowe'
        ordering = ['-created']

    def __unicode__(self):
        return u'%s (%s) : %s' % (self.created, self.category, self.message[:50])

    def humanized_category(self):
        '''Human friendly category name.'''
        return dict(LogEntry.CATEGORY_CHOICES).get(self.category, u'Nieznana')

    @classmethod
    def info(cls, msg, cat=Cat.GENERAL):
        cls(category=cat,
            level=cls.Level.INFO,
            message=msg
        ).save()

    @classmethod
    def warn(cls, msg, cat=Cat.GENERAL):
        cls(category=cat,
              level=cls.Level.WARNING,
              message=msg
        ).save()

    @classmethod
    def error(cls, msg, cat=Cat.GENERAL):
        cls(category=cat,
            level=cls.Level.ERROR,
            message=msg
        ).save()
