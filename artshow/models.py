from django.db import models

# Create your models here.


class Submission(models.Model):
    groupNumber = models.IntegerField()
    student1 = models.CharField(max_length=40)
    student2 = models.CharField(max_length=40, blank=True)
    student3 = models.CharField(max_length=40, blank=True)
    pic = models.ImageField(upload_to='artshow/submissions/pictures')
    title =  models.CharField(max_length=60)
    description =  models.TextField(max_length=500, blank=True)
    code = models.FileField(upload_to='artshow/submissions/code')

    def __unicode__(self):
        return "%s - %s" % (self.groupNumber, self.title)
    
