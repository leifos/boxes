__author__ = 'leif'

from django.conf.urls import patterns, url, include
import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
                       url(r'^howToPlay/$', views.howToPlay, name='howToPlay'),
                       url(r'^start/(?P<num>[0-9]+)/$', views.startgame, name='startgame'),
                       url(r'^pick/(?P<username>[a-zA-Z0-9_.+@-]+)', views.pick, name='pick'),
                       url(r'^query/$', views.query, name='query'),
                       url(r'^assess/$', views.assess, name='assess'),
                       url(r'^players/(?P<username>[a-zA-Z0-9_.+@-]+)', views.profile_page, name='profile'),
                       url(r'^leaderboard/$', views.leaderboard, name='leaderboard'),
                       )
