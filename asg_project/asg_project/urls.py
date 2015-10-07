from django.conf.urls import patterns, include, url
from django.http import HttpResponseRedirect
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', include('asg.urls')),
    # url(r'^asg_project/', include('asg_project.foo.urls')),
    url(r'^asg/', include('asg.urls')),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    (r'^admin/', include(admin.site.urls)),
    (r'^accounts/', include('registration.backends.simple.urls')),

    (r'^users/', lambda x: HttpResponseRedirect('/asg/')),

)
