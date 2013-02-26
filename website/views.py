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
from pygooglechart import XYLineChart
from django.core.mail import send_mail
from django.template.loader import get_template
from twilio.rest import TwilioRestClient
from twilio import TwilioRestException
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.db import transaction

import boto.ses as ses
ses_conn = ses.connect_to_region('us-east-1')
from django.conf import settings


#page_template = page = "http://90fmtrivia.org/scores_page/Scores%d/scores/results%d.htm"

# Simulate during trivia
DEBUG_DURING = False

page_template = {'2012': 'http://90fmtrivia.org/TriviaScores%s/scorePages/results%s.htm', '2011': 'http://90fmtrivia.org/TriviaScores%s/results%s.htm', '2010': 'http://90fmtrivia.org/scores_page/Scores%s/scores/results%s.htm', '2009': 'http://90fmtrivia.org/scores_page/Scores%s/results%s.htm'}
#These are the dates of Trivia, with the year being the key, and the beginning day being the data.
trivia_dates = { "2011": "April 8", "2012": "April 20", "2013": "April 19", "2014": "April 11", "2015": "April 17", "2016": "April 15" }
#Start hour in 24 hour formathttp://90fmtrivia.org/scores_page/Scores2009/results2.htm
trivia_start_hour = 18


##############################################################################
# Public Views
##############################################################################
def home(request):
	if request.method == 'GET':
		template_data = {}
		template_data['email_form'] = EmailSubscriberForm()
		template_data['sms_form'] = SMSSubscriberForm()
		template_data['latest_hour'] = get_last_hour()
		template_data['latest_year'] = get_last_year()
		print "SMS: ", template_data['sms_form']
		return render_to_response("homepage.html", template_data, context_instance=RequestContext(request)) 
	
def email_subscribe(request):
	if request.method == 'POST':
		form = EmailSubscriberForm(request.POST)
		if form.is_valid():
			if form.cleaned_data.has_key('team_name'):
				team_name = form.cleaned_data['team_name'].upper()
			else:
				team_name = None
			email = form.cleaned_data['email']
			sub = EmailSubscriber(email=email, team_name=team_name)
			sub.save()
			
			# Notify of subscription
			print team_name
			c = Context({'email': email, 'team_name': team_name})
			text = get_template('subscribe_email.txt')
			text_content = text.render(c)
			html = get_template('subscribe_email.html')
			html_content = text.render(c)
			subject = "Thank you for subscribing to Trivia Stats Notification System!"
			#send_mail(subject, text_content, settings.EMAIL_FROM_ADDRESS, [email])
			msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_FROM_ADDRESS, [email])
			msg.attach_alternative(html_content, "text/html")
			msg.send()
			if  team_name:
				messages.success(request, "Email %s for team %s successfully added!" % (email, team_name))
			else:
				messages.success(request, "Email %s successfully added!" % (email))
		else:
			# TODO add message about why this doesn't work
			messages.error(request, 'Invalid Email or Team Name')
		return redirect('/')

def sms_subscribe(request):
	if request.method == 'POST':
		form = SMSSubscriberForm(request.POST)
		if form.is_valid():
			if form.cleaned_data.has_key('team_name'):
				team_name = form.cleaned_data['team_name'].upper()
			else:
				team_name = None
			number = clean_number(form.cleaned_data['phone_number'])
			if number == None:
				print "Need a phone_number!"
				return HttpResponseServerError("Invalid phone number")
			sub = SMSSubscriber(team_name=team_name, phone_number=number)
			sub.save()
			
			# Notify of subscription
			c = Context({'number': number, 'team_name': team_name})
			text = get_template('subscribe_sms.txt')
			text_content = text.render(c)
			if len(text_content) > 140:
				print "More than one message!!"
				
			client = TwilioRestClient(get_twilio_account(), get_twilio_token())
			print client
			#try:
			message = client.sms.messages.create(to=number, from_=settings.TWILIO_NUMBER, body=text_content)
			#except TwilioRestException, e:
				#pass
			if  team_name:
				messages.success(request, "Phone number %s for team %s successfully added!" % (number, team_name))
			else:
				messages.success(request, "Phone number %s successfully added!" % (number))
			return redirect('/')
		else:
			messages.error(request, 'Invalid Phone Number or Team Name')
			return redirect('/')
			
def sms_unsubscribe(request):
	if request.method == 'POST':
		form = SMSUnsubscribe(request.POST)
		if form.is_valid():
			number = clean_number(form.cleaned_data['phone_number'])
			subscriber = SMSSubscriber.objects.filter(number=number)
			if len(subscriber) != 1:
				return HttpResponseServerError("Number not subscribed")
			subscriber.delete()
			return redirect('/')
			
def email_unsubscribe(request):
	if request.method == 'POST':
		form = EmailUnsubscribe(request.POST)
		if form.is_valid():
			subscriber = EmailSubscriber.objects.filter(email=form.cleaned_data['email'])
			if len(subscriber) == 0:
				return HttpResponseServerError("Email not subscribed")
			elif len(subscriber) > 1:
				for sub in subscriber:
					sub.delete()
			else:
				subscriber.delete()
			return redirect('/')
			
def get_last_hour():
	''' Get last hour that scores were scraped '''
	s = Settings.objects.all()
	if len(s) == 0:
		print "No settings models!?!"
		return None
	return s[0].lasthour
	
def get_last_year():
	s = Settings.objects.all()
	if len(s) == 0:
		print "No settings models!?!"
		return None
	return s[0].lastyear
	
def playing_this_year(team_name):
	''' Find out if team is in this years competition. '''
	playing_this_year = False
	last_hour = get_last_hour()
	if last_hour is None:
		return None
	last_during_score = Score.objects.filter(team_name=team_name.upper()).filter(hour=last_hour).filter(year=datetime.datetime.now().year)
	if len(last_during_score) > 0:
		playing_this_year = True
	return playing_this_year
	
# Displays all the information for a team. If year is specified, only for that year.
# team_name: str
# team_year: int
def team(request, team_name, team_year=None):
	team_name = team_name.replace('_', ' ')
	template_data = {}
	template_data['team_name'] = team_name.upper()
	template_data['year'] = team_year
	during = during_trivia()
	
	# Check to ensure team is playing this year. Otherwise, just show previous years score.
	template_data['playing'] = playing_this_year(team_name)
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
	template_data['last_hour'] = get_last_hour()
	template_data['last_year'] = get_last_year()
	
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
	#if len(score) > 1:
		#return HttpResponseServerError("More than one score for this hour..Something's wrong!")
	#template_data['score'] = score.score
	#template_data['place'] = score.place
	#template_data['last_hour'] = get_last_hour()
	#if os.path.exists(os.path.join(settings.IMAGE_DIR, "%s-%s.png" % (team_name, template_data['year']))):
		#template_data['img']
		
	#if playing_this_year:
		#template_data['hour'] = get_last_hour()
		#print get_last_hour()
		#score = Score.objects.filter(team_name=team_name.upper()).filter(year=get_last_year()).filter(hour=template_data['hour'])
		#if len(score) == 0:
			#return HttpResponseServerError("Can't find data for team")
		#if len(score) > 1:
			#return HttpResponseServerError("More than one score for this hour..Something's wrong!")
		#template_data['score'] = score.score
		#template_data['place'] = score.place
		#template_data['last_hour'] = last_hour
		
	## Show last score
	#elif not playing_this_year and not team_year:
		#last_year = years_with_scores[0]
		#template_data['last_year'] = last_year
		
		#last_score = Score.objects.order_by('-year').filter(team_name=team_name.upper()).filter(year=last_year).order_by('-hour')[0]
		#template_data['score'] = last_score.score
		#template_data['place'] = last_score.place
		
		#if os.path.exists(os.path.join(settings.IMAGE_DIR, "%s-%s.png" % (team_name, year['year']))):
			#for img in os.listdir(os.path.join(settings.IMAGE_DIR, team_name)):
				#if img[:-4] != '.png':
					#print "Unknown file: ", img
					#continue
				## Images are of format "team_name-year.png"
				#if str(year['year']) in img:
					## Still need to do {{ static_path }}{{ img }}
					#template_data['img'] = "team_imgs/%s/%s" % (team_name, img)
					#print template_data['img']
		
	# not playing, team_year != None
	#else:
		#scores = Score.objects.filter(team_name=team_name.upper()).filter(year=team_year)
		#if len(scores) == 0:
			#return HttpResponseNotFound()
		
		#if os.path.exists(os.path.join(settings.IMAGE_DIR, team_name)):
			#for img in os.listdir(os.path.join(settings.IMAGE_DIR, team_name)):
				#if str(team_year) == img[-8:-4]:
						#template_data['imgs'][team_year] = img[-8:-4]
		
	
		
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
			
def get_twilio_account():
	return private_config.TWILIO_ACCOUNT
	#try:
		#with open('/etc/twilio-account.txt', 'r') as f:
			#account = f.readline().strip()
			#if account is not None:
				#print account
				#return account
	#except OSError, e:
		#pass
	#except IOError, e:
		#pass
	#if os.environ.has_key('TWILIO_ACCOUNT'):
		#return os.environ['TWILIO_ACCOUNT']
	#else:
		#try:
			#return settings.TWILIO_ACCOUNT
		#except AttributeError, e:
			#return HttpResponseServerError("Couldn't send texts through Twilio")
	#return HttpResponseServerError("Couldn't send texts through Twilio")

		
def get_twilio_token():
	return private_config.TWILIO_AUTH
	#try:
		#with open('/etc/twilio-token.txt', 'r') as f:
			#account = f.readline().strip()
			#if account is not None:
				#print account
				#return account
	#except OSError, e:
		#pass
	#except IOError, e:
		#pass
	#if os.environ.has_key('TWILIO_TOKEN'):
		#return os.environ['TWILIO_TOKEN']
	#else:
		#try:
			#return settings.TWILIO_TOKEN
		#except AttributeError, e:
			#return HttpResponseServerError("Couldn't send texts through Twilio")
	#return HttpResponseServerError("Couldn't send texts through Twilio")

def email_notify( hour=None):
	if hour is None:
		hour = get_current_hour()
	for user in EmailSubscriber.objects.all():
		if user.team_name:
			score = Score.objects.filter(hour=hour).filter(team_name=team_name)
			if len(score) != 1:
				print "Failed email notify for hour %d for team name %s" % (int(hour), team_name)
				continue
			else:
				try:
					send_mail('Trivia Scores Updated for Hour %d. %s is in %d place with %d points.' % (get_current_hour(), score.team_name, score.place, score.score), 'Trivia scores for Hour %d have been posted. %s is in %d place with %d points. You can check your current stats at <a href="http://triviastats.com">TriviaStats.com</a>' % (get_current_hour(), score.team_name, score.place, score.score), 'noreply@triviastats.com', user.email, fail_silently=False)
				except smtplib.SMTPException, e:
					print "Emailing for user %s failed." % user
					print e
		else:
			try:
				send_mail('Trivia Scores Updated for Hour %d' % get_current_hour(), 'Trivia scores for Hour %d have been posted. You can check your current stats at <a href="http://triviastats.com">TriviaStats.com</a>' % get_current_hour(), 'noreply@triviastats.com', user.email, fail_silently=False)
			except smtplib.SMTPException, e:
				print "Emailing for user %s failed." % user
				print e

def sms_notify( hour=None):
	account = get_twilio_account()
	token = get_twilio_token()
	from_number = get_twilio_number()
	
	if account is None or token is None or from_number is None:
		print "Missing token, account, or from_number"
		
	client = TwilioRestClient(account, token)
	if client is None:
		print "Client failed."
		
	if hour is None:
		hour = get_current_hour()
	for user in SMSSubscriber.objects.all():
		if user.team_name:
			score = Score.objects.filter(hour=hour).filter(team_name=team_name)
			if len(score) != 1:
				print "Failed sms notify for hour %d for team name %s, %d scores found.." % (int(hour), team_name, len(score))
				continue
			else:
				try:
					# Max length of team name is 36
					# 88 in characters (including spaces), 2 for hour, 3 for place, 5 for points = 134 max characters.
					client.sms.messages.create(to=score.phone_number, from_=from_number, body="Trivia Scores for Hour %d. %s in %d place with %d points. Check scores at http://triviastats.com." % (hour, score.team_name, score.place, score.score))
					#send_mail('Trivia Scores Updated for Hour %d. %s is in %d place with %d points.' % (get_current_hour(), score.team_name, score.place, score.score), 'Trivia scores for Hour %d have been posted. %s is in %d place with %d points. You can check your current stats at <a href="http://triviastats.com">TriviaStats.com</a>' % (get_current_hour(), score.team_name, score.place, score.score), 'noreply@triviastats.com', user.email, fail_silently=False)
				except TwilioRestException, e:
					print "SMS for user %s failed." % (user, )
					print e
		else:
			try:
				# Max length of team name is 36
				client.sms.messages.create(to=score.phone_number, from_=from_number, body="Trivia Scores for Hour %d. Check scores at http://triviastats.com." % (hour, ))
				#send_mail('Trivia Scores Updated for Hour %d' % get_current_hour(), 'Trivia scores for Hour %d have been posted. You can check your current stats at <a href="http://triviastats.com">TriviaStats.com</a>' % get_current_hour(), 'noreply@triviastats.com', user.email, fail_silently=False)
			except TwilioRestException, e:
				print "SMS for user %s failed." % user
				print e
	
	
def teams_by_year(request): 
	return HttpResponse("Not ready yet")

def team_name_year(request):
	return HttpResponse("Not ready yet")

def send_email(subscriber):
	last_hour = get_last_hour()
	top_ten = get_top_ten_teams(Settings.objects.all()[0].lasthour)
	print top_ten
	if subscriber is None:
		return
		
	if subscriber.team_name:
		score = Score.objects.filter(team_name=subscriber.team_name).filter(hour=last_hour)
		if score is None:
			print "Couldn't find score for Hour %d for Team %s", (last_hour, subscriber.team_name)
	else:
		print "No team name. Continuing."
	if score:
		subject = "Trivia Scores Updated for Hour %d. %s is in %d place with %d points." % (last_hour, subscriber.team_name, score.place, score.score)
		text_body = "Trivia scores for Hour %d have been posted. %s is in %d place with %d points. You can check your current stats at TriviaStats.com" % (last_hour, subscriber.team_name, score.place, score.score)
		html_body = "Trivia scores for Hour %d have been posted. %s is in %d place with %d points. You can check your current stats at <a href='http://triviastats.com'>TriviaStats.com</a>" % (last_hour, subscriber.team_name, score.place, score.score)
	else:
		subject = "Trivia Scores Updated for Hour %d." % (last_hour, )
		text_body = "Trivia scores for Hour %d have been posted. You can check your current stats at TriviaStats.com" % (last_hour, )
		html_body = "Trivia scores for Hour %d have been posted. You can check your current stats at <a href='http://triviastats.com'>TriviaStats.com</a>" % (last_hour, )
	ses_conn.send_email(source="TriviaStats@triviastats.com", subject=subject, body=html_body, to_addresses=(subscriber.email, ), format='html',)
	
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
# CLI Functions
##############################################################################

# During Trivia, scrapes each minute to see if a new page is up yet.
def scraper():
	if during_trivia:
		#Scrape for new hours
		scrape_prev(get_current_year())
	else:
		return HttpResponse("Not during Trivia")

# Utility function for scraping a year. Useful for setting up database with previous years.
def scrape_prev(year):
	if year is None:
		print "Year is None."
		return
	s = []
	for hr in range(1, 55):
		success = scrape_year_hour(year, hr)
		if success:
			s.append(hr)
	if len(s) > 0:
	    sms_notify(s[-1])
	    email_notify(s[-1])
	  
	print "Success for hours: ", s
	
def spa():
	for i in range(2009, 2012):
		scrape_prev(i)

##############################################################################
# Auxillary Functions
##############################################################################
def email_update():
	for sub in EmailSubscriber.objects.all():
		if sub.email == None:
			print "Invalid email for ", sub
			continue
		
		send_email(sub)
		#c = Context({'email': email, 'team_name': team_name, 'top_ten': top_ten})
		#subject = "Trivia Stats: Hour %d, %d Have Been Posted" % (Settings.objects.all()[0].last_hour, get_current_year(),)
		#html_content = render_to_string('update_email.html', c)
		#text_content = strip_tags(html_content)
		#msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_FROM_ADDRESS, [email])
		#msg.attach_alternative(html_content, "text/html")
		#msg.send()
			
def sms_update():
	hour = get_last_hour()
	for sub in SMSSubscriber.objects.all():
		if sub.phone_number == None:
			continue
		score = None
		if sub.team_name:
			
			try:
				score = Score.objects.filter(team_name=sub.team_name.upper().get(hour=get_last_hour()))
			except Exception, e:
				print e
				print "Team name doesn't exist or has too many returned..", sub.phone_number, sub.team_name
		if score:
			text_content = "%s Score: %d Place: %d. See more at TriviaStats.com/hour/%d" % (sub.team_name, score.score, score.place, hour)
		else:
			text_content = "Trivia Stats: Scores for Hour %d have been updated. See them at TriviaStats.com/hour/%d" % (hour, hour)
		client = TwilioRestClient(settings.TWILIO_ACCOUNT, settings.TWILIO_AUTH)
		message = client.sms.messages.create(to=sub.phone_number, from_=settings.TWILIO_NUMBER, body=text_content)
		print 'message sent to user'
		
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
		year = get_current_year()
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
	

def scrape_year_hour(yr, hr, force=False):
    #Add check right here to see if data already exists for the given year/hour
	query = Score.objects.filter(year=int(yr)).filter(hour=int(hr))
	if len(query) != 0:
		#print len(query)
		for s in query:
			print s
		print "Already in DB"
		return False
		
	# Trivia has a discrepancy between 02 and 2 for hours..
	if int(hr) < 10:
		if int(yr) >= 2010:
			# Add 0 to the front
			hr = "0%d" % hr
	page = page_template[str(yr)] % (str(yr), str(hr))
	print page
	try:
		p = urllib2.urlopen(page)
	except urllib2.HTTPError, e:
		print("No data for this hour (yet?)")
		return False
		
	soup = BeautifulSoup(''.join(p.read()))
	p.close()

	teams = soup.findAll('dd')
	place_score = soup.findAll('dt')

	db = []
	# Drop all teams into a list of lists:
	# 0: Team name 1: Place 2: Points
	for i in range(0, len(teams)):
		if len(place_score[i].contents) == 1:
			reg = re.findall(r'([0-9]+)', place_score[i].contents[0].replace(',', ''))
		# Happens in first occurence only
		elif len(place_score[i].contents) == 2:
			reg = re.findall(r'[0-9]{1,6}', place_score[i].contents[1].replace(',', ''))
		else:
			# Broken..
			pass
	
		place = reg[0]
		score = reg[1]
		# Generate teams list
		teams_list = teams[i].findAll('li')

		for j in range(0, len(teams_list)):
			# Isn't this uggggggggly?
			# Creates a list, with format noted above first for loop. 
			# Replaces ugly HTML with chars.
			#db.append( (teams_list[j].string.replace('&#160;', ' ').replace('&amp;', '&').replace('&quot;', '"').replace('&nbsp;', ' '), score, place) ) 
			db.append( (teams_list[j].string.replace('&#160;', ' ').replace('&amp;', '&').replace('&quot;', '"').replace('&nbsp;', ' '), int(yr), int(hr),  place, score,) ) 
	insert_bulk(db)
	return True
	#score_objects = []
	#for a in db:
		#print a[0] + " " + a[1] + " " + a[2]
		##print "<br/>"
		#score = Score(team_name = a[0].replace(" ", "_"), hour = int(hr), year = int(yr), score = int(a[1]), place = int(a[2]))
		#score_objects.append(score)
		##score.save()
	##print score_objects
	##insert_many(score_objects)
	##create_in_bulk(score_objects)
	#return True
@transaction.commit_manually
def insert_bulk(values):
	from django.db import connection, transaction
	print "BULK", values[0]
	cursor = connection.cursor()
	
	query = ''' INSERT INTO stats_score
				(team_name, year, hour, place, score)
				VALUES (%s,%s,%s,%s,%s) '''
				
	print cursor.executemany(query,values)
	transaction.commit()
	#transaction.commit_unless_managed()
	#cursor.execute("COMMIT")
        
# Generates a line chart of score over the hours of a year from Google Chart API, downloads it, and saves it to the img directory
# Check for info: https://github.com/gak/pygooglechart/blob/master/pygooglechart.py
def get_chart_place(team_name, year):
	# TODO add caching
	scores = Score.objects.filter(team_name=team_name.upper()).filter(year=year).order_by('hour')
	if len(scores) == 0:
		return None
	chart = XYLineChart(settings.CHART_WIDTH, settings.CHART_HEIGHT)
	x, y = [], []
	for score in scores:
		x.append(score.hour)
		y.append(score.place)
	chart.add_data(x)
	chart.add_data(y)
	chart.set_title("%s %d" % (team_name.upper(), int(year)))
	chart.download("%s.png" % team_name)

# Generates a bar chart of score gained each (group of) hour(s) of a year from Google Chart API, downloads it, and saves it to the img directory
def get_chart_score(team_name, year):
	# TODO add caching
	scores = Score.objects.filter(team_name=team_name.upper()).filter(year=year).order_by('hour')
	if len(scores) == 0:
		return None
	chart = XYLineChart(settings.CHART_WIDTH, settings.CHART_HEIGHT)
	x, y = [], []
	for score in scores:
		x.append(score.hour)
		y.append(score.place)
	chart.add_data(x)
	chart.add_data(y)
	chart.set_title("%s - %d" % (team_name, int(year)))
	chart.download("%s.png" % team_name)
	
def get_current_hour():
	if not during_trivia():
		return None
	
	now = datetime.datetime.now()
	start_str = "%d %s %s" % (trivia_start_hour, trivia_dates[str(now.year)], now.year)
	start = datetime.datetime.strptime(start_str, "%H %B %d %Y")
	
	diff = now - start
	return diff.days * 24 + diff.seconds / 3600
	
	
	year = datetime.date.today().year
	trivia_start_date = trivia_dates[str(year)]
	a = str(trivia_start_date) + " " + str(year) + " " + str(trivia_start_hour)
	time.strptime(a, "%B %d %Y %H")

def get_current_year():
	return datetime.datetime.now().year
	
# Check 
def during_trivia():
	# Simple debugging stuff
	if DEBUG_DURING:
		return True
		
	now = datetime.datetime.now()
	start_str = "%d %s %s" % (trivia_start_hour, trivia_dates[str(now.year)], now.year)
	start = datetime.datetime.strptime(start_str, "%H %B %d %Y")
	end = start + datetime.timedelta(hours=54)
	
	return (start < now < end)

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

# Convenience wrapper..and a way avoid reimporting matplotlib 400 times per hour.
#def plot_all_teams():
	##import matplotlib.pyplot as plt
	##for team in 

# Takes a team name and year, grabs all their scores for that year, and saves an image. Do not call this except through plot_all_teams!!
#def _plot_team(team, year):
	## Just in case someone ignores the above comment about not calling this through plot_all_teams..
	## And for testing!
	##if "matplotlib" not in sys.modules:
	#import matplotlib.pyplot as plt
	## Ensure 4 digit number between 1990 and 2100...for future proofing..
	#if int(year) < 1990 or int(year) > 2100:
		#print "Year %s not in correct format" % year
		#return False
	#scores = Score.objects.filter(team_name=team.upper())
	#if len(scores) == 0:
		#print "No scores found"
		#return False
	#x, y = [], []
	##plt.xlabel('Hour')
	##plt.ylabel('Score')
	#for score in scores:
		##print score.hour, score.place
		#x.append(score.hour)
		#y.append(score.place)
	#print len(x), x
	#print len(y), y
	#plt.plot(x, y)
	#ax = plt.gca()
	#ax.set_ylim(ax.get_ylim()[::-1])
	#plt.savefig('%s-%s.png' % (score.team_name.upper(), str(year)))
	#plt.close()
	
# Additional testing.
