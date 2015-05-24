# -*- coding: utf-8 -*-

import re
import types
import decimal as dec
from decimal import Decimal

from django import forms
from django.core import validators
from django.forms.util import flatatt
from django.utils.encoding import smart_unicode
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.utils import formats
from django.db.models.fields import related
from django.contrib.admin import widgets as admin_widgets

from dshop.main import models as m
from dshop import settings

class TreeNodeChoiceField(forms.ModelChoiceField):
    """A ModelChoiceField for tree nodes."""
    def __init__(self, level_indicator=u'---', *args, **kwargs):
        self.level_indicator = level_indicator
        super(TreeNodeChoiceField, self).__init__(*args, **kwargs)

    def label_from_instance(self, obj):
        """
        Creates labels which represent the tree level of each node when
        generating option labels.
        """
        return u'%s %s' % (self.level_indicator * getattr(obj,
                                                  obj._meta.level_attr),
                           smart_unicode(obj))


class StrippedCharField(forms.CharField):
    '''Char field that output trimmed strings.'''
    def __init__(self, *args, **kwargs):
        super(StrippedCharField, self).__init__(*args, **kwargs)
    def clean(self, value):
        if value is None: value = ""
        return super(StrippedCharField, self).clean(value.strip())


# TODO change this to class decorators that will be called before object creation
class StrippedEmailField(forms.EmailField):
    '''Char field that output trimmed strings.'''
    def __init__(self, *args, **kwargs):
        super(StrippedEmailField, self).__init__(*args, **kwargs)
    def clean(self, value):
        if value is None: value = ""
        return super(StrippedEmailField, self).clean(value.strip())


class L10nIntegerField(forms.IntegerField):
    '''Integer field that accept integers written in local flavour (Polish only).'''
    def __init__(self, *args, **kwargs):
        super(L10nIntegerField, self).__init__(*args, **kwargs)
    def clean(self, value):
        if value is None: value = ""
        return super(L10nIntegerField, self).clean(re.sub(r'\s+', '', value))


class L10nDecimalWidget(forms.TextInput):
    def __init__(self, readonly=False, suffix=u'', normalize=True, attrs=None):
        self.readonly = readonly
        self.suffix = suffix
        self.normalize = normalize
        super(L10nDecimalWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        if self.normalize:
            try:
                value = float(Decimal(re.sub(r',', '.', unicode(value))).normalize())
            except: pass
        if value is not None:
            value = re.sub(r'\.', ',', unicode(value))
        if self.readonly:
            return mark_safe(u'<span %s>%s</span> %s' % (flatatt(attrs), value if value is not None else u'', self.suffix))
        else:
            return mark_safe(super(L10nDecimalWidget, self).render(name, value, attrs) + u' ' + self.suffix)
        

class L10nCurrencyWidget(L10nDecimalWidget):
    def __init__(self, readonly=False, attrs=None):
        super(L10nCurrencyWidget, self).__init__(readonly, normalize=False, attrs=attrs)
    
    def render(self, name, value, attrs=None):
        orig = value
        if value != None:
            try:
                value = re.sub(r',', '.', unicode(value))
                value = Decimal(value).quantize(Decimal('0.01'), rounding=dec.ROUND_HALF_UP)
                if value == value.to_integral():
                    value = value.to_integral()
            except:
                value = orig
        return mark_safe(super(L10nCurrencyWidget, self).render(name, value, attrs) + u' zł')


class L10nDecimalField(forms.DecimalField):
    '''Decimal field that accept decimals written in local flavour (Polish only).'''
    widget = L10nDecimalWidget
    def __init__(self, *args, **kwargs):
        readonly = kwargs.pop('readonly', False)
        suffix = kwargs.pop('suffix', u'')
        super(L10nDecimalField, self).__init__(*args, **kwargs)
        self.widget.readonly = readonly
        self.widget.suffix = suffix
    
    def clean(self, value):
        if value is None: value = ""
        return super(L10nDecimalField, self).clean(re.sub(r',', '.', re.sub(r'\s+', '', value)))


class L10nCurrencyField(L10nDecimalField):
    '''Currency field that accept decimals written in local flavour (Polish only).'''
    widget = L10nCurrencyWidget
    def __init__(self, *args, **kwargs):
        super(L10nCurrencyField, self).__init__(*args, **kwargs)


# TODO change this to class decorators that will be called before object creation
class ArticleQuantityField(L10nDecimalField):
    '''Article quantity field. It validates even when invalid number is given, None is then returned.'''
    def __init__(self, *args, **kwargs):
        super(ArticleQuantityField, self).__init__(*args, **kwargs)
    
    def clean(self, value):
        try:
            return super(ArticleQuantityField, self).clean(value)
        except forms.ValidationError:
            return None



class ModelLinkWidget(forms.Widget):
    def __init__(self, obj, attrs=None):
        self.object = obj
        super(ModelLinkWidget, self).__init__(attrs)
        
    def render(self, name, value, attrs=None):
        final_attrs = self.build_attrs(attrs)
        final_attrs['class'] = ' '.join(final_attrs.get('class', u'').split() + ['model-link'])
        if self.object:
            return mark_safe(u'<a target="_blank" %s href="../../../%s/%s/%s/">%s</a>' %
                    (flatatt(final_attrs), self.object._meta.app_label,
                     self.object._meta.object_name.lower(), self.object.pk, self.object))
        else:
            return mark_safe(u'<span %s>nie wybrano</span>' % flatatt(final_attrs))


class ReadOnlyWidget(forms.Widget):
    def __init__(self, attrs=None):
        super(ReadOnlyWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        if value is None:
            value = u''
        final_attrs = self.build_attrs(attrs)
        final_attrs['class'] = ' '.join(final_attrs.get('class', u'').split() + ['readonly'])
        return mark_safe(u'<span %s>%s</span>' % (flatatt(final_attrs), formats.localize_input(value) if value != u'' else u'&nbsp;'))


class CartItemArticleWidget(forms.TextInput):

    def __init__(self, citem=None, attrs=None):
        self.citem = citem
        super(CartItemArticleWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        if value is None: value = u''
        final_attrs = self.build_attrs(attrs)
        
        if self.citem.pk and not self.citem.article_if_published:
            return mark_safe(u'<span %s>%s</span>' % (flatatt(final_attrs), self.citem.name))
        else:
            related_url = '../../../main/shoparticle/?t=id'
            final_attrs['class'] = 'vForeignKeyRawIdAdminField'
            if value: final_attrs['value'] = value

            output = [super(CartItemArticleWidget, self).render(name, value, final_attrs)]
            output.append('<a href="%s" class="related-lookup" id="lookup_id_%s" onclick="return showRelatedObjectLookupPopup(this);"> ' % \
                    (related_url, name))
            output.append('<img src="%simg/admin/selector-search.gif" width="16" height="16" alt="%s" /></a>' % (settings.ADMIN_MEDIA_PREFIX, _('Lookup')))
            
            if value:
                output.append(u'&nbsp;<a href="%s" target="_blank"><strong>%s</strong></a>' % \
                ('../../../main/shoparticle/%s/' % value, m.ShopArticle.objects.get(pk=int(value))))
            return mark_safe(u''.join(output))


def labeled_widget(widget_cls, label='', tag='strong', classes=[], linebreak=False, before=False):
    '''Widget class decorator. Decorated widgets output additional label after or before widget code.'''

    orig_init = widget_cls.__init__
    def init(self, attrs=None):
        self.label = label
        return orig_init(self, attrs)

    orig_render = widget_cls.render
    def render(self, name, value, attrs=None):
        output = orig_render(self, name, value, attrs)
        lbl = u'<%s>%s</%s>' % (tag, self.label, tag)
        if before:
            return mark_safe(lbl + ('<br />' if linebreak else '') + output)
        else:
            return mark_safe(output + ('<br />' if linebreak else '') + lbl)

    widget_cls.__init__ = init
    widget_cls.render = render
    return widget_cls

def wrapped_widget(widget_cls, tag='div', classes=[]):
    '''Widget class decorator. Decorated widgets are wrapped into given HTML tag (div by default).'''

    orig_render = widget_cls.render
    def render(self, name, value, attrs=None):
        output = orig_render(self, name, value, attrs)
        cls = (u' class="%s"' % ' '.join(classes)) if classes else u''
        output = u'<%s%s>%s</%s>' % (tag, cls, output, tag)
        return mark_safe(output)

    widget_cls.render = render
    return widget_cls

class RawIdLinkedWidget(admin_widgets.ForeignKeyRawIdWidget):

    def render(self, name, value, attrs=None):
        res = super(RawIdLinkedWidget, self).render(name, value, attrs)
        if value:
            related_url = '../../../%s/%s/%s/' % (self.rel.to._meta.app_label, self.rel.to._meta.object_name.lower(), value)
            res = re.sub(r'(<strong>.+</strong>)', r'<a href="%s" target="_blank">\1</a>' % related_url, res)
        return mark_safe(res)


class VariantSelect(forms.Select):
    def render(self, name, value, attrs=None, choices=()):
        if value:
            self.choices = m.ArticleVariant.objects.get(article=value)\
                            .owner.sorted_variant_set().values_list('article__id', 'variant')
        return super(VariantSelect, self).render(name, value, attrs, choices)

class ArticleMultiWidget(forms.MultiWidget):
    class Media:
        js  = ('js/admin_form_widgets.js',)
        css = { 'all' : ('css/admin_form_widgets.css',) }
    
    AMWSelect = wrapped_widget(
            labeled_widget(types.ClassType('AMWSelect', (VariantSelect,), {}), u'Wariant:', tag='label', before=True),
            classes=['article_mwidget']
    )

    def __init__(self, attrs=None):
        attrs = attrs or {}
        attrs['class'] = attrs.get('class', '') + ' article_mwidget'
        widgets = (
            admin_widgets.ForeignKeyRawIdWidget(attrs=attrs, rel=related.ManyToOneRel(m.ShopArticle, 'id')),
            ArticleMultiWidget.AMWSelect(attrs=attrs)
        )
        super(ArticleMultiWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value == '':
            value = None
        if value:
            article = m.Article.objects.get(id=int(value))
            if article.used_by_variant():
                return [article.get_shoparticle().id, article.id]
            else:
                return [article.get_shoparticle().id, None]
        else:
            return [None,None]


class ArticleMultiField(forms.MultiValueField):
    widget = ArticleMultiWidget

    def __init__(self, *args, **kwargs):
        fields = (
            forms.ModelChoiceField(queryset=m.ShopArticle.objects.all()),
            forms.ModelChoiceField(queryset=m.Article.objects.all())
        )
        super(ArticleMultiField, self).__init__(fields, *args, **kwargs)
        self.required = False

    def clean(self, value):
        if not value or not value[0]:
            raise forms.ValidationError(self.error_messages['required'])
        return super(ArticleMultiField, self).clean(value)

    def compress(self, data_list):
        if not data_list:
            return None
        if len(data_list) > 1 and data_list[1]:
            return data_list[1]
        else:
            return data_list[0].article