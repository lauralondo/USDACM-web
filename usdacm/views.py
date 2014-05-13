from django.shortcuts import render, render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

import Image
import json
import time
from datetime import date, timedelta, datetime
from calendar import monthrange

from models import Member, Event, Announcement, TutoringTime, Comment, CarouselSlide
from forms import RegistrationForm, MemberForm, TutoringTimeForm, EventForm, CommentForm



# Create your views here.





def register_user(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        form2 = MemberForm(request.POST, request.FILES)
        if form.is_valid() and form2.is_valid():
            User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
                email=form.cleaned_data['email']
                )
            user = authenticate( username=form.cleaned_data['username'],
                                 password=form.cleaned_data['password1'])
            login(request, user)
            member = form2.save(commit=False)
            member.user = user
            member.save()
            return HttpResponseRedirect(reverse('usdacm.views.profile', args=(user.username,)))         
    else:
        form = RegistrationForm()
        form2 = MemberForm()
    return render_to_response('usdacm/register_user.html', 
                              {'form': form, 'form2': form2},
                              RequestContext(request))

def login_user(request):
    logout(request)
    error = None
    username = password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)      
                return HttpResponseRedirect(reverse('usdacm.views.index'))
        else:
            error = "Uhhhh... that's WRONG!!"
    return render_to_response('usdacm/login.html',
                              {'error' : error},
                              context_instance=RequestContext(request))

def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse('usdacm.views.index'))


def profile(request, name):
    usr = User.objects.get(username=name)
    member = Member.objects.get(user=usr)
    return render_to_response('usdacm/profile.html', 
                              {'member': member}, 
                              context_instance=RequestContext(request))

@login_required
def edit_profile(request, userid):    
    if request.user.id != int(userid): #if this isn't the current user's page, redirect to unauthorized
        return render_to_response('project/unauthorized.html', 
                                  context_instance=RequestContext(request))
    return render_to_response('project/edit_profile.html', 
                              {'userid': userid}, 
                              context_instance=RequestContext(request))











def index(request):
    today = date.today()
    events = Event.objects.filter(date__gte=today).order_by('date')[0:3]
    slides = CarouselSlide.objects.order_by('position')
    return render_to_response('usdacm/index.html', 
                              {'events' : events,
                               'slides' : slides },
                              context_instance=RequestContext(request))

def about(request):
    return render_to_response('usdacm/about.html',
                              context_instance=RequestContext(request))

def members(request):
    members = Member.objects.order_by('firstName')
    return render_to_response('usdacm/members.html', 
                              {'members' : members}, 
                              context_instance=RequestContext(request))




# ANNOUNCEMENTS ========================================================
#
def announcements(request):
    announcements = Announcement.objects.order_by('date')
    return render_to_response('usdacm/announcements.html', 
                              {'announcements' : announcements}, 
                              context_instance=RequestContext(request))

def announcement(request, announcementId):
    ann = Announcement.objects.get(id=announcementId)
    #comments =
    return render_to_response('usdacm/announcement.html',
                              {'announcement' : ann,
                               #'comments' : comments,
                               #'commentForm' : commentForm,
                               },
                              context_instance=RequestContext(request))

@login_required
def create_announcement(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request.FILES)
        if form.is_valid():
            #form.pic = form.pic.resize((100,100), Image.ANTIALIAS)
            form.save()
            return HttpResponseRedirect(reverse('usdacm.views.events'))
    else:
        form = EventForm()
                                       
    return render_to_response('usdacm/create_event.html', 
                              {'form' : form},
                              context_instance=RequestContext(request))
    

@login_required
def edit_announcement(request):
    return 0

@login_required
def delete_announcement(request):
    return 0





# EVENTS ===============================================================
#
def events(request):
    today = date.today()     #get today's date
    events = Event.objects.order_by('date').filter(date__gte=today)[0:4]

    return render_to_response('usdacm/events.html', 
                              {'events' : events, 
                               'year' : today.year, 
                               'month' : today.month,
                               },
                              context_instance=RequestContext(request))


def event(request, eventId):
    event = get_object_or_404(Event, pk=eventId)
    modified = False
    if(event.last_modified - event.created > timedelta(minutes=1)):
        modified = True
    
    comments = Comment.objects.filter(event=event).order_by('date')
    commentForm = CommentForm(request.POST)
    if commentForm.is_valid():
        comm = commentForm.save(commit=False)
        comm.member = Member.objects.get(user=request.user)
        comm.event = event
        comm.date = datetime.now()
        comm.save()
        return HttpResponseRedirect(reverse('usdacm.views.event', kwargs={ 'eventId': event.id }))
    else:
        commentForm = CommentForm()

    return render_to_response('usdacm/event.html',
                              {'event' : event,
                               'modified' : modified,
                               'comments' : comments,
                               'commentForm' : commentForm},
                              context_instance=RequestContext(request))


@login_required
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            member = Member.objects.get(user=request.user)
            event.created_by = member
            event.last_modified_by = member
            
            '''
            if hasattr(event, 'pic'):               
                image = Image.open(event.pic)
                (width, height) = image.size
                
                if (100/width < 100/height):
                    scale = 100.0/height
                else:
                    scale = 100.0/width
                    
                size = (int(width/scale), int(height/scale))
                image.resize(size, Image.ANTIALIAS)        # IOError ar /events/create  decoder jpeg not available
                image.save(event.pic.path)
                    
                #event.pic = event.pic.resize((100,100), Image.ANTIALIAS)'''
            event.save()
            return HttpResponseRedirect(reverse('usdacm.views.events'))
    else:
        form = EventForm()
                                       
    return render_to_response('usdacm/create_event.html', 
                              {'form' : form},
                              context_instance=RequestContext(request))

@login_required
def edit_event(request, eventId):
    event = Event.objects.get(id=eventId)
    return render_to_response('usdacm/edit_event.html', 
                              {'event' : event},
                              context_instance=RequestContext(request))

@login_required
def delete_event(request, eventId):
    event = get_object_or_404(Event, pk=eventId).delete()
    return HttpResponseRedirect(reverse('usdacm.views.events'))
    

#retrieves events for the requested month. returns list in a json string
#to be read by the JavaScript Calendar script
def get_month_events(request):
    context = RequestContext(request)
    today = date.today()
    #by default, use today's month and year
    year = today.year   #the year in the current calendar view
    month = today.month #the month in the current calsendar view
    
    #get the passed in year and month from the JavaScript's GET request
    if request.method == 'GET' and len(request.GET) > 0: #if arguments exist,
        year = int(request.GET['newYear'])
        month = int(request.GET['newMonth'])

    #get dates for the current, previous, and next months
    currDate = date(year, month, 1)
    prevDate = currDate-timedelta(1)
    nextDate = date(year, month, monthrange(year,month)[1]) + timedelta(1)

    #number of days in the curent and previous months
    currDays = monthrange(year, month)[1]
    prevDays = prevDate.day

    #day of the week of the first of the month
    weekStart = currDate.weekday()+1
    if(weekStart == 7): weekStart = 0

    #day of the week of the last of the month
    weekEnd = date(year, month, currDays).weekday()+1
    if(weekEnd == 7): weekEnd = 0

    #query events from the database
    prevMonthEvents = Event.objects.filter(date__year=prevDate.year).filter(date__month=prevDate.month)
    monthEvents =     Event.objects.filter(date__year=year).filter(date__month=month)
    nextMonthEvents = Event.objects.filter(date__year=nextDate.year).filter(date__month=nextDate.month)

    dayList = list()
    #get previous month's events
    for day in range(prevDays-weekStart+1, prevDays+1):
        eventList = [obj.as_dict() for obj in prevMonthEvents.filter(date__day=day)]
        dayList.append( dict(day=day, events=eventList, active=-1) )
    #get current month's events
    for day in range(1, currDays+1):
        act = 0
        if(day == today.day  and  month == today.month  and  year == today.year): 
            act = 1
        eventList = [obj.as_dict() for obj in monthEvents.filter(date__day=day)]
        dayList.append( dict(day=day, events=eventList, active=act) )    
    #get next month's events
    for day in range(1, 7-weekEnd):
        eventList = [obj.as_dict() for obj in nextMonthEvents.filter(date__day=day)]
        dayList.append( dict(day=day, events=eventList, active=-1) )

    url = reverse('usdacm.views.event', args=[0])[:-3] #get the url for the event page without id
    package = dict(url=url, dayList=dayList)           #the complete info package to send to JavaScript
    return HttpResponse(json.dumps(package))           #dump package to a json message









# Tutoring --------------------------------------------------------------
#
def tutoring(request):
    return render_to_response('usdacm/tutoring.html', 
                              context_instance=RequestContext(request))


def tutoring_schedule(request):
    days = list()
    ttimes = TutoringTime.objects.filter(day='Monday').order_by('start')
    day = 'Monday'
    days.append({'day':day, 'ttimes':ttimes})

    ttimes = TutoringTime.objects.filter(day='Tuesday').order_by('start')
    day = 'Tuesday'
    days.append({'day':day, 'ttimes':ttimes})

    ttimes = TutoringTime.objects.filter(day='Wednesday').order_by('start')
    day = 'Wednesday'
    days.append({'day':day, 'ttimes':ttimes})

    ttimes = TutoringTime.objects.filter(day='Thursday').order_by('start')
    day = 'Thursday'
    days.append({'day':day, 'ttimes':ttimes})

    ttimes = TutoringTime.objects.filter(day='Friday').order_by('start')
    day = 'Friday'
    days.append({'day':day, 'ttimes':ttimes})

    return render_to_response('usdacm/tutoring_schedule.html', 
                              {'days' : days,},
                              context_instance=RequestContext(request))


@login_required
def tutoring_signup(request):
    if request.method == 'POST':
        form = TutoringTimeForm(request.POST)
        if form.is_valid():
            member = Member.objects.get(user=request.user)
            ttime = form.save(commit=False)
            ttime.member = member
            ttime.save()
            return HttpResponseRedirect(reverse('usdacm.views.tutoring_schedule'))
    else:
        form = TutoringTimeForm()
                                       
    return render_to_response('usdacm/tutoring_signup.html', 
                              {'form' : form},
                              context_instance=RequestContext(request))



@login_required
def tutoring_delete(request, ttimeId):
    ttime= get_object_or_404(TutoringTime, pk=ttimeId).delete()
    return HttpResponseRedirect(reverse('usdacm.views.tutoring_schedule'))
