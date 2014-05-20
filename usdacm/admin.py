from django.contrib import admin
from usdacm import models

# Register models here.
admin.site.register(models.Member)
admin.site.register(models.Event)
admin.site.register(models.Announcement)
admin.site.register(models.TutoringTime)
admin.site.register(models.EventComment)
admin.site.register(models.AnnouncementComment)
admin.site.register(models.CarouselSlide)

