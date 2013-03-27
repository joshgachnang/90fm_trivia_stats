# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpResponseServerError, \
    HttpResponseBadRequest
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext, Context
from website.models import Score,  Settings, SMSSubscriberForm, EmailSubscriberForm, EmailSubscriber, SMSSubscriber, \
    SearchForm, get_last_hour, get_last_year, playing_this_year, get_current_hour, get_current_year, during_trivia,\
    get_top_ten_teams
from BeautifulSoup import BeautifulStoneSoup, BeautifulSoup
import urllib2
import sys, os
import re
import time
import datetime
# import settings
from django.core.mail import send_mail
from django.template.loader import get_template

from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.forms.models import model_to_dict


import boto.ses as ses
ses_conn = ses.connect_to_region('us-east-1')
from django.conf import settings


##############################################################################
# Public Views
##############################################################################
def home(request):
    if request.method == 'GET':
        template_data = {}
        template_data['email_form'] = EmailSubscriberForm()
        template_data['sms_form'] = SMSSubscriberForm()
        # template_data['latest_hour'] = get_last_hour()
        # template_data['latest_year'] = get_last_year()
        template_data['top_teams'] = get_top_ten_teams()
        print "SMS: ", template_data['sms_form']
        return render_to_response("homepage.html", template_data, context_instance=RequestContext(request))


# Displays all the information for a team. If year is specified, only for that year.
# team_name: str
# team_year: int
def team(request, team_name, team_year=None):
    team_name = team_name.replace('_', ' ')
    template_data = {}
    template_data['team_name'] = team_name.upper()
    template_data['year'] = team_year
    # during = during_trivia()

    # Check to ensure team is playing this year. Otherwise, just show previous years score.
    template_data['playing'] = playing_this_year(team_name)
    template_data['last_hour'] = get_last_hour()
    template_data['last_year'] = get_last_year()

    template_data['scores'] = {}
    scores = Score.objects.filter(team_name=team_name.upper()).order_by('-year')
    if len(scores) == 0:
        return HttpResponseNotFound("Can't find data for team: {0}".format(team_name))
    template_data['scores'] = {}
    for year in scores.values_list('year').distinct():
        template_data['scores'][year[0]] = scores.filter(year=year[0]).order_by('hour')

    return render_to_response("team.html", template_data, context_instance=RequestContext(request))

# Displays a list of teams, year combos matching the search.
def search(request):
    template_data = {}
    if request.method == 'POST':
        print "POST", request.POST
        form = SearchForm(request.POST)
        if form.is_valid():
            search = form.cleaned_data['search']
            template_data['teams'] = Score.objects.filter(team_name__icontains=search).order_by('year')
        print template_data
        return render_to_response("search_results.html", template_data, context_instance=RequestContext(request))
    else:
        return HttpResponseBadRequest("Only POSTs allowed.")

# Gives the teams and scores for a certain hour in a year
def year_hour_overview(request, year, hour):
    template_data = {}
    template_data['hour'] = year
    template_data['year'] = hour
    scores = Score.objects.filter(year=year, hour=hour)
    template_data['teams'] = {}
    for score in scores:
        template_data['teams'][score.team_name] = model_to_dict(score)
    return render_to_response('hour.html', template_data, context_instance=RequestContext(request))

# List years, and which teams were in first.
def archive(request):
    template_data = {}
    template_data['scores'] = {}
    for year in Score.objects.values_list('year').distinct():
        template_data['scores'][year[0]] = get_top_ten_teams(year[0], 54)
    print template_data
    return render_to_response("archive.html", template_data, context_instance=RequestContext(request))

# Email/SMS Subscriptions
def email_subscribe(request):
    pass
def email_unsubscribe(request):
    pass
def sms_subscribe(request):
    pass
def sms_unsubscribe(request):
    pass
##############################################################################
# Auxillary Functions
##############################################################################





def get_referer_view(request, default=None):
    """
    Return the referer view of the current request
    """
    # if the user typed the url directly in the browser's address bar
    default = '/'
    referer = request.META.get('HTTP_REFERER')
    if not referer:
        return default

    # remove the protocol and split the url at the slashes
    referer = re.sub('^https?:\/\/', '', referer).split('/')
    if referer[0] != request.META.get('SERVER_NAME'):
        return default

    # add the slash at the relative path's view and finished
    referer = u'/' + u'/'.join(referer[1:])
    return referer
