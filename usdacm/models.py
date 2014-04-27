from django.db import models
from django.contrib.auth.models import User
import json
# Create your models here.


class Member(models.Model):
    user = models.ForeignKey(User,  unique=True)
    firstName = models.CharField(max_length=20)
    lastName = models.CharField(max_length=20)
    major = models.CharField(max_length=40) #TODO: different type?
    pic = models.FileField(upload_to='acm/members/pics', blank=True)
    aboutMe = models.CharField(max_length=500, blank=True)
    title = models.CharField(max_length=30, blank=True)
    #posts = #all posts made by this member? 
    #access level / permissions
    #projects = models.ManyToManyField(Project, blank=True)
    
    def __unicode__(self):
        return self.user.username


# object for club news and announcement posts
class Announcement(models.Model):
    title = models.CharField(max_length=100)
    text = models.CharField(max_length=500)
    pic = models.FileField(upload_to='acm/announcements', blank=True)
    date = models.DateTimeField(auto_now=True, auto_now_add=True)
    poster = models.ForeignKey(User)

    def __unicode__(self):
        return self.title


# object for club events or meetings
class Event(models.Model):
    title = models.CharField(max_length=100)
    text = models.CharField(max_length=500)
    pic = models.FileField(upload_to='acm/events', blank=True)
    date = models.DateTimeField()
    
    #returns a dictionary of the event details for the js events calendar
    def as_dict(self):
        d =  dict(  title = self.title,
                    pic = "",
                    text = self.text,
                    year = self.date.year,
                    month = self.date.month,
                    day = self.date.day,
                    hour = self.date.hour,
                    minute = self.date.minute,
                    active = True)
        if self.pic: #if a picture was uploaded, save URL
            d[pic_url] = self.pic.url
        return d
            
    #string representation
    def __unicode__(self):
        return self.title



class TutoringTime(models.Model):
    member = models.ForeignKey(Member)
    MON = 0
    TUES = 1
    WED = 2
    THURS = 3
    FRI = 4
    SAT = 5
    SUN = 6
    DAY_CHOICES = (
        (MON, 'Monday'),
        (TUES, 'Tuesday'),
        (WED, 'Wednesday'),
        (THURS, 'Thursday'),
        (FRI, 'Friday')
    )
    day = models.IntegerField(choices=DAY_CHOICES, default=MON)
    #times = models.ManyToManyField(TimeFromTo)
    start = models.TimeField()
    end = models.TimeField()
    note = models.CharField(max_length=150, blank=True)

    def __unicode__(self):
        return "%s - %s: %s %s" % (str(self.start), str(self.end), 
                                   self.member.firstName, self.member.lastName)

