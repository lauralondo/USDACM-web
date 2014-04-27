from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from models import Submission
from forms import SubmissionForm

# Create your views here.

def submissions(request):
    subs = Submission.objects.order_by('groupNumber')
    return render_to_response('artshow/artshow.html', 
                  {'submissions' : subs},
                  context_instance=RequestContext(request))

def new_submission(request):
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('artshow.views.submissions'))
    else:
        form = SubmissionForm()
    return render_to_response('artshow/new_submission.html', 
                              {'form' : form},
                              context_instance=RequestContext(request))
    
