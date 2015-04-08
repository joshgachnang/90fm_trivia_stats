from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.http import HttpResponse
from django.views.generic.base import RedirectView
from rest_framework.routers import DefaultRouter

from website import api

admin.autodiscover()

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'api/v1/subscribers', api.SubscriberViewSet)
router.register(r'api/v1/scores', api.ScoreViewSet)
router.register(r'api/v1/teams', api.TeamsList)

urlpatterns = patterns(
    "",
    # url(r"^$", direct_to_template, {
    # "template": "homepage.html",
    # }, name="home"),
    url(r"^admin/", include(admin.site.urls)),
    url(r'^api/v1/auth/', include('djoser.urls')),
)
urlpatterns += patterns(
    'website.views',
    url(r'^', include(router.urls)),
    url(r'^$', 'home', name='home'),
    (r'^robots\.txt$', lambda r: HttpResponse(
        'User-agent: Google\nDisallow:"',
        mimetype="text/plain")),
    url(r'^favicon\.ico$', RedirectView.as_view(
        url='/static/img/favicon.ico')),
    url(r'^api-auth/',
        include('rest_framework.urls', namespace='rest_framework'))
)
