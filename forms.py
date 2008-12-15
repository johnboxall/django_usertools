from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.admin.models import ADDITION
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.models import LogEntry

USER_TYPE_ID = ContentType.objects.get(app_label="auth", model="user").id
MESSAGE = "User added."

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
        
        LogEntry.objects.log_action(request.user.id, USER_TYPE_ID, user.id, unicode(user), ADDITION, MESSAGE)        
        request.user.message_set.create(message=MESSAGE)

        
        return user