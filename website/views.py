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
    during = utils.during_trivia()

    # Check to ensure team is playing this year. Otherwise, just show previous years score.
    template_data['playing'] = utils.playing_this_year(team_name)
    if template_data['playing'] is None:
        return HttpResponseServerError("No settings module?")

    scores = Score.objects.filter(team_name=team_name.upper()).order_by('-year')

    # Returns a list of dicts of form [{'year'}: int_year, ...]
    years_with_scores_dicts = scores.values('year').distinct()
    years_with_scores = []
    for year in years_with_scores_dicts:
        years_with_scores.append(year['year'])
    #print years_with_scores
    print years_with_scores
    # Show current scores
    template_data['last_hour'] = utils.get_last_hour()
    template_data['last_year'] = utils.get_last_year()

    # Data structure:
    # {2011: {'last_score': 5, 'last_place': 400, 'img': IMG_PATH_OR_NONE, 'scores': {1: SCORE, 2: SCORE, 3: SCORE...}}}

    # Score structure: {'hour': 1, 'score': 5, 'place': 400 }
    score_dict = {}
    scores = Score.objects.filter(team_name=team_name.upper())
    if len(scores) == 0:
        return HttpResponseServerError("Can't find data for team")
    for year in years_with_scores:
        year_scores = scores.filter(year=year)
        if len(year_scores) == 0:
            print "No scores found for year %d" % year
            continue
        s = {}
        for hour_score in year_scores:
            if os.path.exists(os.path.join(settings.IMAGE_DIR, "%s-%s.png" % (team_name, year))):
                img = os.path.join(settings.IMAGE_DIR, "%s-%s.png" % (team_name, year))
            else:
                img = None
            s[hour_score.hour] = {'hour': hour_score.hour, 'score': hour_score.score, 'place': hour_score.place }
        score_dict[year] = {'last_score': s[54]['score'], 'last_place': s[54]['place'], 'img': img, 'scores': s}
    #print score_dict
    template_data['scores'] = score_dict
    print score_dict
    #print template_data
    if len(scores) != 0:
        return render_to_response("team.html", template_data, context_instance=RequestContext(request))
    else:
        return HttpResponseNotFound()


def search(request):
    template_data = {}
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            print form.cleaned_data['search']
            print Score.objects.filter(team_name__icontains=form.cleaned_data['search'])
            teams = Score.objects.filter(team_name__icontains=form.cleaned_data['search']).order_by('year').values('team_name').distinct()
            if len(teams) == 0:
                messages.error(request, "No teams with that search term found. Please try again.")
                return redirect(get_referer_view(request))
            # Team list will be tuples as so: (team name, team_name (for linking to))
            team_list = []
            for team in teams:
                if team == None:
                    continue
                print "TEAM", team
                team_list.append((team['team_name'], team['team_name'].replace(' ', '_')))
            template_data['teams'] = team_list
            print template_data
            return render_to_response('search_results.html', template_data, context_instance=RequestContext(request))
        else:
            messages.error(request, "Invalid search. Please try again")
            return redirect(get_referer_view(request))

def teams_by_year(request):
    return HttpResponse("Not ready yet")

def team_name_year(request):
    return HttpResponse("Not ready yet")

def year_hour_overview(request, year, hour):
    template_data = {}
    template_data['hour'] = year
    template_data['year'] = hour
    scores = Score.objects.filter(year=year, hour=hour)
    if len(scores) == 0:
        template_data['teams'] = None
        return render_to_response('hour.html',  template_data, context_instance=RequestContext(request))
    teams = {}
    for score in scores:
        teams[score.team_name] = {'team_name': score.team_name, 'score': score.score, 'place': score.place, 'url': score.team_name.replace(' ', '_')}

    template_data['teams'] = teams
    return render_to_response('hour.html', template_data, context_instance=RequestContext(request))

def past_years(request):
    template_data = {}
    years_with_scores_dicts = Score.objects.all().values('year').distinct()
    years_with_scores = []
    for year in years_with_scores_dicts:

        years_with_scores.append(year['year'])
    print years_with_scores
    template_data['years'] = years_with_scores
    return render_to_response('past_years.html', template_data, context_instance=RequestContext(request))

def past_year_hours(request, year):
    template_data = {}
    template_data['year'] = year
    hours_with_scores_dicts = Score.objects.filter(year=year).values('hour').distinct()
    if len(hours_with_scores_dicts) == 0:
        return HttpResponseNotFound()
    hours_with_scores = []
    for hour in hours_with_scores_dicts:
        hours_with_scores.append(hour['hour'])
    print hours_with_scores
    template_data['hours'] = hours_with_scores
    return render_to_response('year_hours.html', template_data, context_instance=RequestContext(request))

##############################################################################
# Auxillary Functions
##############################################################################
def clean_number(number):
    orig_number = number.replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
    print orig_number
    if len(orig_number) != 10:
        if orig_number[0] == 1:
            return orig_number[1:]
    else:
            return orig_number

# Returns a list of tuples like so:
# (place (index + 1), team_name, score)
# Returns None on error
def get_top_ten_teams(hour, year=None):
    if year == None:
        year = utils.get_current_year()
    top_ten = []
    place = 1
    scores = Score.objects.filter(year=year).filter(hour=hour).order_by('place')[0:10]
    if len(scores) < 10:
        print "Found %d scores!" % len(scores)
        return None
    for score in scores:
        top_ten.append((place, score.team_name, score.score))
        place += 1
    return top_ten




def get_referer_view(request, default=None):
    '''
    Return the referer view of the current request

    Example:
        def some_view(request):
            ...
            referer_view = get_referer_view(request)
            return HttpResponseRedirect(referer_view, '/accounts/login/')
    '''


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
