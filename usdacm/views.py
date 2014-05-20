# views.py
# USD ACM
# Laura Londo
# 20 May 2014


'''
This document defines a callback for every page available on the website. When 
an internet browser or other device makes a request to a URL in the website, 
the corresponding view responsible for that URL is called. The view will query 
the database for the relevant data, if needed, and render the data to the 
caller, usually along with other resources needed to display a page. 
'''


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

from models import Member, Event, Announcement, TutoringTime, EventComment, AnnouncementComment, CarouselSlide
from forms import RegistrationForm, MemberForm, TutoringTimeForm, EventForm, AnnouncementForm, EventCommentForm, AnnouncementCommentForm, CarouselSlideForm




# view for registering a new user/member in the database
#
def register_user(request):
    if request.method == 'POST':                         # if the form was submitted on page load,
        form = RegistrationForm(request.POST)            # retrieve the registration form
        form2 = MemberForm(request.POST, request.FILES)  # retrieve the mamber form
        if form.is_valid() and form2.is_valid():         # if both forms are filled in correctly,
            User.objects.create_user(                    # create a new user
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
                email=form.cleaned_data['email']
                )
            user = authenticate( username=form.cleaned_data['username'], #ensure the new user is authenticated
                                 password=form.cleaned_data['password1'])
            login(request, user)                     # log the new user in
            member = form2.save(commit=False)        # save the member form without submitting to the database
            member.user = user                       # link the new user to the member object as a foriegn key
            member.save()                            # save and submit the new member object
            return HttpResponseRedirect(reverse('usdacm.views.profile', # redirect to this user's profile view
                                                args=(user.username,))) 
    else:                                            # else this is a GET request (a form was not submitted)
        form = RegistrationForm()                    # create a new registration form
        form2 = MemberForm()                         # create a new member form
    return render_to_response('usdacm/register_user.html',    # render registration page 
                              {'form': form, 'form2': form2}, # and pass it both forms
                              RequestContext(request)) 

# member login page
def login_user(request):
    logout(request)                                  # log the previous user out
    error = None
    username = password = '' 
    if request.POST:                                 # if the login form was submitted
        username = request.POST['username']          # get the form's username
        password = request.POST['password']          # and password
        user = authenticate(username=username, password=password) #attempt to authenticate the user
        if user is not None:                         # if the user credentials matched,
            if user.is_active:                       # and if the user's account is active 
                login(request, user)                 # log the user in
                return HttpResponseRedirect(reverse('usdacm.views.index')) #redirect the user to the home page
        else:                                        # if the login information was incorrect,
            error = "Uhhhh... that's WRONG!!"        # error message
    return render_to_response('usdacm/login.html',   # render the login page with any error messages
                              {'error' : error},
                              context_instance=RequestContext(request))

# logout request and redirect
def logout_user(request):
    logout(request)                                 # log the current user out
    return HttpResponseRedirect(reverse('usdacm.views.index')) # redirect to the home page


# member profile page. Takes in the username of the member to be viewed
def profile(request, name):
    usr = get_object_or_404(User, username=name)    # find the requested user or render the 404 page
    member = Member.objects.get(user=usr)           # get the member object linked to this user
    return render_to_response('usdacm/profile.html',# render the profile tamplate
                              {'member': member},   # pass the member object to the template
                              context_instance=RequestContext(request))

# edit member profile. requires a loged-in user
@login_required
def edit_profile(request, userid):    
    if request.user.id != int(userid):              # if this isn't the current user's page, 
        return render_to_response('project/unauthorized.html', # redirect to unauthorized
                                  context_instance=RequestContext(request))
    return render_to_response('project/edit_profile.html', # render the edit profile template
                              {'userid': userid},   # pass the user id of the member to edit
                              context_instance=RequestContext(request))

# displays the members of the ACM club
def members(request):
    members = Member.objects.order_by('firstName')  # get all members sorted by name
    return render_to_response('usdacm/members.html',# render the members template 
                              {'members' : members},# pass the list of member objects to the template
                              context_instance=RequestContext(request))









# home page
def index(request):
    today = date.today()                           # get today's date
    events = Event.objects.filter(date__gte=today).order_by('date')[0:3] # get the first four events on or after today
    announ = Announcement.objects.order_by('created')[0:3] # get the latest four announcements
    slides = CarouselSlide.objects.order_by('position') # get the carousel objects to display in the image slider
    return render_to_response('usdacm/index.html', # render the index template
                              {'events' : events,  # pass the events list
                               'announcements' : announ, # the announcements list
                               'slides' : slides },# and carousel slides to the template
                              context_instance=RequestContext(request))


# about page. gives general information about ACM and computer science
def about(request):
    return render_to_response('usdacm/about.html', # render the about template
                              context_instance=RequestContext(request))





# ANNOUNCEMENTS ==========================================================================
# views that deal with announcement objects

# announcements page. Lists all of the announcements by most recent posting date
def announcements(request):
    announcements = Announcement.objects.order_by('-created') # get all anouncements ordered by date created
    return render_to_response('usdacm/announcements.html',    # render the annoucements template
                              {'announcements' : announcements}, # pass the list of announcements to the template
                              context_instance=RequestContext(request))

# announcement view. shows the complete information about the specified announcement.
# takes in the id of the requested announcement
def announcement(request, announcementId):
    announ = get_object_or_404(Announcement, pk=announcementId) # get the announcement or return 404 page
    modified = False                                    # whether the announcement has been modified
    if(announ.last_modified - announ.created > timedelta(minutes=1)): # if the update and created time are not the same,
        modified = True                                 # then there has been a modification

    comments = AnnouncementComment.objects.filter(announcement=announ).order_by('date') # get all comments for this announcement
    commentForm = AnnouncementCommentForm(request.POST) # if a comment form has been posted,
    if commentForm.is_valid():                          # if the form is valid       
        comm = commentForm.save(commit=False)           # create the comment object
        comm.member = Member.objects.get(user=request.user) # set poster to the curent user
        comm.announcement = announ                      # set the foreign key to the current announcement object
        comm.date = datetime.now()                      # set the date of the comment creation
        comm.save()                                     # save the comment to the database
        # redirect to the same announcement page
        return HttpResponseRedirect(reverse('usdacm.views.announcement', kwargs={ 'announcementId': announ.id }))
    else:                                               # else the form was invalid,
        commentForm = AnnouncementCommentForm()         # create a new form
        
    return render_to_response('usdacm/announcement.html', # render the announcement template
                              {'announcement' : announ, # pass teh viewd announcment object
                               'comments' : comments,   # the list of comments  
                               'commentForm' : commentForm, # and the comment form
                               },
                              context_instance=RequestContext(request))


# view to create a new announcement. member login required.
@login_required
def create_announcement(request):
    if request.method == 'POST':                       # if a form has been submitted
        form = AnnouncementForm(request.POST)          # get the form information
        if form.is_valid():                            # if the form fields are valid
            announcement = form.save(commit=False)     # create a new announcement object
            member = Member.objects.get(user=request.user) # get the current user
            announcement.created_by = member           # set the creator to the current user
            announcement.last_modified_by = member     # set the last updated by to the current user
            announcement.save()                        # save the new announcement
            return HttpResponseRedirect(reverse('usdacm.views.announcements')) #redirect the the announcemetns page
    else:                                              # else a form was not submitted
        form = AnnouncementForm()                      # create a new form
                                       
    return render_to_response('usdacm/create_announcement.html', # render the create announcement template 
                              {'form' : form},                   # pass teh form to the template
                              context_instance=RequestContext(request))
    

# edit an announcemetn. member login required.
# takes in the announcement id for the requested announcement
@login_required
def edit_announcement(request, announcementId):        
    announcement = get_object_or_404(Announcement, pk=announcementId)# get the announcement or render a 404 page
    return render_to_response('usdacm/edit_announcement.html', # reder the edit announcement template
                              {'announcement' : announcement}, # pass the announcement object to the template
                              context_instance=RequestContext(request))


# delete an event. member login required. 
# takes in the announcement id for the requested announcement
@login_required
def delete_announcement(request, announcementId):
    announcement = get_object_or_404(Announcement, pk=announcementId).delete() # get the event or return 404 page
    return HttpResponseRedirect(reverse('usdacm.views.announcements')) # redirect to the  announcement page





# EVENTS =================================================================================
# views pertaining to events

# announcements page. Lists a few of the upcoming events
def events(request):
    today = date.today()                             # get today's date
    events = Event.objects.order_by('date').filter(date__gte=today)[0:4] # get the next 5 events starting today

    return render_to_response('usdacm/events.html',  # render the events template
                              {'events' : events,    # pass the events list
                               'year' : today.year,  # the current year
                               'month' : today.month,# and the current month for use in the calendar
                               },
                              context_instance=RequestContext(request))


# event view. shows the complete information about the specified event.
# takes in the id of the requested event
def event(request, eventId):
    event = get_object_or_404(Event, pk=eventId)     # get the event or render 404 page
    modified = False                                 # whether the event has been modified
    if(event.last_modified - event.created > timedelta(minutes=1)): # if the update and creation time are not the same,
        modified = True                              # the event has been modified
    
    comments = EventComment.objects.filter(event=event).order_by('date') # get all the commets for this event
    commentForm = EventCommentForm(request.POST)     # if the comment form has been posted
    if commentForm.is_valid():                       # and if the comment form is valid
        comm = commentForm.save(commit=False)        # create a new comment object
        comm.member = Member.objects.get(user=request.user) # get the current user
        comm.event = event                           # link the event to the comment
        comm.date = datetime.now()                   # set the post date for the comment
        comm.save()                                  # save the new comment object to the database
        return HttpResponseRedirect(reverse('usdacm.views.event', kwargs={ 'eventId': event.id })) # redirect to the same event page
    else:                                            # else the comment form was invalid
        commentForm = EventCommentForm()             # create a new comment form
        
    return render_to_response('usdacm/event.html',   # render the event template
                              {'event' : event,      # pass in the event object
                               'modified' : modified,# the modification status
                               'comments' : comments,# the list of comments
                               'commentForm' : commentForm}, # adn the comment form
                              context_instance=RequestContext(request))


# event creation view. member login required.
@login_required
def create_event(request):
    if request.method == 'POST':                     # if the form was posted,
        form = EventForm(request.POST, request.FILES)# get the form information
        if form.is_valid():                          # and if the form is valid,
            event = form.save(commit=False)          # create a new event object
            member = Member.objects.get(user=request.user) # get teh current user
            event.created_by = member                # set this user as the event creator
            event.last_modified_by = member          # set the last modified field to this user

            # the following is a proposed method to rescale the event image upon uplaod, however the server
            # sends back an error that the jped decoder is not available.
            
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

            event.save()                          # save the new event to the database
            return HttpResponseRedirect(reverse('usdacm.views.events')) # redirect to the events page
    else:                                         # else the form was not posted
        form = EventForm()                        # create a new form
                                       
    return render_to_response('usdacm/create_event.html', # render the create event template
                              {'form' : form},            # pass the event form to the template
                              context_instance=RequestContext(request))

# edit event view. member login required.
# takes int the id of the requested event.
@login_required
def edit_event(request, eventId):
    event = get_object_or_404(Event, pk=eventId)  # get the event or return 404 page
    return render_to_response('usdacm/edit_event.html', # render the edit event template
                              {'event' : event},  # pass the event object to the template
                              context_instance=RequestContext(request))

# delete event. member login required.
# takes in teh id of the requested event
@login_required
def delete_event(request, eventId):
    event = get_object_or_404(Event, pk=eventId).delete() # get the event and delete it or return 404 page
    return HttpResponseRedirect(reverse('usdacm.views.events')) # redirect to events page
    

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
# views pertaining to tutoring


# the turoring schedule adn information page
def tutoring_schedule(request):
    days = list()                                      # create a new list for days
    # get tutoring times for Monday through Fridau
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

    return render_to_response('usdacm/tutoring_schedule.html', #render teh ttoring schedule template
                              {'days' : days,},                # pass the list of tutoring days with their times
                              context_instance=RequestContext(request))


# tutoring sign up view. requires member login.
@login_required
def tutoring_signup(request):
    if request.method == 'POST':                       # if the tutoring form is posted,
        form = TutoringTimeForm(request.POST)          # get the information from the form
        if form.is_valid():                            # if the form is valid,
            member = Member.objects.get(user=request.user) # get the current user
            ttime = form.save(commit=False)            # create a new tutoring time object
            ttime.member = member                      # set the tutor member to the current user
            ttime.save()                               # save the tutoring time to the database
            return HttpResponseRedirect(reverse('usdacm.views.tutoring_schedule')) #redirect to the tutoring schedule page
    else:                                              # else the form was not submitted
        form = TutoringTimeForm()                      # create a new tutoring form
                                       
    return render_to_response('usdacm/tutoring_signup.html', # render the tutoring signup template
                              {'form' : form},         # pass the form to the template
                              context_instance=RequestContext(request))


# delete a tutoring time. member login required
# takes in an id for the requested ttime object
@login_required
def tutoring_delete(request, ttimeId):
    ttime= get_object_or_404(TutoringTime, pk=ttimeId).delete() # get the ttime and delete is or return 404 page
    return HttpResponseRedirect(reverse('usdacm.views.tutoring_schedule')) # redirect to the totoring schedule page




# Carousel Slide. the images and descriptions used in the image slider on the home page
# create a new carousel slide
@login_required
def carouselSlide_create(request):
    return 0
    
