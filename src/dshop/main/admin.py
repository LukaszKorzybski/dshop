# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.http import HttpResponse
from django.utils import formats
from django.http import HttpResponse
from django.utils import formats
from django import forms
from datetime import datetime

try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local


from dshop import settings
from dshop.main import models as m
from dshop.main import admin_forms
from dshop.main import adapters
from dshop.main.templatetags import utils as filters
from django.contrib.auth import forms as auth_forms
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import models as auth_models
from django.core.exceptions import PermissionDenied

thread_local = local()


def script_view(request, script):
    return HttpResponse(u'<script type="text/javascript">%s;</script>' % script)


def close_related_view(request, tab_name):
    return HttpResponse(u'<script type="text/javascript">opener.closeRelatedWin("%s"); window.close();</script>' % tab_name)


class FilteredChangeList(ChangeList):
    def __init__(self, request, adm, model, filter, *args, **kwargs):
        self.filter = filter
        self.model = model
        self.formset = None
        super(FilteredChangeList, self).__init__(request, model, adm.list_display, adm.list_display_links,
                        adm.list_filter, adm.date_hierarchy, (), adm.list_select_related, adm.list_per_page, adm.list_editable, adm)

    def get_query_set(self):
        return super(FilteredChangeList, self).get_query_set().filter(**self.filter)

    def url_for_result(self, result):
        return "../../%s/%s" % (self.model._meta.module_name, super(FilteredChangeList, self).url_for_result(result))


class DshopAdmin(admin.ModelAdmin):
    default_tab = ''

    class Media:
        css = { 'all' : ('css/admin_forms.css',) }
        js = ('lib/tinymce/tiny_mce.js', 'lib/tinymce/jquery.tinymce.js', 'js/admin_forms.js', 'js/admin-lists.js')

    def handle_return_url(self, request, result, object_id=None):
        if request.method == 'POST' and not request.REQUEST.has_key('_popup') and not request.POST.has_key('_addanother') and not request.POST.has_key('_continue'):
            ret_url = request.REQUEST.get('adm_ret_url', None)
            if ret_url:
                result['Location'] = ret_url
        return result

    def response_change(self, request, obj):
        return_url = request.POST.get('adm_ret_url', '')
        resp = super(DshopAdmin, self).response_change(request, obj)
                
        if return_url and (request.POST.has_key('_addanother') or request.POST.has_key('_saveasnew') or request.POST.has_key('_continue')):
            resp['Location'] += ("&" if '?' in resp['Location'] else "?") + "adm_ret_url=" + return_url

        if request.POST.has_key("_continue") and request.POST.has_key('active_tab'):
                resp['Location'] += ("&" if '?' in resp['Location'] else '?') + "active_tab=" + request.POST['active_tab']
        return resp

    def response_add(self, request, obj, post_url_continue='../%s/'):
        return_url = request.POST.get('adm_ret_url', '')
        resp = super(DshopAdmin, self).response_add(request, obj, post_url_continue)

        if return_url and (request.POST.has_key('_addanother') or request.POST.has_key('_continue')):
            resp['Location'] += ("&" if '?' in resp['Location'] else "?") + "adm_ret_url=" + return_url

        return resp

    def add_view(self, request, form_url='', extra_context=None):
        ectx = extra_context or {}
        ectx['active_tab'] = request.REQUEST.get('active_tab', self.default_tab)
        ectx['adm_ret_url'] = request.REQUEST.get('adm_ret_url', request.GET.get('ref', ''))
        
        result = super(DshopAdmin, self).add_view(request, form_url, ectx)
        return self.handle_return_url(request, result)

    def change_view(self, request, object_id, extra_context=None):
        ectx = extra_context or {}
        ectx['active_tab'] = request.REQUEST.get('active_tab', self.default_tab)
        ectx['adm_ret_url'] = request.REQUEST.get('adm_ret_url', request.GET.get('ref', ''))

        result = super(DshopAdmin, self).change_view(request, object_id, ectx)
        return self.handle_return_url(request, result, object_id)

    def delete_view(self, request, object_id, extra_context=None):
        ectx = extra_context or {}
        ectx['adm_ret_url'] = request.REQUEST.get('adm_ret_url', request.GET.get('ref', ''))
        
        result = super(DshopAdmin, self).delete_view(request, object_id, extra_context)
        return self.handle_return_url(request, result, object_id)

    def changelist_view(self, request, extra_context=None):
        ctx = extra_context or {}
        ctx['opts'] = self.model._meta
        return super(DshopAdmin, self).changelist_view(request, ctx)


class CategoryTreeAdmin(DshopAdmin):
    CAT_TREE_VAR = 'category'

    def changelist_view(self, request, extra_context=None):
        cat_filter = self.CAT_TREE_VAR + '__id__exact'
        ectx = extra_context or {}
        
        if cat_filter in request.GET:
            ectx['current_category'] = m.Category.objects.get(id=int(request.GET[cat_filter]))
        return super(CategoryTreeAdmin, self).changelist_view(request, ectx)


class SPageAttachmentAdmin(admin.ModelAdmin):
    pass

class SPageAttachmentInline(admin.StackedInline):
    model = m.SPageAttachment
    extra = 1

class SPageContentInline(admin.StackedInline):
    model = m.SPageContent
    extra = 1

class StaticPageAdmin(DshopAdmin):
    form = admin_forms.StaticPageForm
    list_display = ('title', 'public', 'l_get_desc_count', 'get_absolute_url', 'preview_link')
    list_filter = ('public', 'tree_id')
    inlines =[SPageContentInline, SPageAttachmentInline]

    def l_get_desc_count(self, inst):
        return inst.get_descendant_count()
    l_get_desc_count.short_description = u'il. podstron'

class NewsAdmin(DshopAdmin):
    form = admin_forms.NewsForm
    list_display = ('title', 'public', 'sticky', 'created')
    list_filter = ('public', 'sticky')
    ordering = ['-created']

class HelpLinkAdmin(DshopAdmin):
    list_display = ['name', 'url']

class AdditionalLinkAdmin(DshopAdmin):
    list_display = ['location', 'order', 'title', 'url']
    list_filter = ('location',)

class SystemParamAdmin(admin.ModelAdmin):
    list_display = ['key', 'value', 'help_text']
    search_fields = ['key']

class MainPageAdAdmin(DshopAdmin):
    list_display = ['name', 'order', 'file', 'target_link']
    
    def target_link(self, inst):
        return u'<a href="%s" target="_blank">%s</a>' % (inst.target, inst.target)
    target_link.allow_tags = True
    target_link.short_description = u'link docelowy'

class MetaInfoAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'content']

class RedirectAdmin(DshopAdmin):
    list_display = ['source', 'dest']



class MetaProducerAdmin(admin.ModelAdmin):
    list_display = ['name', 'prod_ids']

class AddressInline(admin.StackedInline):
    model = m.Address
    form = admin_forms.AddressForm
    extra = 1

    fieldsets = [
        (None, {
            'fields' : ('type', ('first_name', 'last_name'), 'company_name', 'nip', 'code', 'town',
                       ('street', 'number'), ('phone', 'second_phone'), )
        })
    ]

class ClientDiscountInline(admin.TabularInline):
    form = admin_forms.ClientDiscountForm
    model = m.ClientDiscount
    extra = 2

class ClientAdmin(DshopAdmin):
    form = admin_forms.ClientForm
    list_display = ['login', 'client_num', 'first_name', 'last_name', 'company_name',
                    'town', 'active', 'profile_complete']
    list_filter = ['created', 'type', 'active', 'profile_complete', 'newsletter']
    search_fields = ['=r_client_num', '^login', '^first_name', '^last_name', '^company_name']
    date_hierarchy = 'created'
    inlines = [AddressInline]

    fieldsets = [
        ('Podstawowe', {
            'fields' : ('client_num', 'login', 'password1', 'active', 'profile_complete', 'newsletter', 'acceptance',
                        'type', ('first_name', 'last_name'), 'company_name', 'nip', 'code', 'town',
                       ('street', 'number'), ('phone', 'second_phone'), )
        }),
        (u'Inne', {
            'fields' : ('promo_card_active', 'promo_points', 'promo_multiplier',
                        'payment_deadline', 'created', 'last_login', 'activation_code')
        })
    ]

    default_tab = 'profile'

    def save_model(self, request, obj, form, change):
        pwd = form.cleaned_data.get('password1')
        if pwd:
            obj.set_password(pwd)
        obj.save()

class DiscountAdmin(DshopAdmin):
    list_display = ['shoparticle', 'variant_name', 'nature', 'l_net', 'l_gross', 'l_percent',
            'active', 'l_orig_net', 'l_orig_gross', 'cover_all_variants']
    list_filter = ['nature']
    date_hierarchy = 'created'
    search_fields = ['^article__name', '^article__cat_index']
    raw_id_fields = ['article']

    def l_net(self, inst):
        return filters.money(inst.net)
    l_net.short_description = u'netto'

    def l_gross(self, inst):
        return filters.money(inst.gross)
    l_gross.short_description = u'brutto'

    def l_percent(self, inst):
        return filters.number(inst.percent, precision=2)
    l_percent.short_description = u'procent'

    def l_orig_net(self, inst):
        return filters.money(inst.orig_net)
    l_orig_net.short_description = u'netto bazowe'

    def l_orig_gross(self, inst):
        return filters.money(inst.orig_gross)
    l_orig_gross.short_description = u'brutto bazowe'

    def cover_all_variants(self, inst):
        return inst.cover_variants
    cover_all_variants.short_description = u'na wszystkie warianty'
    cover_all_variants.boolean = True

    def variant_name(self, inst):
        if inst.shoparticle().variants:
            return inst.article.get_variant().variant
        else:
            return u''
    variant_name.short_description = u'wariant'

class PromotionAdmin(DiscountAdmin):
    form = admin_forms.PromotionForm
    fields = ['article', 'cover_variants', 'nature', 'net', 'gross', 'price_calc',
              'percent', 'created', 'short_desc', 'vat', 'orig_net', 'orig_gross']

class ClientDiscountAdmin(DiscountAdmin):
    form = admin_forms.ClientDiscountForm
    list_display = ['shoparticle', 'variant_name', 'client', 'nature', 'l_net', 'l_gross',
                    'l_percent', 'active', 'l_orig_net', 'l_orig_gross', 'cover_all_variants']
    search_fields = ['=client__r_client_num', '^client__login', '^article__name', '^article__cat_index']
    raw_id_fields = ['article', 'client']
    fields = ['client', 'article', 'cover_variants', 'nature', 'net', 'gross',
              'price_calc', 'percent', 'created', 'vat', 'orig_net', 'orig_gross']

class ClientCardAdmin(admin.ModelAdmin):
    list_display = ['number', 'activated', 'activation_code']

class ProducerAdmin(admin.ModelAdmin):
    list_display = ['name', 'public', 'toplist', 'article_count', 'articles_link']
    list_filter = ['public', 'toplist', 'exec_time']

    def articles_link(self, inst):
        url = u'/'+settings.ADMIN_PREFIX + u'main/shoparticle/?producer__id__exact=%d' % inst.id
        return u'<a href="%s">produkty</a>' % url
    articles_link.allow_tags = True
    articles_link.short_description = u'produkty'

class PropertyAdmin(DshopAdmin):
    list_display = ['name', 'spec_count']
    search_fields = ['name']


class PropMembershipInline(admin.TabularInline):
    model = m.PropertyMembership
    extra = 3

class SpecificationAdmin(DshopAdmin):
    list_display = ['name', 'properties_count', 'article_count', 'articles_link']
    search_fields = ['name']
    inlines = [PropMembershipInline]

    def articles_link(self, inst):
        url = u'/'+settings.ADMIN_PREFIX + u'main/shoparticle/?specification__id__exact=%d' % inst.id
        return u'<a href="%s">produkty</a>' % url
    articles_link.allow_tags = True
    articles_link.short_description = u'produkty'

class ExecutionTimeAdmin(admin.ModelAdmin):
    form = admin_forms.ExecutionTimeForm
    list_display = ['__unicode__', 'producers_link', 'articles_link']

    def producers_link(self, inst):
        url = u'/'+settings.ADMIN_PREFIX + u'main/producer/?exec_time__id__exact=%d' % inst.id
        return u'<a href="%s">producenci</a>' % url
    producers_link.allow_tags = True
    producers_link.short_description = u'producenci'

    def articles_link(self, inst):
        url = u'/'+settings.ADMIN_PREFIX + u'main/shoparticle/?exec_time__id__exact=%d' % inst.id
        return u'<a href="%s">produkty</a>' % url
    articles_link.allow_tags = True
    articles_link.short_description = u'produkty'

class FileAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'link']
    list_filter = ['type']
    search_fields = ['name']

    def link(self, inst):
        return u'<a href="%s">podgląd</a>' % inst.url
    link.short_description = u"adres URL"
    link.allow_tags = True

class UnitAdmin(DshopAdmin):
    form = admin_forms.UnitForm
    list_display = ['name', 'short', 'l_precision']

    def l_precision(self, inst):
        return filters.number(inst.precision, 3)
    l_precision.short_description = u'precyzja'

class CategoryAdmin(CategoryTreeAdmin):
    CAT_TREE_VAR = 'parent'

    def __call__(self, request, *args, **kwargs):
        thread_local.main_category_admin_request = request
        return super(CategoryAdmin, self).__call__(request, *args, **kwargs)

    form = admin_forms.CategoryForm
    list_display = ['name', 'depth']
    list_filter = ['parent']
    search_fields = ['^name']
    raw_id_fields = ('parent',)

    def depth(self, inst):
        return inst.level
    depth.short_description = u'poziom'
    depth.admin_order_field = 'level'

class ArticleAdmin(DshopAdmin):
    form = admin_forms.ArticleForm
    list_display = ['cat_index', 'name', 'l_net', 'l_gross', 'l_stock_lvl', 'used',
            'used_by_shoparticle', 'used_by_variant']
    list_filter = ['r_used', 'r_used_shoparticle']
    search_fields = ['^cat_index', 'name']

    def l_net(self, inst):
        return filters.money(inst.net)
    l_net.short_description = u'netto'

    def l_gross(self, inst):
        return filters.money(inst.gross)
    l_gross.short_description = u'brutto'

    def l_stock_lvl(self, inst):
        return filters.number(inst.stock_lvl, -4)
    l_stock_lvl.short_description = u'stan na magazynie'

class ArticlePhotoInline(admin.TabularInline):
    model = m.ArticlePhoto
    formset = admin_forms.ArticlePhotoFormSet
    extra = 2

class ArticleAttachmentInline(admin.TabularInline):
    model = m.ArticleAttachment
    extra = 2

class ArticleVariantInline(admin.TabularInline):
    model = m.ArticleVariant
    form = admin_forms.ArticleVariantForm
    formset = admin_forms.ArticleVariantFormSet
    extra = 4
    raw_id_fields = ['article']

class ArticlePropertyInline(admin.TabularInline):
    model = m.ArticleProperty
    form = admin_forms.ArticlePropertyForm
    extra = 5    

class ShopArticleAdmin(CategoryTreeAdmin):
    form = admin_forms.ShopArticleForm
    list_display = ['cat_index', 'name', 'producer', 'l_net', 'l_gross',
                    'public', 'new','stock_level', 'l_specification', 'opinions_summary']
    list_filter = ['category','public', 'new', 'recommended', 'frontpage', 'producer', 'exec_time']
    search_fields = ['^article__cat_index', '^name']
    raw_id_fields = ['article', 'category', 'recc_articles', 'specification']
    inlines = [ArticlePropertyInline, ArticlePhotoInline, ArticleVariantInline, ArticleAttachmentInline]

    fieldsets = [
        ('Podstawowe', {
            'classes' : ('base',),
            'fields' :  ('name', 'art_cat_index', 'art_unit', ('art_vat', 'art_price_calc'),
                        ('art_purchase_net', 'art_purchase_gross'), ('art_net', 'art_gross'),
                         'art_stock_lvl', 'art_supplier_stock_lvl', 'art_weight', 'created', 'spec_changed')
        }),
        ('Kategoryzacja', {
            'classes' : ('categories',),
            'fields' :  ('producer', 'art_supplier', 'category', 'public', ('new', 'recommended',
                        'frontpage'), 'exec_time', 'param')
        }),
        (u'Opis', {
            'fields' : ('short_desc', 'desc')
        }),
        (u'Polecane', {
            'classes' : ('recc',),
            'fields' :  ('recc_articles',)
        }),
        (u'Ustawienia wariantów', {
            'fields' : ('variants','variants_type', 'variants_name', 'main_variant_name',
                        'variants_unit', 'main_variant_qty')
        }),
        (u'Specyfikacja', {
            'fields' : ('specification',)
        })
    ]

    default_tab = 'base'
    
    def has_add_permission(self, request):
        if request.user.get_profile().is_external:
            return False
        else:
            return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        if request.user.get_profile().is_external:
            return False
        else:
            return True

    def queryset(self, request):
        qs = super(ShopArticleAdmin, self).queryset(request)
        supplier = request.user.get_profile().supplier
        if supplier.internal_supplier:
            return qs
        else:
            return qs.filter(article__supplier=supplier)

    def change_view(self, request, object_id, extra_content=None):
        if request.user.get_profile().is_external:
            raise PermissionDenied
        else:
            return super(ShopArticleAdmin, self).change_view(request, object_id, extra_content)
    
    def stock_level(self, inst):
        return filters.number(inst.article.stock_lvl, -3)
    stock_level.short_description = u'stan na mag.'


    def l_net(self, inst):
        return filters.money(inst.net)
    l_net.short_description = u'netto'

    def l_gross(self, inst):
        return filters.money(inst.gross)
    l_gross.short_description = u'brutto'

    def l_specification(self, inst):
        return inst.specification if inst.specification is not None else u''
    l_specification.short_description = u'specyfikacja'

    def opinions_summary(self, inst):
        if inst.r_opinion_count:
            return u'%s / %d opini' % (filters.number(inst.avg_rating, 1), inst.opinion_count)
        else:
            return u''
    opinions_summary.short_description = u'opinie'
    opinions_summary.allow_tags = True
    opinions_summary.admin_order_field = 'r_avg_rating'

class OrderItemInline(admin.TabularInline):
    model = m.OrderItem
    form = admin_forms.OrderItemForm
    formset = admin_forms.OrderItemFormSet
    extra = 3


class OrderAdmin(DshopAdmin):
    form = admin_forms.OrderForm
    list_display = ['number', 'client', 'l_status_info', 'created', 'l_suspended', 'l_execution_date',
                    'payment', 'payment_status_info', 'shipment_ident',  'l_supplier']
    list_filter = ['created', 'status', 'payment', 'payment_status', 'suspended']
    date_hierarchy = 'created'
    search_fields = ['=number', '=client__r_client_num', '^client__login',
            '^client__first_name', '^client__last_name', '^client__company_name']
    raw_id_fields = ['client']
    inlines = [OrderItemInline]
    actions = ['act_send_to_supplier']

    fieldsets = [
        (u'Informacje', {
            'classes' : ('info',),
            'fields'  : ('number', 'status', 'send_status_email', 'send_employee_msg',
                         'employee_msg', 'created', 'exec_time', 'execution_date', 'suspended')
        }),
        (u'Przesyłka', {
            'classes' : ('shipment',),
            'fields'  : ('shipment_ident', 'shipment_sent', 'shipment_weight',
                         'auto_shipper', 'auto_params', 'shipper', 'pkg_type',
                         'net', 'gross', 'discount_net', 'discount_gross')
        }),
        (u'Płatność', {
            'classes' : ('payment',),
            'fields'  : ('payment', 'payment_status', 'payment_trans_num', 'payment_amount', 'payment_deadline')
        }),
        (u'Zamawiający', {
            'classes' : ('client',),
            'fields'  : ('client',)
        }),
        (u'Odbiorca', {
            'classes' : ('shipment_addr',),
            'fields'  : ('shipment_address',)
        }),
        (u'Dokumenty', {
            'classes' : ('docs',),
            'fields'  : ('inv_client', 'inv_perfekt')
        })
    ]
    
    def l_status_info(self, inst):
        human_status = dict(m.Order.STATUS_CHOICES).get(inst.status, 'unknown')

        #if inst.status in m.Order.Status.SET_BEFORE_SEND:
        #    group = u'before-send'
        #elif inst.status in m.Order.Status.SET_SENT:
        #    group = u'sent'
        #elif inst.status in m.Order.Status.SET_FINAL:
        #    group = u'final'
        #else:
        #    group = u''
        
        group = u''
        html = u'%s<em class="status-group hidden">%s</em>' % (human_status, group)
        return html
    l_status_info.short_description = u'status'
    l_status_info.allow_tags = True
      
    def act_send_to_supplier(self, request, queryset):
        '''This action sends order to the external supplier for processing.'''
        orders_sent = []
        if request.user.get_profile().is_external:
            raise PermissionDenied

        for order in queryset.all():
            supplier = order.can_be_sent_to_supplier()
            if supplier:
                order.sent_to_supplier = supplier
                order.save()
                log = m.LogEntry()
                log.category = 'order'
                log.level = 'info'
                log.message = u'Przesłano zamówienie do dostawcy. Dostawca: %s, Zamówienie: %s' % (supplier.name, order.number)
                log.created = datetime.now()
                log.save()
                orders_sent.append(order)

        order_numbers = u' '.join([o.number for o in orders_sent])
        self.message_user(request, u'Wysłano zamówienia nr: %s do zewnętrznych dostawców'
                          % order_numbers)
    act_send_to_supplier.short_description = u'Wyślij zamówienia do dostawcy'


    def queryset(self, request):
        qs = super(OrderAdmin, self).queryset(request)
        supplier = request.user.get_profile().supplier
        if supplier.internal_supplier:
            return qs
        else:
            return qs.filter(sent_to_supplier=supplier)

    def has_add_permission(self, request):
        if request.user.get_profile().is_external:
            return False
        else:
            return True

    def has_delete_permission(self, request, obj=None):
        if request.user.get_profile().is_external:
            return False
        else:
            return True
    
    def l_suspended(self, inst):
        if inst.suspended:
            return u'<span class="warning">tak</span>'
        else:
            return u'nie'
    l_suspended.short_description = 'wstrzymane'
    l_suspended.allow_tags = True
    l_suspended.admin_order_field = 'suspended'
    
    def l_supplier(self, inst):
        suppliers = inst.suppliers()
        if (None not in suppliers and len(suppliers) == 1):
            supplier = suppliers.pop()
        else:
            supplier = None
        
        sent_to_supplier_id = unicode(inst.sent_to_supplier.id) if inst.sent_to_supplier else u''
        html = [
            supplier.name if supplier else u'',
            u'<em class="sent-to-supplier hidden">',
            sent_to_supplier_id,
            u'</em>'
        ]
        return u''.join(html)
    l_supplier.short_description = u'dostawca'
    l_supplier.allow_tags = True
    
    def shipment_ident(self, inst):
        shipment = inst.shipment()
        return shipment.identifier or u''
    shipment_ident.short_description = u'nr przesyłki'

    def payment_status_info(self, inst):
        status = dict(m.Order.PAYMENT_STATUS_CHOICES)[inst.payment_status]

        if inst.payment_status == m.Order.PaymentStatus.CONFIRMED:
            if inst.full_payment_done:
                html = u'<span title="Płatność wykonana w pełnej kwocie." class="ok">%s</span>' % status
            else:
                html = u'<span title="Płatność niepełna!" class="warning">%s</span>' % status
        else:
            html = status

        if inst.payment == m.Order.Payment.ONLINE and inst.payment_status != m.Order.PaymentStatus.NONE:
            html = u' <a target="_blank" title="Przejdź do DotPay.pl" class="changelist-einfo-link"\
                    href="%s">%s</a>' % (adapters.DotPayPayment(inst).statusUrl(), html)
        
        return html
    payment_status_info.short_description = u'status płatności'
    payment_status_info.allow_tags = True
    payment_status_info.admin_order_field = 'payment_status'

    def l_execution_date(self, inst):
        if not inst.execution_date:
            return u''

        if inst.status in m.Order.Status.BEFORE_SEND:
            if inst.execution_today():
                return u'<span class="warning" title="Zamówienie powinno zostać \
                        wysłane dzisiaj.">%s</span>' % formats.localize(inst.execution_date)
            elif inst.execution_passed():
                return u'<span class="fail" title="Przewidywany termin realizacji \
                        minął.">%s</span>' % formats.localize(inst.execution_date)
        return formats.localize(inst.execution_date)
    
    l_execution_date.short_description = u'przew. data realizacji'
    l_execution_date.allow_tags = True

class ArticleParamAdmin(DshopAdmin):
    list_display = ['name']

class FileTypeAdmin(DshopAdmin):
    list_display = ['name', 'icon_img']

    def icon_img(self, inst):
        if inst.icon:
            return u'<img src="%s" style="max-height: 64px" />' % inst.icon.url
        else:
            return u''
    icon_img.short_description = u"ikona"
    icon_img.allow_tags = True

class ShipperPackageThrlInline(admin.TabularInline):
    model = m.ShipperPackageThrl
    form = admin_forms.ShipperPackageThrlForm
    extra = 4

class ShipperPalletThrlInline(admin.TabularInline):
    model = m.ShipperPalletThrl
    form = admin_forms.ShipperPalletThrlForm
    extra = 4

class StockIntegrationInline(admin.TabularInline):
    model = m.StockIntegration
    extra = 1

class ShipperAdmin(DshopAdmin):
    list_display = ['name', 'packages', 'pallets', 'cash_on_delivery']
    form = admin_forms.ShipperForm
    inlines = [ShipperPackageThrlInline, ShipperPalletThrlInline]

class CompanyAdmin(DshopAdmin):
    list_display = ['name']

class OpinionAdmin(DshopAdmin):
    list_display = ['article', 'author', 'created', 'client_login', 'rating', 'snippet', 'abuse_count', 'blocked']
    list_filter = ['created', 'blocked']
    search_fields = ['^client_login', '=article__article__cat_index', '^author']
    raw_id_fields = ['article']

class PageFragmentAttachmentInline(admin.TabularInline):
    model = m.PageFragmentAttachment
    extra = 2

class PageFragmentAdmin(DshopAdmin):
    list_display = ['name', 'location', 'l_order']
    list_filter = ['location']
    inlines = [PageFragmentAttachmentInline]

    def l_order(self, inst):
        return inst.order if inst.order is not None else ''

class SupplierAdmin(DshopAdmin):
    list_display = ['name', 'phone', 'fax', 'email']
    inlines = [StockIntegrationInline]

class LogEntryAdmin(DshopAdmin):
    list_display = ['humanized_category', 'created', 'message']
    list_filter = ['category']

class DshopUserCreateForm(auth_forms.UserCreationForm):
    supplier = forms.ModelChoiceField(queryset=m.Supplier.objects.all(), label=u'Dostawca', empty_label=None)

    def __init__(self, *args, **kwargs):
        super(DshopUserCreateForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        super(DshopUserCreateForm, self).save(False)
        self.save_m2m()
        self.instance.save()
        
        profile = m.UserProfile(supplier=self.cleaned_data['supplier'])
        profile.user = self.instance
        profile.save()
        
        return self.instance

class DshopUserChangeForm(auth_forms.UserChangeForm):
    supplier = forms.ModelChoiceField(queryset=m.Supplier.objects.all(), label=u'Dostawca', empty_label=None)

    def __init__(self, *args, **kwargs):
        super(DshopUserChangeForm, self).__init__(*args, **kwargs)
        try:
            self.initial['supplier'] = self.instance.get_profile().supplier
        except m.UserProfile.DoesNotExist:
            pass

    def save(self, commit=True):
        super(DshopUserChangeForm, self).save(False)
        self.save_m2m()

        try:
            profile = self.instance.get_profile()
            profile.supplier = self.cleaned_data['supplier']
            profile.save()

        except m.UserProfile.DoesNotExist:
            profile = m.UserProfile(supplier=self.cleaned_data['supplier'])
            profile.user = self.instance
            profile.save()
        
        return self.instance

def create_dshop_user_admin():
    class admin(auth_admin.UserAdmin):
        form = DshopUserChangeForm
        add_form = DshopUserCreateForm

    supplier_fset = ('Dostawca', { 'fields': ('supplier', ) })
    fset = [f for f in auth_admin.UserAdmin.fieldsets]
    fset.append(supplier_fset)

    add_fset = [f for f in auth_admin.UserAdmin.add_fieldsets]
    add_fset.append(supplier_fset)

    setattr(admin, 'fieldsets', fset)
    setattr(admin, 'add_fieldsets', add_fset)

    return admin

DshopUserAdmin = create_dshop_user_admin()

admin.site.unregister(auth_models.User)
admin.site.register(auth_models.User, DshopUserAdmin)

admin.site.register(m.StaticPage, StaticPageAdmin)
admin.site.register(m.News, NewsAdmin)
admin.site.register(m.HelpLink, HelpLinkAdmin)
admin.site.register(m.AdditionalLink, AdditionalLinkAdmin)
admin.site.register(m.SystemParam, SystemParamAdmin)
admin.site.register(m.MainPageAd, MainPageAdAdmin)
admin.site.register(m.MetaInfo, MetaInfoAdmin)
admin.site.register(m.Redirect, RedirectAdmin)
admin.site.register(m.Company, CompanyAdmin)

admin.site.register(m.MetaProducer, MetaProducerAdmin)
admin.site.register(m.ClientCard, ClientCardAdmin)
admin.site.register(m.Client, ClientAdmin)
admin.site.register(m.ClientDiscount, ClientDiscountAdmin)
admin.site.register(m.Producer, ProducerAdmin)
admin.site.register(m.Specification, SpecificationAdmin)
admin.site.register(m.Property, PropertyAdmin)
admin.site.register(m.ExecutionTime, ExecutionTimeAdmin)
admin.site.register(m.File, FileAdmin)
admin.site.register(m.Unit, UnitAdmin)
admin.site.register(m.Promotion, PromotionAdmin)
admin.site.register(m.Category, CategoryAdmin)
admin.site.register(m.Article, ArticleAdmin)
admin.site.register(m.ShopArticle, ShopArticleAdmin)
admin.site.register(m.ArticleParam, ArticleParamAdmin)
admin.site.register(m.Order, OrderAdmin)
admin.site.register(m.FileType, FileTypeAdmin)
admin.site.register(m.PageFragment, PageFragmentAdmin)
admin.site.register(m.Shipper, ShipperAdmin)
admin.site.register(m.Supplier, SupplierAdmin)

admin.site.register(m.LogEntry, LogEntryAdmin)

if int(m.SystemParam.get(key='opinions_active')) == 1:
    admin.site.register(m.Opinion, OpinionAdmin)
