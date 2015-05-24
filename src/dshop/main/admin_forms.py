# -*- coding: utf-8 -*-

import types
from decimal import Decimal
import datetime as dt

from django import forms
from django.forms.util import ErrorList
from django.forms.models import BaseInlineFormSet
from django.utils.formats import localize, localize_input
from django.contrib import admin
from django.contrib.admin import widgets as admin_widgets

from dshop.main import models as m
from dshop.main import services
from dshop.main import formfields as dfields
from dshop.main.templatetags import utils
from dshop.main.formfields import TreeNodeChoiceField
from dshop.main.templatetags import utils as filters

class DshopForm(forms.ModelForm):
    def check_required(self, field):
        value = self.cleaned_data.get(field, None)
        if  value == None or value == '':
            self._errors[field] = ErrorList([u'To pole jest wymagane'])
            if field in self.cleaned_data:
                del self.cleaned_data[field]

    def localize_field(self, fname):
        '''Set field as localized.'''
        self.fields[fname].localize = True
        self.fields[fname].widget.is_localized = True


class StaticPageForm(forms.ModelForm):
    parent = TreeNodeChoiceField(queryset=m.StaticPage.tree.all(), required=False)

    class Meta:
        model = m.StaticPage

    def clean_public(self):
        spage = self.instance
        public = self.cleaned_data["public"]

        # TODO: add possibility to make recurrent changes of 'public' param to whole subtree
        # by introducing new form field that would control that.
        if spage.pk and not public:
            if True in [sp.public for sp in spage.get_descendants()]:
                raise forms.ValidationError(u"Strona musi być publiczna ponieważ posiada publiczne podstrony.")

        parent = self.cleaned_data.get("parent", None)
        if parent and public:
            if False in [sp.public for sp in spage.get_ancestors()]:
                raise forms.ValidationError(u"Strona nie może być publiczna ponieważ posiada niepublicznych przodków.")
        return public


class CategoryForm(forms.ModelForm):
    class Meta:
        model = m.Category

    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)

        self.modify = True if self.instance.pk else False
        self.parent = None
        
        if self.modify:
            self.parent = self.instance.parent

    def clean_parent(self):
        parent = self.cleaned_data.get('parent')
        if parent and self.instance in parent.get_ancestors():
            raise forms.ValidationError(u'Nie można przenosić kategorii do jej potomka.')
        return parent

    def recalculate_subtree(self):
        '''Recalculate tree related properties for whole subtree (subgroups and articles)'''
        subgroups = self.instance.get_descendants()
        for g in subgroups:
            g.save()

        for g in [self.instance] + list(subgroups):
            for sarticle in g.article_set.all():
                sarticle.save()

    def save(self, commit=True):
        super(CategoryForm, self).save(commit)
        self.instance.save()
        self.save_m2m()

        if self.modify:
            if self.parent != self.instance.parent:
                self.recalculate_subtree()
        
        return self.instance


class UnitForm(forms.ModelForm):
    class Meta:
        model = m.Unit

    precision = dfields.L10nDecimalField(label=u'Precyzja', max_digits=8, decimal_places=4,
            help_text=m.Unit.precision_help)

    def clean_precision(self):
        prec = self.cleaned_data['precision']
        if prec <= 0:
            raise forms.ValidationError(u'Precyzja musi być większa od zera.')
        return prec


class ExecutionTimeForm(forms.ModelForm):
    class Meta:
        model = m.ExecutionTime

    def clean_min(self):
        min = self.cleaned_data['min']
        if min <= 0:
            raise forms.ValidationError(u'Ilość dni musi być większa od zera.')
        return min

    def clean_max(self):
        max = self.cleaned_data['max']
        if max <= 0:
            raise forms.ValidationError(u'Ilość dni musi być większa od zera.')
        return max

    def clean(self):
        min = self.cleaned_data.get('min')
        max = self.cleaned_data.get('max')

        if min and max and min > max:
            raise forms.ValidationError(u'Max musi być większe lub równe min.')
        return super(ExecutionTimeForm, self).clean()


class NewsForm(DshopForm):
    def __init__(self, *args, **kwargs):
        super(NewsForm, self).__init__(*args, **kwargs)
        self.localize_field('created')


class AddressForm(DshopForm):
    class Meta:
        model = m.Address

    def clean(self):
        cd = self.cleaned_data
        type = cd.get('type')
        if type and type == m.BaseAddress.Type.COMPANY:
            self.check_required('company_name')
            self.check_required('nip')

        return cd

class ClientForm(DshopForm):
    class Meta:
        model = m.Client

    client_num = forms.IntegerField(label=u'Numer klienta', required=False)
    activation_code = forms.CharField(label=u'Kod aktywacyjny', required=False)
    login = forms.EmailField(label=u'Login')
    password1 = forms.CharField(label=u'Utwórz nowe hasło', required=False, widget=forms.PasswordInput)
    first_name = forms.CharField(label=u'Imię', required=False)
    last_name = forms.CharField(label=u'Nazwisko', required=False)
    town = forms.CharField(label=u'Miasto', required=False)
    street = forms.CharField(label=u'Ulica', required=False)
    number = forms.CharField(label=u'Nr lokalu', required=False)
    code = forms.CharField(label=u'Kod pocztowy', required=False)
    acceptance = forms.BooleanField(label=m.Client.acceptance_label, required=True)
    profile_complete = forms.BooleanField(label=m.Client.profile_complete_label, required=False, initial=True,
            help_text=m.Client.profile_complete_help)
    promo_multiplier = dfields.L10nDecimalField(label=m.Client.promo_multiplier_label,
            max_digits=6, decimal_places=2, min_value=Decimal('0.01'), initial=Decimal(1),
            help_text=m.Client.promo_multiplier_help)

    def __init__(self, *args, **kwargs):
        super(ClientForm, self).__init__(*args, **kwargs)
        self.localize_field('created')
        self.localize_field('last_login')

    def clean_login(self):
        l = self.cleaned_data['login'].lower()
        obj = m.Client.objects.filter(login=l)
        if len(obj) and self.instance and self.instance.id != obj[0].id:
            raise forms.ValidationError(u'podany login jest już zajęty')
        return l

    def clean_promo_points(self):
        points = self.cleaned_data['promo_points']
        if points < 0:
            raise forms.ValidationError(u'Ilość punktów nie może być mniejsza od zera.')
        return points

    def clean_payment_deadline(self):
        deadline = self.cleaned_data['payment_deadline']
        if deadline < 0:
            raise forms.ValidationError(u'Ilość dni w terminie płatności nie może być mniejsza od zera.')
        return deadline

    def clean_password1(self):
        if not self.instance.pk:
            self.check_required('password1')

        pwd = self.cleaned_data.get('password1')
        if pwd and len(pwd) < 5:
            raise forms.ValidationError(u'Hasło musi zawierać co najmniej 5 znaków.')
        return pwd

    def clean(self):
        cd = self.cleaned_data
        complete = cd.get('profile_complete', False)

        if complete:
            for f in ['first_name', 'last_name', 'town', 'street', 'number', 'code', 'phone']:
                self.check_required(f)

            type = cd.get('type')
            if type and type == m.BaseAddress.Type.COMPANY:
                self.check_required('company_name')
                self.check_required('nip')

        created = cd.get('created')
        last_login = cd.get('last_login')
        if created and last_login:
            if last_login < created:
                self._errors['last_login'] = ErrorList([u'Nie może być wcześniej niż utworzenie konta klienta.'])
                del cd['last_login']

        # prevent some fields from being changed by user
        cd['client_num'] = self.instance.client_num
        cd['activation_code'] = self.instance.activation_code
        return cd


class DiscountForm(DshopForm):
    net = dfields.L10nCurrencyField(label=u'Cena netto', required=False, max_digits=14, decimal_places=2, min_value=0)
    gross = dfields.L10nCurrencyField(label=u'Cena brutto', required=False, max_digits=14, decimal_places=2, min_value=0)
    percent = dfields.L10nDecimalField(label=u'Procent (%)', required=False, max_digits=6, decimal_places=2, min_value=0, max_value=100)
    article = dfields.ArticleMultiField(label=u'Produkt', widget=dfields.ArticleMultiWidget())
    vat = forms.CharField(widget=forms.HiddenInput)
    orig_net = forms.CharField(widget=forms.HiddenInput)
    orig_gross = forms.CharField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(DiscountForm, self).__init__(*args, **kwargs)
        self.localize_field('created')
        
        if self.instance.pk:
            self.initial['vat'] = self.instance.article.vat
            self.initial['orig_net'] = self.instance.net
            self.initial['orig_gross'] = self.instance.gross

    def clean(self):
        nature = self.cleaned_data.get('nature')
        price_calc = self.cleaned_data.get('price_calc')

        if nature and price_calc:
            if nature == m.Discount.Nature.PERCENT:
                self.check_required('percent')
            else:
                if price_calc == m.PriceCalc.NET:
                    self.check_required('net')
                else:
                    self.check_required('gross')
        return self.cleaned_data


class ClientDiscountForm(DiscountForm):
    class Meta:
        model = m.ClientDiscount

    def clean(self):
        client = self.cleaned_data.get('client')
        article = self.cleaned_data.get('article')

        if client and article:
            if m.ClientDiscount.objects.filter(client=client, article=article).exclude(pk=self.instance.id).count():
                raise forms.ValidationError(u'Wybrany klient posiada już rabat na wybrany artykuł.')
        return super(ClientDiscountForm, self).clean()


class PromotionForm(DiscountForm):
    class Meta:
        model = m.Promotion

    def clean_article(self):
        article = self.cleaned_data.get('article')
        if m.Promotion.objects.filter(article=article).exclude(pk=self.instance.id).count():
            raise forms.ValidationError(u'Na wybrany artykuł już istnieje promocja.')
        return article


class ArticleForm(DshopForm):
    class Meta:
        model = m.Article

    vat = dfields.L10nDecimalField(label=u'VAT (%)', max_digits=6, decimal_places=2, min_value=0)
    net = dfields.L10nCurrencyField(label=u'Cena netto', max_digits=14, required=False, decimal_places=2, min_value=0)
    gross = dfields.L10nCurrencyField(label=u'Cena brutto', max_digits=14, required=False, decimal_places=2, min_value=0)
    stock_lvl = dfields.L10nDecimalField(label=u'stan na magazynie', max_digits=14, decimal_places=4, min_value=0)
    weight = dfields.L10nDecimalField(label=u'Waga (kg)', max_digits=14, decimal_places=4, min_value=0)

    def clean_cat_index(self):
        cat_idx = self.cleaned_data['cat_index']
        if m.Article.objects.filter(cat_index=cat_idx).exclude(pk=self.instance.id).count():
            raise forms.ValidationError(u'Produkt o podanym numerze już istnieje, proszę podać inny numer katalogowy.')
        return cat_idx

    def clean(self):
        price_calc = self.cleaned_data.get('price_calc')
        if price_calc:
            if price_calc == m.PriceCalc.NET:
                self.check_required('net')
            else:
                self.check_required('gross')
        return self.cleaned_data


class ArticleVariantForm(DshopForm):
    class Meta:
        model = m.ArticleVariant
        fields = ['variant','qty', 'art_cat_index', 'art_net', 'art_gross', 'art_price_calc',
                  'art_stock_lvl', 'art_weight']

    qty = dfields.L10nDecimalField(label=m.ArticleVariant.qty_label,
            required=False, max_digits=14, decimal_places=4, min_value=Decimal('0.0001'))

    # Article fields
    art_cat_index = forms.CharField(label=u'Numer katalogowy')
    art_purchase_net = dfields.L10nCurrencyField(label=u'Cena zakupu netto', required=False, max_digits=14, decimal_places=2, min_value=Decimal(0))
    art_purchase_gross = dfields.L10nCurrencyField(label=u'Cena zakupu brutto', required=False, max_digits=14, decimal_places=2, min_value=Decimal(0))
    art_net = dfields.L10nCurrencyField(label=u'Cena netto', required=False, max_digits=14, decimal_places=2, min_value=Decimal(0))
    art_gross = dfields.L10nCurrencyField(label=u'Cena brutto', required=False, max_digits=14, decimal_places=2, min_value=Decimal(0))
    art_price_calc = forms.ChoiceField(label=u'Obliczaj na podst. ceny', choices=m.PRICE_CALC_CHOICES, initial=m.PriceCalc.NET)
    art_stock_lvl = forms.DecimalField(label=u'Stan na magazynie', max_digits=14,
            decimal_places=4, min_value=Decimal(0), initial=localize_input(Decimal('0.0')), localize=True)
    art_weight = forms.DecimalField(label=u'Waga (kg)', max_digits=14, decimal_places=4, min_value=Decimal(0), localize=True)

    def __init__(self, *args, **kwargs):
        super(ArticleVariantForm, self).__init__(*args, **kwargs)
        self.modification = True if self.instance.pk else False

        # copy article field values
        if self.modification:
            article = self.instance.article
            for name, field in self.fields.iteritems():
                if name.startswith('art_'):
                    self.initial[name] = getattr(article, name[4:])

    def clean_art_cat_index(self):
        cat_idx = self.cleaned_data['art_cat_index']
        qs = m.Article.objects.filter(cat_index=cat_idx)
        if self.instance.pk: qs = qs.exclude(pk=self.instance.article.id)

        if qs.count():
            raise forms.ValidationError(u'Produkt lub wariant o podanym numerze już istnieje, proszę podać inny numer katalogowy.')
        return cat_idx

    def clean(self):
        price_calc = self.cleaned_data.get('art_price_calc')
        if price_calc:
            if price_calc == m.PriceCalc.NET:
                self.check_required('art_net')
            else:
                self.check_required('art_gross')

        return super(ArticleVariantForm, self).clean()

    def save(self, commit=True):
        super(ArticleVariantForm, self).save(False)
        cd = self.cleaned_data

        # create or update article object
        if self.modification:
            article = self.instance.article
        else:
            article = m.Article()

        article.name = u'%s - %s' % (self.instance.name, self.instance.variant)

        article.supplier = self.instance.owner.supplier
        article.unit = self.instance.owner.unit
        article.vat = self.instance.owner.vat
        for name, field in self.fields.iteritems():
            if name.startswith('art_'):
                setattr(article, name[4:], cd.get(name))

        article.save()
        if not self.modification:
            self.instance.article = article

        self.instance.save()
        self.save_m2m()
        return self.instance



class ArticleVariantFormSet(BaseInlineFormSet):
    def get_queryset(self):
        if not hasattr(self, '_queryset'):
            qs = super(ArticleVariantFormSet, self).get_queryset().filter(main=False)
            self._queryset = qs
        return self._queryset

    def save_existing(self, form, instance, commit=True):
        # Save variants only when they are turned on, because otherwise they are deleted
        # by ShopArticle's save method before we get here.
        if self.instance.variants:
            super(ArticleVariantFormSet, self).save_existing(form, instance, commit)

    def clean(self):
        super(ArticleVariantFormSet, self).clean()
        
        if any(self.errors):
            return

        if self.instance.variants:
            for form in self.forms:
                article = form.cleaned_data.get('article')
                if article and article == self.instance.article:
                    raise forms.ValidationError(u'Wybrany produkt magazynowy jest używany przez wariant główny.')
        

class ArticlePhotoFormSet(BaseInlineFormSet):
    def clean(self):
        super(ArticlePhotoFormSet, self).clean()
        
        if any(self.errors):
            return

        main_cnt, form_cnt = 0, 0
        for form in self.forms:
            if form.cleaned_data:
                form_cnt += 1
                main = form.cleaned_data.get('main')
                if main:
                    main_cnt += 1

        if form_cnt > 0 and main_cnt > 1:
            raise forms.ValidationError(u'Najwyżej jedno zdjęcie może być ustawione jako główne.')

    def save(self, commit=True):
        saved_photos = super(ArticlePhotoFormSet, self).save(commit)
        
        if saved_photos or self.deleted_objects:
            print "photos changed!"
            all_photos = self.instance.photo_set.all()
            main_photo = reduce(lambda x,y: x if x.main == True else y, all_photos, m.ArticlePhoto(main=False))

            if all_photos and not main_photo.main:
                main_photo = list(all_photos)[-1]
                main_photo.main = True
                main_photo.save()

            if main_photo.main:
                self.instance.r_main_photo = main_photo
            else:
                self.instance.r_main_photo = None
            self.instance.save()

        return saved_photos

class ShopArticleForm(DshopForm):
    class Meta:
        model = m.ShopArticle

    main_variant_qty = dfields.L10nDecimalField(label=m.ShopArticle.main_variant_qty_label,
            required=False, max_digits=14, decimal_places=4, min_value=Decimal('0.0001'))

    # Article fields
    art_cat_index = forms.CharField(label=u'Numer katalogowy')
    art_supplier = forms.ModelChoiceField(label=u'Dostawca', required=False, queryset=m.Supplier.objects.all())
    art_unit = forms.ModelChoiceField(label=u'Jednostka', queryset=m.Unit.objects.all())
    art_vat = dfields.L10nDecimalField(label=u'VAT (%)', max_digits=6, decimal_places=2, min_value=0)
    art_purchase_net = dfields.L10nCurrencyField(label=u'Cena zakupu netto', required=False, max_digits=14, decimal_places=2, min_value=Decimal(0))
    art_purchase_gross = dfields.L10nCurrencyField(label=u'Cena zakupu brutto', required=False, max_digits=14, decimal_places=2, min_value=Decimal(0))
    art_net = dfields.L10nCurrencyField(label=u'Cena netto', required=False, max_digits=14, decimal_places=2, min_value=Decimal(0))
    art_gross = dfields.L10nCurrencyField(label=u'Cena brutto', required=False, max_digits=14, decimal_places=2, min_value=Decimal(0))
    art_price_calc = forms.ChoiceField(label=u'Obliczaj na podst. ceny', choices=m.PRICE_CALC_CHOICES, initial=m.PriceCalc.NET)
    art_stock_lvl = forms.DecimalField(label=u'Stan na magazynie', max_digits=14,
            decimal_places=4, min_value=Decimal(0), initial=localize_input(Decimal('0.0')), localize=True)
    art_supplier_stock_lvl = forms.DecimalField(label=u'Stan na magazynie dostawcy', max_digits=14,
            decimal_places=4, min_value=Decimal(0), initial=localize_input(Decimal('0.0')), localize=True)
    art_weight = forms.DecimalField(label=u'Waga (kg)', max_digits=14, decimal_places=4, min_value=Decimal(0), localize=True)

    # helper fields
    spec_changed = forms.BooleanField(label=u'', initial=False, required=False, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(ShopArticleForm, self).__init__(*args, **kwargs)
        self.modification = True if self.instance.pk else False

        # copy article field values
        if self.modification:
            article = self.instance.article
            for name, field in self.fields.iteritems():
                if name == "art_supplier":
                    self.initial['art_supplier'] = article.supplier.id if article.supplier else None
                elif name == "art_unit":
                    self.initial['art_unit'] = article.unit.id
                elif name.startswith('art_'):
                    self.initial[name] = getattr(article, name[4:])
        
        self.localize_field('created')
        self.fields['art_supplier'].widget = admin_widgets.RelatedFieldWidgetWrapper(
                self.fields['art_supplier'].widget, m.Article.supplier.field.rel, admin.site)
        self.fields['art_unit'].widget = admin_widgets.RelatedFieldWidgetWrapper(
                self.fields['art_unit'].widget, m.Article.unit.field.rel, admin.site)
    
    def clean_art_cat_index(self):
        cat_idx = self.cleaned_data['art_cat_index']
        qs = m.Article.objects.filter(cat_index=cat_idx)
        if self.instance.pk: qs = qs.exclude(pk=self.instance.article.id)

        if qs.count():
            raise forms.ValidationError(u'Produkt o podanym numerze już istnieje, proszę podać inny numer katalogowy.')
        return cat_idx

    def clean(self):
        price_calc = self.cleaned_data.get('art_price_calc')
        variants = self.cleaned_data.get('variants')
        variants_type = self.cleaned_data.get('variants_type')

        if price_calc:
            if price_calc == m.PriceCalc.NET:
                self.check_required('art_net')
            else:
                self.check_required('art_gross')
        
        if variants:
            map(self.check_required, ['variants_type', 'variants_name', 'main_variant_name'])
            if variants_type == m.ShopArticle.VariantsType.QUANTITY:
                map(self.check_required, ['variants_unit', 'main_variant_qty'])
            else:
                self.cleaned_data['variants_unit'] = None
                self.cleaned_data['main_variant_qty'] = None
        else:
            self.cleaned_data['variants_type'] = ''
            self.cleaned_data['variants_name'] = ''
            self.cleaned_data['main_variant_name'] = ''
            self.cleaned_data['variants_unit'] = None
            self.cleaned_data['main_variant_qty'] = None

        return super(ShopArticleForm, self).clean()
    
    def save(self, commit=True):
        super(ShopArticleForm, self).save(False)
        cd = self.cleaned_data

        # create or update article instance
        if self.modification:
            article = self.instance.article
        else:
            article = m.Article()

        article.name = self.instance.name
        if self.instance.variants:
             article.name += u' - %s' % self.instance.main_variant_name

        for name, field in self.fields.iteritems():
            if name.startswith('art_'):
                setattr(article, name[4:], cd.get(name))
        
        article.save()
        if not self.modification:
            self.instance.article = article

        self.instance.save()
        self.save_m2m()
        return self.instance


class ArticlePropertyForm(DshopForm):
    class Meta:
        model = m.ArticleProperty
    
    property_name = forms.CharField(label=u'', widget=forms.HiddenInput, required=False)
    property = forms.CharField(label=m.ArticleProperty.property_label, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(ArticlePropertyForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['property_name'].initial = self.instance.name()

    def clean_property(self):
        try:
            prop = m.PropertyMembership.objects.get(pk=int(self.cleaned_data['property']))
        except:
            raise forms.ValidationError(u'Wybrana własność nie istnieje. Możliwe, że została wcześniej usunięta.')
        return prop


class ShipperForm(DshopForm):
    class Meta:
        model = m.ArticleProperty

    vat = dfields.L10nDecimalField(label=u'VAT (%)', max_digits=6, decimal_places=2, min_value=0)
    package_wrapping_weight = dfields.L10nDecimalField(label=u'waga opakowania paczki (kg)',
                max_digits=8, decimal_places=4, required=False, min_value=0)
    pallet_capacity = dfields.L10nDecimalField(label=u'ładowność palety (kg)',
                max_digits=8, decimal_places=2, required=False, min_value=Decimal('0.01'))
    cash_on_delivery_net = dfields.L10nCurrencyField(label=u'Opłata za płatność przy odbiorze (netto)',
                max_digits=14, decimal_places=2, required=False, min_value=0)

    def clean(self):
        packages = self.cleaned_data.get('packages')
        pallets = self.cleaned_data.get('pallets')
        cash_on_delivery = self.cleaned_data.get('cash_on_delivery')

        if not (packages or pallets):
            raise forms.ValidationError(u'Spedytor musi obsługiwać paczki lub palety.')

        if packages:
            self.check_required('package_wrapping_weight')
        if pallets:
            self.check_required('pallet_capacity')
        if cash_on_delivery:
            self.check_required('cash_on_delivery_net')

        return super(ShipperForm, self).clean()


class ShipperThrlForm(DshopForm):
    max_weight = dfields.L10nDecimalField(label=u'maks. waga (kg)', max_digits=8, decimal_places=2)
    net = dfields.L10nCurrencyField(label=u'cena netto', max_digits=14, required=False, decimal_places=2, min_value=Decimal(0))
    gross = dfields.L10nCurrencyField(label=u'cena brutto', max_digits=14, required=False, decimal_places=2, min_value=Decimal(0))

    def clean(self):
        price_calc = self.cleaned_data.get('price_calc')
        if price_calc:
            if price_calc == m.PriceCalc.NET:
                self.check_required('net')
            else:
                self.check_required('gross')
        
        return super(ShipperThrlForm, self).clean()


class ShipperPackageThrlForm(ShipperThrlForm):
    class Meta:
        model = m.ShipperPackageThrl


class ShipperPalletThrlForm(ShipperThrlForm):
    class Meta:
        model = m.ShipperPalletThrl


class OrderForm(DshopForm):
    class Meta:
        model = m.Order

    send_status_email = forms.BooleanField(label=u'Wyślij email z informacją o zmianie statusu', required=False, initial=False)
    send_employee_msg = forms.BooleanField(label=u'Wyślij dodatkową wiadomość do klienta', required=False,
            help_text=u'Wiadomość zostanie wysłana w momencie zapisania zmian w zamówieniu.')
    employee_msg = forms.CharField(label=u'Wiadomość', required=False, widget=forms.Textarea())
    payment_amount = dfields.L10nCurrencyField(label=u'Kwota płatności', required=False, max_digits=14, decimal_places=2, min_value=Decimal(0))
    exec_time = forms.CharField(label=u'Estymowany czas realizacji', required=False, widget=dfields.ReadOnlyWidget())

    # shipment related fields
    shipment_address = forms.CharField(label=u'Odbiorca', required=False, widget=dfields.ReadOnlyWidget())
    shipment_ident = forms.CharField(label=u'numer przewozowy', required=False)
    shipment_weight = dfields.L10nDecimalField(label=u'waga', required=False, readonly=True, suffix=u'kg')
    auto_shipper = forms.BooleanField(label=u'Automatyczny wybór spedytora', required=False, initial=True)
    auto_params = forms.BooleanField(label=u'Automatyczne parametry przesyłki', required=False, initial=True)
    shipper = forms.ModelChoiceField(label=u'Spedytor', required=False, queryset=m.Shipper.objects.all())
    pkg_type = forms.ChoiceField(label=u'Rodzaj pakowania', required=False, choices=m.Shipment.PKG_TYPE_CHOICES)
    net = dfields.L10nCurrencyField(label=u'Cena netto', required=False, max_digits=14, decimal_places=2, min_value=Decimal(0))
    gross = dfields.L10nCurrencyField(label=u'Cena brutto', required=False, max_digits=14, decimal_places=2, min_value=Decimal(0))
    discount_net = dfields.L10nCurrencyField(label=u'Cena netto po obniżce', required=False, max_digits=14, decimal_places=2, min_value=Decimal(0))
    discount_gross = dfields.L10nCurrencyField(label=u'Cena brutto po obniżce', required=False, max_digits=14, decimal_places=2, min_value=Decimal(0))
    shipment_sent = forms.CharField(label=u'Wysłana', required=False, localize=True, widget=dfields.ReadOnlyWidget())
    
    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial', {})
        instance = kwargs.get('instance', None)

        self.orig_status = None
        self.modification = True if instance else False

        initial['shipment_address'] = u''
        if self.modification:
            self.orig_status = instance.status
            shipment = instance.shipment()

            initial['exec_time'] = unicode(instance.exec_time())
            initial['shipment_ident'] = shipment.identifier
            initial['shipment_weight'] = instance.weight()
            initial['auto_shipper'] = shipment.auto_shipper
            initial['auto_params'] = shipment.auto_params
            initial['shipper'] = m.Shipper.objects.get(name=shipment.shipper_name).id
            initial['pkg_type'] = shipment.pkg_type
            initial['net'] = shipment.net
            initial['gross'] = shipment.gross
            initial['discount_net'] = shipment.discount_net
            initial['discount_gross'] = shipment.discount_gross
            if shipment.sent:
                initial['shipment_sent'] = shipment.sent
            kwargs['initial'] = initial

        super(OrderForm, self).__init__(*args, **kwargs)
        
        self.fields['number'].widget = dfields.ReadOnlyWidget()
        self.localize_field('created')
        self.localize_field('execution_date')
        self.localize_field('payment_deadline')

        if self.modification:
            self.fields['client'].widget = dfields.ModelLinkWidget(instance.client)
        else:
            self.fields['client'].required = True

    def clean_status(self):
        status = self.cleaned_data.get('status')

        if self.instance.status == status:
            if status in ['RJ', 'CA', 'CL', 'RT']:
                raise forms.ValidationError(u'Zamówienie ma status końcowy (jest zamknięte), aby móc je modyfikować zmień status zamówienia.')

        if self.modification and self.orig_status in ['NE', 'AC', 'RE'] and status == 'CL':
            raise forms.ValidationError(u'Najpierw zmień status na "wysłane", dopiero wtedy możesz zamknąć zamówienie.')

        return status
    
    def clean(self):
        status = self.cleaned_data.get('status')
        suspended = self.cleaned_data.get('suspended')
        
        if suspended:
            if self.instance.status != status:
                if status not in ['NE', 'AC', 'RE']:
                    raise forms.ValidationError(u'Nie można zmienić statusu ponieważ zamówienie jest wstrzymane.')
            else:
                if status not in ['NE', 'AC', 'RE']:
                    raise forms.ValidationError(u'Aby wstrzymać zamówienie musi ono mieć status nowe,  w realizacji lub gotowe do wysyłki.')

        # prevent these fields from user change
        if self.modification:
            self.cleaned_data['client'] = self.instance.client
            self.cleaned_data['number'] = self.instance.number

        # payment deadline
        client = self.cleaned_data['client']
        payment = self.cleaned_data.get('payment')
        payment_deadline = self.cleaned_data.get('payment_deadline')
        if client and payment == m.Order.Payment.DELAYED:
            if not payment_deadline:
                self.cleaned_data['payment_deadline'] = dt.datetime.now() + dt.timedelta(days=client.payment_deadline)
        elif payment != m.Order.Payment.DELAYED:
            self.cleaned_data['payment_deadline'] = None

        # shipment
        auto_shipper = self.cleaned_data.get('auto_shipper')
        auto_params = self.cleaned_data.get('auto_params')
        if not auto_shipper:
            self.check_required('shipper')
            if not auto_params:
                fields = ['pkg_type', 'net', 'gross', 'discount_net', 'discount_gross']
                for f in fields:
                    self.check_required(f)

        return self.cleaned_data

    def save(self, commit=True):
        if self.modification and self.instance:
            orig = m.Order.objects.get(id=self.instance.id)
        else:
            orig = None
        
        super(OrderForm, self).save(False)
        cd = self.cleaned_data

        if not self.modification:
            self.instance = m.Order.create_submitted(cd['client'])

        # Status
        if self.instance.status == 'SE':
            shipment = self.instance.send()
        else:
            shipment = self.instance.shipment()

        # Shipment
        shipment.identifier = cd['shipment_ident']
        shipment.auto_shipper = cd['auto_shipper']
        
        if not shipment.auto_shipper:
            shipment.shipper_name = cd['shipper'].name
            shipment.auto_params = cd['auto_params']
            
            if not shipment.auto_params:
                shipment.pkg_type = cd['pkg_type']
                shipment.net = cd['net']
                shipment.gross = cd['gross']
                shipment.discount_net = cd['discount_net']
                shipment.discount_gross = cd['discount_gross']
        m.Shipper.assign_to(shipment)

        # Promo points
        client = self.instance.client
        if self.instance.status == 'CL' and client.promo_card_active:
            client.promo_points += self.instance.promo_points()
            client.save()

        shipment.save()
        self.instance.save()
        self.save_m2m()

        # After save stuff
        if cd.get('send_status_email', False):
            services.send_status_change_email(self.instance)
        if cd['send_employee_msg']:
            services.send_employee_msg(self.instance, cd['employee_msg'])

        if self.modification and self.orig_status != 'CL' and self.instance.status == 'CL':
            m.Opinion.post_order_close(self.instance) # TODO here is good example for need of custom events, it would decouple code
        
        if self.modification:
            client = self.instance.client
            if not client.stock_id:
                from dshop import wfmag
                conn = wfmag.engine.connect()
                client.stock_id = wfmag.insert_or_update_client(client, conn)
                client.save()
                conn.close()
        
        if self.modification and orig:
            supplier = self.instance.sent_to_supplier
            if supplier and self.instance.inv_client != '' and orig.inv_client != self.instance.inv_client:
                log = m.LogEntry()
                log.category = 'inv'
                log.level = 'info'
                log.message = u'Przesłano fakturę do dostawcy. Dostawca: %s, Zamówienie: %s' % (supplier.name, self.instance.number)
                log.created = dt.datetime.now()
                log.save()
        
        return self.instance


class OrderItemForm(DshopForm):
    class Meta:
        model = m.OrderItem
        fields = ['article', 'param_value', 'orig_price', 'discount_price_calc',
                  'discount_net', 'discount_gross', 'qty', 'sum_discount', 'total_weight', 'stock_level']
        widgets = {
            'param_value' : dfields.labeled_widget(
                        types.ClassType('LabeledTextarea', (forms.Textarea,), {}), '', linebreak=True)(attrs={'class':'hidden'})
        }
    
    article = dfields.ArticleMultiField(label=u'Produkt', widget=dfields.ArticleMultiWidget())
    qty = dfields.L10nDecimalField(label=u'ilość', required=False, max_digits=10, decimal_places=4, min_value=Decimal(0))
    discount_price_calc = forms.ChoiceField(label=u'Obliczaj na podst.', choices=m.PRICE_CALC_CHOICES, initial=m.PriceCalc.NET)
    discount_net = dfields.L10nCurrencyField(label=u'netto po obniżce', required=False, max_digits=14, decimal_places=2, min_value=Decimal(0))
    discount_gross = dfields.L10nCurrencyField(label=u'brutto po obniżce', required=False, max_digits=14, decimal_places=2, min_value=Decimal(0))
    orig_price = forms.CharField(label=u'cena', required=False, widget=dfields.ReadOnlyWidget())
    sum_discount = forms.CharField(label=u'suma po obniżce', required=False, widget=dfields.ReadOnlyWidget())
    stock_level = forms.CharField(label=u'stan', required=False, widget=dfields.ReadOnlyWidget())
    total_weight = forms.CharField(label=u'waga', required=False, widget=dfields.L10nDecimalWidget(readonly=True))

    def __init__(self, *args, **kwargs):
        super(OrderItemForm, self).__init__(*args, **kwargs)
        citem = self.instance
        
        if citem.pk:
            self.initial['article'] = citem.article_id if citem.article_if_published else None
            self.initial['orig_price'] = self.render_orig_price(citem)
            self.initial['sum_discount'] =  self.render_sum_discount(citem)
            self.initial['stock_level'] = filters.number(citem.article.stock_lvl, -4)
            self.initial['total_weight'] = citem.total_weight
            
            if not citem.article_if_published:
                self.fields['article'].required=False
            
            if citem.param:
                self.fields['param_value'].widget.attrs['class'] = ''
                self.fields['param_value'].widget.label = citem.param_name

    def render_orig_price(self, citem):
        tmpl = u'<strong>%s</strong> / <span>%s</span> <span class="hidden vat">%s</span> <span class="hidden weight">%s</span>'
        return tmpl % (utils.money(citem.orig_gross), utils.money(citem.orig_net), utils.number(citem.vat), utils.number(citem.weight))

    def render_sum_discount(self, citem):
        tmpl = u'<strong>%s</strong> / <span>%s</span>'
        return tmpl % (utils.money(citem.sum_discount_gross) ,utils.money(citem.sum_discount_net))

    def clean_qty(self):
        return self.cleaned_data.get('qty', Decimal(1))

    def clean(self):
        # change prevent
        self.cleaned_data['weight'] = self.instance.weight

        # price calc
        if self.instance.pk:
            dis_price_calc = self.cleaned_data.get('discount_price_calc')
            if dis_price_calc:
                if dis_price_calc == m.PriceCalc.NET:
                    self.check_required('discount_net')
                else:
                    self.check_required('discount_gross')

        return self.cleaned_data

    def save(self, commit=True):
        article_id = self.cleaned_data.get('article').id
        citem = self.instance

        #if not citem.pk or citem.article_if_published:
        if article_id and citem.article_id != article_id:
            citem.set_abstr_article(m.Article.objects.get(id=article_id).get_abstr_article())
        
        self.instance.set_qty(self.cleaned_data['qty'])
        return super(OrderItemForm, self).save(commit)


class OrderItemFormSet(BaseInlineFormSet):
    pass
            
