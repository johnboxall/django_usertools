from django import forms
from django.conf import settings
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.auth import login, get_backends
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from usertools.helpers import update_related_fields, duplicate


USER_TYPE_ID = ContentType.objects.get(app_label="auth", model="user").id


class LoginAsForm(forms.Form):
    """
    Form that logins you in as User. You can restrict the Users by passing
    a queryset `qs`.
    
    """
    # TODO: Be nice to use a ForeignKeyRawIdWidget here, but it
    #       requires a rel parameter - how would we fake that?
    user = forms.ModelChoiceField(queryset=User.objects.all())
    
    def __init__(self, data=None, files=None, request=None, qs=None, *args,
                 **kwargs):
        super(LoginAsForm, self).__init__(data=data, files=files, *args, **kwargs)
        self.request = request
        
        # Rendering a million users takes a while, so login by id.
        self.fields["user"].widget = forms.TextInput()

        if qs is not None:
            self.fields["user"].queryset = qs
    
    def save(self):
        user = self.cleaned_data["user"]
        
        # In lieu of a call to authenticate()
        backend = get_backends()[0]
        user.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
        login(self.request, user)
        
        message = "Logged in as %s" % self.request.user        
        self.request.user.message_set.create(message=message)


class UserForm(forms.Form):
    "Create a User from an email address."
    email = forms.EmailField()
    
    def save(self, request):    
        email = self.cleaned_data['email']
        user = User.objects.create_user(email, email, email)
        message = "User added."
        LogEntry.objects.log_action(request.user.id, USER_TYPE_ID, user.id, unicode(user), ADDITION, message)        
        request.user.message_set.create(message=message)        
        return user


class AdminToolFormBase(forms.Form):
    "This must be subclassed to work."
    user = forms.ModelChoiceField(User.objects.all())


class TransferFormBase(AdminToolFormBase):
    def save(self, request):
        objs = self.cleaned_data['objs']
        user = self.cleaned_data['user']
        for obj in objs:
            # Uses `update` so we need to pass in the `user.id`
            update_related_field(obj, {"user": user.id})
        message = "Transfer complete."
        request.user.message_set.create(message=message)


class DuplicateFormBase(AdminToolFormBase):
    def save(self, request, callback=None, **kwargs):
        objs = self.cleaned_data['objs']
        user = self.cleaned_data['user']
        for obj in objs:
            clone = duplicate(obj, {"user": user}, **kwargs)
            if callable(callback):
                callback(clone)
        message = "Duplicate complete."
        request.user.message_set.create(message=message)