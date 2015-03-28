from django.conf.urls import *
from django.contrib import admin
from website import api

admin.autodiscover()
from django.conf.urls import patterns, include, url
from django.views.generic.base import RedirectView
from django.http import HttpResponse
from rest_framework.routers import DefaultRouter

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'api/v1/users', api.UserViewSet)
router.register(r'api/v1/email_subscribers', api.EmailSubscriberViewSet)
router.register(r'api/v1/sms_subscribers', api.SMSSubscriberViewSet)
router.register(r'api/v1/scores', api.ScoreViewSet)

urlpatterns = patterns(
    "",
    # url(r"^$", direct_to_template, {
    # "template": "homepage.html",
    # }, name="home"),
    url(r"^admin/", include(admin.site.urls)),
    url(r'^auth/', include('djoser.urls')),
)
urlpatterns += patterns(
    'website.views',
    url(r'^', include(router.urls)),
    url(r'^$', 'home', name='home'),
    # Utility function
    # (r'^scrape/(?P<yr>\d+)/(?P<hr>\d+)/$',
    # 'scrape_year_hour'),

    # (r'^bulkdelete/$', 'bulkdelete'),
    # (r'^year/(?P<yr>\d+)/$', 'teams_by_year'),
    # #This will list the teams that participated that year

    # Meant for cron jobs
    # (r'^scraper/$', 'scraper'),
    (r'^team/(?P<team_name>\S+)/$', 'team'),
    (r'^team/(?P<team_name>\S+)/(?P<team_year>\d{4})/$',
     'team'),
    (r'^email/subscribe/$', 'email_subscribe'),
    (r'^email/unsubscribe/$', 'email_unsubscribe'),
    (r'^sms/subscribe/$', 'sms_subscribe'),
    (r'^sms/unsubscribe/$', 'sms_unsubscribe'),
    (r'^search/$', 'search'),
    (r'^archive/$', 'archive'),
    # (r'^years/$', 'past_years'),
    # (r'^years/(?P<year>\d+)/$', 'past_year_hours'),
    (r'^score/(?P<year>\d{4})/(?P<hour>\d{1,2})/$',
     'year_hour_overview'),

    (r'^robots\.txt$', lambda r: HttpResponse(
        'User-agent: Google\nDisallow:"',
        mimetype="text/plain")),
    url(r'^favicon\.ico$', RedirectView.as_view(
        url='/static/img/favicon.ico')),
    url(r'^api-auth/',
        include('rest_framework.urls', namespace='rest_framework'))
)
