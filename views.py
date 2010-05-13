from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import reverse, get_mod_func
from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.functional import curry

from usertools.forms import UserForm, TransferFormBase, DuplicateFormBase, LoginAsForm


DEFAULT_CONTEXT = {'title':'User Tools'}


@staff_member_required
def login_as(request, form_cls=LoginAsForm, template="usertools/login_as.html",
             ctx=None, next=None, qs=None):
    ctx = ctx or DEFAULT_CONTEXT.copy()
    if request.method == "POST":
        form = form_cls(request.POST, request=request, qs=qs)
        if form.is_valid():
            form.save()
            next = next or request.REQUEST.get("next") or settings.LOGIN_REDIRECT_URL
            return HttpResponseRedirect(next)
    else:
        form = form_cls(request.GET, request=request, qs=qs)
    
    ctx["form"] = form
    return render_to_response(template, ctx, RequestContext(request))

@staff_member_required
def usertools(request, template="usertools/usertools.html", ctx=DEFAULT_CONTEXT,
              next=None, form_cls=UserForm):
    form = form_cls(request.POST or None)
    if form.is_valid():
        form.save(request=request)
        if next is None:
            next = reverse('usertools')
        return HttpResponseRedirect(next)
    
    ctx['form'] = form    
    return render_to_response(template, ctx, RequestContext(request))

#TODO: This is ugly as sin.
@staff_member_required
def tool(request, model_cls, form_cls, template, ctx=DEFAULT_CONTEXT, next="", **kwargs):
    
    # Allow passing model_cls as a string.
    if isinstance(model_cls, str):
        mod_name, model_name = get_mod_func(model_cls)
        model_cls = getattr(__import__(mod_name, {}, {}, ['']), model_name)
    
    #TODO: Could allow this to be overridden easier?
    class ToolForm(form_cls):
        objs = forms.ModelMultipleChoiceField(model_cls._default_manager.all())
    
    form = ToolForm(request.POST or None)
    if form.is_valid():
        form.save(request, **kwargs)
        return HttpResponseRedirect(next)
    
    ctx['form'] = form
    return render_to_response(template, ctx , RequestContext(request))

def duplicate(request, model_cls, model_order=None, template="usertools/tool.html"):
    return tool(request, model_cls, DuplicateFormBase, template, model_order=model_order)

def transfer(request, model_cls, template="usertools/tool.html"):
    return tool(request, model_cls, TransferFormBase, template)

#TODO: This would be a lot more fun as a generic admin action.
@staff_member_required
def export(request, temlate='usertools/export.html', filename="users.xls"):
    data = User.objects.values_list('email', flat=True)
    context = {'data': data}
    response = render_to_response(template, context, RequestContext(request))
    response['Content-Disposition'] = 'attachment; filename=%s ' % filename
    response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'
    return response