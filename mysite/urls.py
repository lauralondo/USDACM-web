from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()



urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),




    (r'^$', 'usdacm.views.index'),
    (r'^login/$', 'usdacm.views.login_user'),
    (r'^logout/$', 'usdacm.views.logout_user'),
    (r'^profile/(\w+)/$', 'usdacm.views.profile'),
    (r'^profile/edit_profile/(?P<userid>\d+)/$', 'usdacm.views.edit_profile'),
    (r'^join/$', 'usdacm.views.register_user'),
    (r'^about/$', 'usdacm.views.about'),
    (r'^members/$', 'usdacm.views.members'),

    (r'^event/(?P<eventId>\d+)/$', 'usdacm.views.event'),
    (r'^events/$', 'usdacm.views.events'),
    (r'^events/create/$', 'usdacm.views.create_event'),
    (r'^event/edit/(?P<eventId>\d+)/$', 'usdacm.views.edit_event'),
    (r'^event/delete/(?P<eventId>\d+)/$', 'usdacm.views.delete_event'),
    (r'^get_month_events/$', 'usdacm.views.get_month_events'),

    (r'^announcements/$', 'usdacm.views.announcements'),
    (r'^announcement/(?P<announcementId>\d+)/$', 'usdacm.views.announcement'),
    (r'^announcement/create/(?P<announcementId>\d+)/$', 'usdacm.views.create_announcement'),
    (r'^announcement/edit/(?P<announcementId>\d+)/$', 'usdacm.views.edit_announcement'),
    (r'^announcement/delete/(?P<announcementId>\d+)/$', 'usdacm.views.delete_announcement'),

    (r'^tutoring/$', 'usdacm.views.tutoring'),
    (r'^tutoring/schedule/$', 'usdacm.views.tutoring_schedule'),
    (r'^tutoring/sign-up/$', 'usdacm.views.tutoring_signup'),
    (r'^tutoring/delete/(?P<ttimeId>\d+)/$', 'usdacm.views.tutoring_delete'),


    (r'^artshow/$', 'artshow.views.submissions'),
    (r'^artshow/new_submission/$', 'artshow.views.new_submission'),


)
