# -*- coding: utf-8 -*-

import hashlib
from datetime import datetime

from django import forms
from django.forms.util import ErrorList

from dshop.main import models as m
from dshop.main import formfields as dforms

class LoginForm(forms.Form):
    username = forms.CharField(label=u'Email', required=False)
    password = forms.CharField(label=u'Hasło', required=False, widget=forms.PasswordInput)
    remember = forms.BooleanField(label=u'Zapamiętaj mnie na tym komputerze', required=False)
    next = forms.CharField(widget=forms.HiddenInput)

    def clean_username(self):
        return self.cleaned_data.get('username', '').strip().lower()

class PasswordRecoverForm(forms.Form):
    email = forms.CharField(label=u'Email', required=False)

    def clean_email(self):
        return self.cleaned_data.get('email', '').strip().lower()

class ChangePasswdForm(forms.Form):
    password = forms.CharField(label=u'Nowe hasło', required=False, widget=forms.PasswordInput)
    password2 = forms.CharField(label=u'Powtórz hasło', required=False, widget=forms.PasswordInput)
    
    def clean(self):
        pwd1 = self.cleaned_data.get('password', '')
        pwd2 = self.cleaned_data.get('password2', '')

        if pwd1 and len(pwd1) < 5:
            raise forms.ValidationError(u'Hasło musi mieć co najmniej 5 znaków.')
        if pwd1 and pwd2:
            if pwd1 != pwd2:
                raise forms.ValidationError(u'Podane hasła nie są identyczne.')
        else:
            raise forms.ValidationError(u'Oba pola są wymagane.')
        return self.cleaned_data


class RegisterForm(forms.Form):
    email = dforms.StrippedEmailField(label=u'Email', help_text=u'Adres będzie Twoim identyfikatorem. \
                                             Na niego również wyślemy email, którym dokonasz aktywacji konta.')
    email2 = dforms.StrippedEmailField(label=u'Powtórz email')
    password = forms.CharField(label=u'Hasło', min_length=4, widget=forms.PasswordInput)
    password2 = forms.CharField(label=u'Powtórz hasło', widget=forms.PasswordInput)
    newsletter = forms.BooleanField(required=False, initial=True,
                                    label=u'Chcę otrzymywać informacje o promocjach i nowościach w sklepie Optionall.pl')

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if m.Client.objects.filter(login=email).count() > 0:
               raise forms.ValidationError(u"Podany adres email jest już zajęty, wybierz inny adres.")
        return email

    def clean_email2(self):
        email = self.cleaned_data['email2'].lower()
        if 'email' in self.cleaned_data and email != self.cleaned_data['email']:
            raise forms.ValidationError(u'Adresy email nie zgadzają się.')
        return email

    def clean_password2(self):
        pwd = self.cleaned_data['password2']
        if 'password' in self.cleaned_data and pwd != self.cleaned_data['password']:
            raise forms.ValidationError(u'Podane hasła nie są identyczne.')
        return pwd

    def createClient(self):
        '''return new client object.'''
        client = m.Client()
        client.login = self.cleaned_data['email']
        client.set_password(self.cleaned_data['password'])
        client.newsletter = self.cleaned_data['newsletter']
        return client


# TODO add client type related fields dynamically in __init__ depending on client type
class ProfileForm(forms.Form):
    firstName = dforms.StrippedCharField()
    lastName = dforms.StrippedCharField()
    companyName = dforms.StrippedCharField(required=False)
    nip = dforms.StrippedCharField(required=False)
    street = dforms.StrippedCharField()
    buildingNo = dforms.StrippedCharField()
    postCode = dforms.StrippedCharField()
    city = dforms.StrippedCharField()
    phone = dforms.StrippedCharField()
    secondPhone = dforms.StrippedCharField(required=False)

    def __init__(self, dict=None, initial=None, type=None, **kwargs):
        client = initial
        init = ProfileForm.client2Initial(client) if client else {}
        self.type = client.type if client else type
        
        super(ProfileForm, self).__init__(dict, initial=init, **kwargs)

    def _require(self, field):
            if not self.cleaned_data.get(field):
                self._errors[field] = ErrorList([u'To pole jest wymagane.'])
                del self.cleaned_data[field]

    @staticmethod
    def client2Initial(client):
        return {
            'firstName' : client.first_name,
            'lastName'  : client.last_name,
            'companyName' : client.company_name,
            'nip' : client.nip,
            'street' : client.street,
            'buildingNo' : client.number,
            'postCode' : client.code,
            'city' : client.town,
            'phone' : client.phone,
            'secondPhone' : client.second_phone,
            'newsletter' : client.newsletter
        }

    def clean(self):
        if self.type == m.Client.Type.COMPANY:
            self._require('companyName')
            self._require('nip')
        return self.cleaned_data

    def updateClient(self, client):
        cleaned_data = self.cleaned_data

        client.type = self.type
        client.first_name = cleaned_data['firstName']
        client.last_name = cleaned_data['lastName']

        if self.type == m.Client.Type.COMPANY:
            client.company_name = cleaned_data['companyName']
            client.nip = cleaned_data['nip']
        
        client.street = cleaned_data['street']
        client.number = cleaned_data['buildingNo']
        client.code = cleaned_data['postCode']
        client.town = cleaned_data['city']
        client.phone = cleaned_data['phone']
        client.second_phone = cleaned_data['secondPhone']
        client.profile_complete = True


class CompleteProfileForm(ProfileForm):
    clientType = forms.ChoiceField(choices=(
                (m.Client.Type.PERSON, u'osoba fizyczna'),
                (m.Client.Type.COMPANY, u'firma')
        ), initial="osoba")
    permission = forms.BooleanField(initial=True)

    def __init__(self, dict=None, **kwargs):
        super(CompleteProfileForm, self).__init__(dict, **kwargs)

    def clean(self):
        self.type = self.cleaned_data['clientType']
        return super(CompleteProfileForm, self).clean()

    def updateClient(self, client):
        super(CompleteProfileForm, self).updateClient(client)
        client.acceptance = True


class MyProfileForm(ProfileForm):
    newsletter = forms.BooleanField(required=False, initial=True,
            label=u'Chcę otrzymywać informacje o promocjach i nowościach w sklepie Optionall.pl')

    def __init__(self, dict=None, initial=None, type=None, **kwargs):
        super(MyProfileForm, self).__init__(dict, initial, type, **kwargs)

    def updateClient(self, client):
        super(MyProfileForm, self).updateClient(client)
        client.newsletter = self.cleaned_data['newsletter']


class ActivateCardForm(forms.Form):
    clientNumber = dforms.L10nIntegerField(label=u"ID Klienta")
    code = dforms.L10nIntegerField(label=u'Kod Aktywacyjny')

    def __init__(self, dict=None, client=None, **kwargs):
        super(ActivateCardForm, self).__init__(dict, **kwargs)
        self.client = client

    def clean(self):
        number = self.cleaned_data.get('clientNumber')
        code = self.cleaned_data.get('code')
        
        if number and code:
            try:
                card = m.ClientCard.objects.get(number=number)
            except m.ClientCard.DoesNotExist:
                raise forms.ValidationError(u"Nieprawidłowy numer klienta lub kod aktywacyjny.")
            if (number < 100248 or number > 100312) and card.activationCode != code:
                raise forms.ValidationError(u"Nieprawidłowy numer klienta lub kod aktywacyjny.")
        return self.cleaned_data


class Add2CartForm(forms.Form):
    article = forms.IntegerField()
    qty = dforms.L10nDecimalField()
    variant = forms.IntegerField(required=False)


class RemoveFromCartForm(forms.Form):
    article = forms.IntegerField()


class RecalcCartForm(forms.Form):
    def __init__(self, cart, *args, **kwargs):
        super(RecalcCartForm, self).__init__(*args, **kwargs)
        for item in cart.item_set.all():
            self.fields['qty-%d' % item.article_id] = dforms.ArticleQuantityField(required=False)


# Remote forms

class CartItemParamForm(forms.Form):
    order_id = forms.IntegerField(widget=forms.HiddenInput, required=False)
    article = forms.IntegerField(widget=forms.HiddenInput)
    param = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows':'10', 'cols':'24'}),
                label=u'Podaj')

class OrderNotesForm(forms.Form):
    id = forms.IntegerField(label=u'', widget=forms.HiddenInput())
    notes = forms.CharField(required=False, widget=forms.Textarea(), label=u'')


class AddOpinionForm(forms.ModelForm):
    id = forms.CharField(required=True, widget=forms.HiddenInput())

    class Meta:
        model = m.Opinion
        exclude = ['created', 'blocked', 'abuse_count']
        widgets = {
            'article' : forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        self.client = kwargs.pop('client', None)
        super(AddOpinionForm, self).__init__(*args, **kwargs)

        ratings = [(str(i),str(i)) for i in range(1, int(m.SystemParam.get('opinions_max_rating')) + 1)]
        ratings.reverse()
        self.fields['rating'] = forms.ChoiceField(label=u'Ocena', choices=[('', '')] + ratings,
            error_messages={'required': u'Podaj ocenę przez zaznaczenie gwiazdek.',
                            'invalid_choice': u'Podaj ocenę przez zaznaczenie gwiazdek.'})
        self.fields['author'].label = u'Imię / nick'
        self.fields['content'].label = u'';

    def clean_id(self):
        id = self.cleaned_data.get('id', u'')
        if id != u'13':
            raise forms.ValidationError('Błąd formularza')
        return id

    def clean(self):
        if m.SystemParam.get('opinions_allow_anonymous') != "1" and not self.client:
            raise forms.ValidationError(u'Aby dodać opinię musisz się zalogować.');
        return self.cleaned_data

    def save(self, commit=True):
        if self.client:
            self.instance.client_login = self.client.login
        super(AddOpinionForm, self).save(commit)
