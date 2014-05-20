# forms.py
# USD ACM
# Laura Londo
# 20 May 2014

'''
Forms are used to gather information from the user that can be used to modify or create 
date in the tables.
'''

import re
from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm
from models import Member, Event, Announcement, TutoringTime, EventComment, AnnouncementComment, CarouselSlide




class RegistrationForm(forms.Form):
    username = forms.CharField(label=u'Username', max_length=30)
    email = forms.EmailField(label=u'Email')
    password1 = forms.CharField(
        label=u'Password',
        widget=forms.PasswordInput()
        )
    password2 = forms.CharField(
        label=u'Password (again)',
        widget=forms.PasswordInput()
        )
    
    def clean_password2(self):
        if 'password1' in self.cleaned_data:
            password1 = self.cleaned_data['password1']
            password2 = self.cleaned_data['password2']
            if password1 == password2:
                return password2
            raise forms.ValidationError(u'Passwords do not match.')

    def clean_username(self):
        username = self.cleaned_data['username']
        if not re.search(r'^\w+$', username):
            raise forms.ValidationError(u'Username can only contain '
                                        'alphanumeric characters and the underscore.')
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(u'Username is already taken.')






# the followinf forms are auto-generated using a model as the template for the
# form fields. fields can be excluded from the form if the user is not respnsible
# for providing input for those fields.


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        exclude = ['user','aboutMe','title']


class TutoringTimeForm(forms.ModelForm):
    class Meta:
        model = TutoringTime
        exclude = ['member']


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        exclude = ['created', 'created_by', 'last_modified', 'last_modified_by']


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        exclude = ['created', 'created_by', 'last_modified', 'last_modified_by']


class EventCommentForm(forms.ModelForm):
    class Meta:
        model = EventComment
        exclude = ['member', 'event', 'date']


class AnnouncementCommentForm(forms.ModelForm):
    class Meta:
        model = AnnouncementComment
        exclude = ['member', 'announcement', 'date']






# custon slide form
class CarouselSlideForm(forms.Form):
    position = forms.IntegerField(
        label = 'Position')
    image = forms.ImageField(
        label = 'Image')
    headline = forms.CharField(
        label = 'Headline')
    description = forms.CharField(
        label = 'Description')
    button_text = forms.CharField(
        label = 'Button Text')
    button_url = forms.URLField(
        label = 'Button URL')
