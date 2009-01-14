from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import get_mod_func
from django import forms

from usertools.forms import UserForm, TransferFormBase, DuplicateFormBase
from usertools.helpers import update_related_field

ADMIN_CONTEXT = {'title':'User Tools'}

@staff_member_required
def usertools(request, template="usertools/usertools.html", context=None,
              next=None, form_class=UserForm):
    context = context or ADMIN_CONTEXT
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
        
@staff_member_required
def export(request):
    data = User.objects.values_list('email', flat=True)
    context = {'data':data}
    response = render_to_response('export.html', context, RequestContext(request))
    filename = "users.xls" # would be cool to put the data here?
    response['Content-Disposition'] = 'attachment; filename=%s ' % filename
    response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'
    return response

@staff_member_required
def tool(request, model_cls, form_cls, template, context=None, next="."):
    """ 
    """
    if context
    context = context or ADMIN_CONTEXT

    if isinstance(model_cls, str):
        mod_name, model_name = get_mod_func(model_cls)
        model_cls = getattr(__import__(mod_name, {}, {}, ['']), model_name)
        
    class ToolForm(form_cls):
        objs = forms.ModelMultipleChoiceField(model_cls._default_manager.all())

    if request.method == "POST":
        form = ToolForm(request.POST)
        if form.is_valid():
            form.save(request)
            return HttpResponseRedirect(next)
    else:
        form = ToolForm()    
    context['form'] = form
    return render_to_response(template, context , RequestContext(request))

def duplicate(request, model_cls):
    """
    put me in your url conf
    
    (r'^transfer/$', 'usertools.views.transfer', {'model_cls': 'blog.models.Post'})
    
    
    """
    return tool(request, model_cls, DuplicateFormBase, "usertools/tool.html")
    
def transfer(request, model_cls):
    "put me in your url conf"
    return tool(request, model_cls, TransferFormBase, "usertools/tool.html")