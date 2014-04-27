from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import json
import time
from datetime import date, timedelta
from calendar import monthrange

from models import Member, Event, Announcement, TutoringTime
from forms import RegistrationForm, MemberForm, TutoringTimeForm, EventForm



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
    username = password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)      
                return HttpResponseRedirect(reverse('usdacm.views.index'))
    return render_to_response('usdacm/login.html', 
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


def edit_profile(request, userid):    
    if request.user.id != int(userid): #if this isn't the current user's page, redirect to unauthorized
        return render_to_response('project/unauthorized.html', 
                                  context_instance=RequestContext(request))
    return render_to_response('project/edit_profile.html', 
                              {'userid': userid}, 
                              context_instance=RequestContext(request))






def index(request):
    first_event = Event.objects.order_by('date')[:1]
    rest_events = Event.objects.order_by('date')[1:4]
    return render_to_response('usdacm/index.html', 
                              {'first_event': first_event, 'rest_events' : rest_events}, 
                              context_instance=RequestContext(request))

def about(request):
    return render_to_response('usdacm/about.html', 
                              context_instance=RequestContext(request))

def members(request):
    members = Member.objects.order_by('firstName')
    return render_to_response('usdacm/members.html', 
                              {'members' : members}, 
                              context_instance=RequestContext(request))










def events(request):#, year=date.today().year, month=date.today().month):
    today = date.today()         #get today's date
    #try:
    #    d = date(int(year), int(month), 1) #the first of the month
    #    valErr = False           #there was no value error
    #except ValueError:           #if bad values passed in, default to the current date
    year = today.year        #get today's year
    month = today.month      #get today's month
    #    d = date(today.year, today.month, 1) #the first of this month
    #    valErr = True            #there was a value error
    
    '''
    #get number of days in the month
    nextMonth =int(month) + 1
    nextYear = int(year)
    if (nextMonth == 13): 
        nextMonth = 1
        nextYear = int(year)+1
    days = (date(nextYear, nextMonth, 1) - d).days
    
    #get the number of days last month
    lastMonth = int(month) - 1
    lastYear = int(year)
    if (lastMonth == 0): 
        lastMonth = 12
        lastYear = int(year)-1
    lastDays = (d - date(lastYear, lastMonth, 1)).days


    weekStart = (d.weekday()+1)%7 #day of the week of the first of the month
    rolloverDays = weekStart   #number of days from the previous month
    previewDays = 6 - (d.replace(day=days).weekday()+1)%7
    '''

    events = Event.objects.order_by('date')


    return render_to_response('usdacm/events.html', 
                              {'events' : events, 
                               'year' : today.year, 
                               'month' : today.month,
                               },
                              context_instance=RequestContext(request))





def get_month_events(request):
    context = RequestContext(request)
    
    date(2014, 3, 1)
    #by default, use today's month and year
    year = date.today().year
    month = date.today().month
    
    #get the passed in year and month from the JavaScript's GET request
    if request.method == 'GET':
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
    monthEvents = Event.objects.filter(date__year=year).filter(date__month=month)
    nextMonthEvents = Event.objects.filter(date__year=nextDate.year).filter(date__month=prevDate.month)
    
    
    monthList = list()

    #get previous month's events
    for day in range(prevDays-weekStart+1, prevDays+1):
        eventList = [obj.as_dict() for obj in prevMonthEvents.filter(date__day=day)]
        monthList.append( dict(day=day, events=eventList, active=False) )

    #get current month's events
    for day in range(1, currDays+1):
        eventList = [obj.as_dict() for obj in monthEvents.filter(date__day=day)]
        monthList.append( dict(day=day, events=eventList, active=True) )
        
    #get next month's events
    for day in range(1, 7-weekEnd):
        eventList = [obj.as_dict() for obj in nextMonthEvents.filter(date__day=day)]
        monthList.append( dict(day=day, events=eventList, active=False) )


    return HttpResponse(json.dumps(monthList))








def announcements(request):
    announcements = Announcement.objects.order_by('date')
    return render_to_response('usdacm/announcements.html', 
                              {'announcements' : announcements}, 
                              context_instance=RequestContext(request))

def tutoring(request):
    return render_to_response('usdacm/tutoring.html', 
                              context_instance=RequestContext(request))

def tutoring_schedule(request):
    mon = TutoringTime.objects.filter(day=0).order_by('start')
    tues = TutoringTime.objects.filter(day=1).order_by('start')
    wed = TutoringTime.objects.filter(day=2).order_by('start')
    thurs = TutoringTime.objects.filter(day=3).order_by('start')
    fri = TutoringTime.objects.filter(day=4).order_by('start')
    sat = TutoringTime.objects.filter(day=5).order_by('start')
    sun = TutoringTime.objects.filter(day=6).order_by('start')

    return render_to_response('usdacm/tutoring_schedule.html', 
                              {'monday' : mon, 'tuesday' : tues,
                               'wednesday' : wed, 'thursday' : thurs,
                               'friday' : fri, 'saturday' : sat,
                               'sunday' : sun},
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
            #member.tutoringTimes.add(ttime)
            return HttpResponseRedirect(reverse('usdacm.views.tutoring_schedule'))
    else:
        form = TutoringTimeForm()
                                       
    return render_to_response('usdacm/tutoring_signup.html', 
                              {'form' : form},
                              context_instance=RequestContext(request))


def create_event(request):
    if request.method == 'POST':
        form = EventForm(resuest.POST)
        if form.is_valid():
            form.save()
            #member = Member.objects.get(user=request.user)
            #ttime = form.save(commit=False)
            #ttime.member = member
            #ttime.save()
            #member.tutoringTimes.add(ttime)
            return HttpResponseRedirect(reverse('usdacm.views.events'))
    else:
        form = EventForm()
                                       
    return render_to_response('usdacm/create_event.html', 
                              {'form' : form},
                              context_instance=RequestContext(request))


