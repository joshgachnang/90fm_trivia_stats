# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpResponseServerError
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext, Context
from website.models import Score, AvailableHours, Settings, SMSSubscriberForm, EmailSubscriberForm, EmailSubscriber, SMSSubscriber, SearchForm
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
import utils


##############################################################################
# Public Views
##############################################################################
def home(request):
    if request.method == 'GET':
        template_data = {}
        template_data['email_form'] = EmailSubscriberForm()
        template_data['sms_form'] = SMSSubscriberForm()
        template_data['latest_hour'] = utils.get_last_hour()
        template_data['latest_year'] = utils.get_last_year()
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
    # during = utils.during_trivia()

    # Check to ensure team is playing this year. Otherwise, just show previous years score.
    template_data['playing'] = utils.playing_this_year(team_name)
    template_data['last_hour'] = utils.get_last_hour()
    template_data['last_year'] = utils.get_last_year()

    template_data['scores'] = {}
    scores = Score.objects.filter(team_name=team_name.upper()).order_by('-year')
    if len(scores) == 0:
        return HttpResponseNotFound("Can't find data for team: {0}".format(team_name))
    for year in scores.values_list('year').distinct():
        year_scores = scores.filter(year=year).order_by('hour')
        template_data['scores'][year] = model_to_dict(year_scores)

    return render_to_response("team.html", template_data, context_instance=RequestContext(request))


def search(request):
    template_data = {}
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            search = form.cleaned_data['search']
            template_data['teams'] = Score.objects.filter(team_name__icontains=search).order_by('year').values_list('team_name').distinct()
        return render_to_response("search.html", template_data, context_instance=RequestContext(request))


def teams_by_year(request):
    return HttpResponse("Not ready yet")

def team_name_year(request):
    return HttpResponse("Not ready yet")

def year_hour_overview(request, year, hour):
    template_data = {}
    template_data['hour'] = year
    template_data['year'] = hour
    scores = Score.objects.filter(year=year, hour=hour)
    template_data['teams'] = {}
    for score in scores:
        template_data['teams'][score.team_name] = model_to_dict(score)
    return render_to_response('hour.html', template_data, context_instance=RequestContext(request))


##############################################################################
# Auxillary Functions
##############################################################################

# Returns a list of tuples like so:
# (place (index + 1), team_name, score)
# Returns None on error
def get_top_ten_teams(hour, year=None):
    top_ten = []
    place = 1
    if year == None:
        year = utils.get_current_year()
    scores = Score.objects.filter(year=year).filter(hour=hour).order_by('place')[0:10]
    for score in scores:
        top_ten.append({"score": score.score, "place": place, "team_name": score.team_name})
        place += 1
    return top_ten

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
