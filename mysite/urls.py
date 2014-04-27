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


    (r'^events/$', 'usdacm.views.events'),
    (r'^events/(?P<year>\d+)/(?P<month>\d+)/$', 'usdacm.views.events'),

    (r'^get_month_events/$', 'usdacm.views.get_month_events'),

    (r'^events/create/$', 'usdacm.views.create_event'),
    (r'^announcements/$', 'usdacm.views.announcements'),
    (r'^tutoring/$', 'usdacm.views.tutoring'),
    (r'^tutoring/schedule/$', 'usdacm.views.tutoring_schedule'),
    (r'^tutoring/sign-up/$', 'usdacm.views.tutoring_signup'),

    (r'^artshow/$', 'artshow.views.submissions'),
    (r'^artshow/new_submission/$', 'artshow.views.new_submission'),


)
