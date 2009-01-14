from django.conf.urls.defaults import *

urlpatterns = patterns('usertools.views',
    url(r'^tools/$', 'usertools', name="usertools"),
    url(r'^tools/export/$', 'export', name="usertools_export"),
)