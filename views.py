from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.forms.models import BaseModelFormSet, modelformset_factory
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.generic.create_update import delete_object
from django.views.decorators.vary import vary_on_headers
from django.views.decorators.cache import cache_page, never_cache
from django.contrib.sites.models import Site


from usertools.forms import *

ADMIN_CONTEXT = {'title':'User Tools'}

@login_required
def usertools(request, template="usertools.html", context=None, next=None, form_class=UserForm):
    if context is None:
        context = ADMIN_CONTEXT
    else:
        context = ADMIN_CONTEXT.update(context)
    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            form.save(request)
            if next is None:
                next = reverse('usertools')
            return HttpResponseRedirect(next)
    else:
        form = form_class()
    context['form'] = form    
    return render_to_response(template, context, RequestContext(request))
    
@login_required
def export(request):
    data = User.objects.values_list('email', flat=True)
    context = {'data':data}
    response = render_to_response('export.html', context, RequestContext(request))
    filename = "users.xls" # would be cool to put the data here?
    response['Content-Disposition'] = 'attachment; filename=%s ' % filename
    response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'
    return response