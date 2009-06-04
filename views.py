from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import reverse, get_mod_func
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.functional import curry

from usertools.forms import UserForm, TransferFormBase, DuplicateFormBase, LoginAsForm
from usertools.helpers import update_related_field

ADMIN_CONTEXT = {'title':'User Tools'}


def post_form_view(request, form_cls, template="usertools/login_as.html",
              context=None, next=None, ):
    ctx = context or {}
    ctx.update(ADMIN_CONTEXT)

    data = request.POST or None
    form = form_cls(data, request=request)

    if form.is_valid():
        form.save()        
        return HttpResponseRedirect(next or ".")

    ctx["form"] = form    
    return render_to_response(template, ctx, RequestContext(request))
    
@staff_member_required
def login_as(request, form_cls=LoginAsForm, template="usertools/login_as.html",
             context=None, next=settings.LOGIN_REDIRECT_URL, qs=None):
    form_cls_qs = curry(form_cls, qs=qs)
    return post_form_view(request, form_cls_qs, template, context, next)

# @@@ Refractor to use post_form_view...
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
def export(request, temlate='usertools/export.html', filename="users.xls"):
    data = User.objects.values_list('email', flat=True)
    context = {'data': data}
    response = render_to_response(template, context, RequestContext(request))
    response['Content-Disposition'] = 'attachment; filename=%s ' % filename
    response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'
    return response

@staff_member_required
def tool(request, model_cls, form_cls, template, context=None, next=".", **kwargs):
    context = context or ADMIN_CONTEXT

    if isinstance(model_cls, str):
        mod_name, model_name = get_mod_func(model_cls)
        model_cls = getattr(__import__(mod_name, {}, {}, ['']), model_name)
    # Else it should be a subclass of model or assert.
        
    # @@@ How could you allow this to be overridden?
    class ToolForm(form_cls):
        objs = forms.ModelMultipleChoiceField(model_cls._default_manager.all())

    if request.method == "POST":
        form = ToolForm(request.POST)
        if form.is_valid():
            form.save(request, **kwargs)
            return HttpResponseRedirect(next)
    else:
        form = ToolForm()    
    context['form'] = form
    return render_to_response(template, context , RequestContext(request))

def duplicate(request, model_cls, duplicate_order=None, callback=None):
    return tool(request, model_cls, DuplicateFormBase, "usertools/tool.html", duplicate_order=duplicate_order)
    
def transfer(request, model_cls):
    return tool(request, model_cls, TransferFormBase, "usertools/tool.html")