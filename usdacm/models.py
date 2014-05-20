# models.py
# USD ACM
# Laura Londo
# 20 May 2014


'''
Models describe the structure of the tables in the database. A table represents what 
would be a class in many programming languages where every column in the table is a 
field or attribute of the class and every row is an instance or individual object of 
that class. Every table used in the application's database is defined by a model that
describes all of the different fields of that object as well as their restriction, the 
relationships to other objects, and methods used to manipulate their data.

'''



from django.db import models
from django.contrib.auth.models import User
import json
import datetime
from django.utils import timezone
#import Image

# Create your models here.

# memeber class. used to extend teh default Django user class and provide
# more information to be submitted. each registered user will be linked with
# a member object.
class Member(models.Model):
    user = models.ForeignKey(User,  unique=True)
    firstName = models.CharField(max_length=20)
    lastName = models.CharField(max_length=20)
    major = models.CharField(max_length=40, blank=True) #TODO: different type?
    pic = models.FileField(upload_to='acm/members/pics', blank=True)
    aboutMe = models.CharField(max_length=500, blank=True)
    title = models.CharField(max_length=30, blank=True)
    #access level / permissions
    
    def __unicode__(self):
        return self.user.username


# object for club news and announcement posts
class Announcement(models.Model):
    title = models.CharField(max_length=100)
    text = models.CharField(max_length=500)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(Member, related_name="announcement_created_by")
    last_modified = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(Member, related_name="announcement_last_modified_by")

    def __unicode__(self):
        return self.title


# object for club events or meetings
class Event(models.Model):
    title = models.CharField(max_length=100)
    text = models.CharField(max_length=1000)
    pic = models.ImageField(upload_to='acm/events', blank=True)
    date = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(Member, related_name="event_created_by") #ensures unique foreign key names
    last_modified = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(Member, related_name="event_last_modified_by")
 
    #returns a dictionary of the event details for the js events calendar
    def as_dict(self):
        daate = self.date
        loc = timezone.localtime(daate)
        d =  dict(  title = self.title,
                    id = self.id,
                    pic_url = "",
                    text = self.text,
                    year = self.date.year,
                    month = self.date.month,
                    day = self.date.day,
                    hour = loc.hour,
                    minute = self.date.minute,
                    active = True)
        if self.pic: #if a picture was uploaded, save URL
            d['pic_url'] = self.pic.url
        return d
    

    # a possible option for resizing images on upload, however 
    # an error indicates that a jpeg encoder is missing
    '''def save(self):
        super(Event, self).save() #save everything else as normal?

        if not self.pic:
            return
        
        image = Image.open(self.pic)
        (width, height) = image.size
        
        if (100/width < 100/height):
            scale = 100/height
        else:
            scale = 100/width

        size = (width/scale, height/scale)
        image.resize(size, Image.ANTIALIAS)
        image.save(self.pic.path)'''
        
            
    #string representation
    def __unicode__(self):
        return self.title


# user comments for an event.
class EventComment(models.Model):
    member = models.ForeignKey(Member)
    event = models.ForeignKey(Event)
    text = models.TextField(max_length=1000)
    date = models.DateTimeField()

    def __unicode__(self):
        return "comment: " + self.text 


# user comments for an announcement.
class AnnouncementComment(models.Model):
    member = models.ForeignKey(Member)
    announcement = models.ForeignKey(Announcement)
    text = models.TextField(max_length=1000)
    date = models.DateTimeField()

    def __unicode__(self):
        return "comment: " + self.text


# A tutoring time for the tutoring schedule. members are allowed to create many 
# tutoring times for the hours that they would like to help other students with
# ther computer science problems.
class TutoringTime(models.Model):
    member = models.ForeignKey(Member)
    DAY_CHOICES = (
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday')
        )
    day = models.CharField(choices=DAY_CHOICES, max_length=10) #limited to the provided weekdays
    start = models.TimeField()
    end = models.TimeField()
    note = models.CharField(max_length=150, blank=True)

    def __unicode__(self):
        return "%s - %s: %s %s" % (str(self.start), str(self.end), 
                                   self.member.firstName, self.member.lastName)


# slide for the home page image carousel. Provides an image and optional short title
# and description. also allows the creation of a button to link to another page.
class CarouselSlide(models.Model):
    position = models.IntegerField()
    image = models.ImageField(upload_to='acm/index/carousel')
    headline = models.CharField(max_length=100, blank=True)
    description = models.TextField(max_length = 200, blank=True)
    button_text = models.CharField(max_length=20, blank=True)
    button_url = models.URLField(blank=True)
    
    def __unicode__(self):
        stri = "Carousel Slide " + str(self.position)
        if self.headline:
            stri += " - " + self.headline
        return stri
