from django.conf import settings
from django.conf.urls import *

from django.contrib import admin
admin.autodiscover()


handler500 = "pinax.server_error"


urlpatterns = patterns("",
    #url(r"^$", direct_to_template, {
        #"template": "homepage.html",
    #}, name="home"),
    url(r"^admin/", include(admin.site.urls)),
)
urlpatterns += patterns('website.views',
    url(r"^$", "home", name="home"),
    # Utility function
    # (r'^scrape/(?P<yr>\d+)/(?P<hr>\d+)/$', 'scrape_year_hour'),
    #(r'^bulkdelete/$', 'bulkdelete'),
    #(r'^year/(?P<yr>\d+)/$', 'teams_by_year'), #This will list the teams that participated that year

    # Meant for cron jobs
    # (r'^scraper/$', 'scraper'),
    (r'^team/(?P<team_name>\S+)/$', 'team'),
    (r'^team/(?P<team_name>\S+)/(?P<team_year>\d{4})/$', 'team'),
    (r'^email/subscribe/$', 'email_subscribe'),
    (r'^email/unsubscribe/$', 'email_unsubscribe'),
    (r'^sms/subscribe/$', 'sms_subscribe'),
    (r'^sms/unsubscribe/$', 'sms_unsubscribe'),
    (r'^search/$', 'search'),
    (r'^archive/$', 'archive'),
    # (r'^years/$', 'past_years'),
    # (r'^years/(?P<year>\d+)/$', 'past_year_hours'),
    (r'^score/(?P<year>\d{4})/(?P<hour>\d{1,2})/$', 'year_hour_overview'),
)

urlpatterns += (url(r'^admin/django-ses/', include('django_ses.urls')),)
