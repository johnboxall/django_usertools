from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.admin.models import ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.models import LogEntry

from usertools.helpers import update_related_field, duplicate


USER_TYPE_ID = ContentType.objects.get(app_label="auth", model="user").id


class UserForm(forms.Form):
    "Create a User w/ from an e-mail address."
    email = forms.EmailField()
    
    def save(self, request):    
        email = self.cleaned_data['email']
        username = email.split('@')[0]
        password = username
        user = User.objects.create_user(username, email, password)
        user.username = email
        user.save()
        
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
            update_related_field(obj, user.id, "user")
        message = "Transfer complete."
        request.user.message_set.create(message=message)

class DuplicateFormBase(AdminToolFormBase):
    def save(self, request):
        objs = self.cleaned_data['objs']
        user = self.cleaned_data['user']
        for obj in objs:
            duplicate(obj, user, "user")
        message = "Duplicate complete."
        request.user.message_set.create(message=message)