import logging
import random
import string
import urllib2

import datetime
import time
import re
from BeautifulSoup import BeautifulSoup
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import models
from django.template import Context
from django.template.loader import get_template
from rest_framework import serializers
from twilio.rest import TwilioRestClient
from twilio import TwilioRestException
import twitter

logger = logging.getLogger('django')

# Cache client
_twilio_client = None


def random_code():
    return ''.join(random.choice(string.ascii_uppercase + string.digits)
                   for _ in range(8))


class Subscriber(models.Model):
    phone_number = models.CharField(max_length=14, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    team_name = models.CharField(max_length=64, default=None, blank=True,
                                 null=True)
    error_msg = models.TextField()
    # Use this code to confirm deletion.
    delete_code = models.CharField(max_length=8, blank=True, null=True,
                                   default=random_code)

    def save(self, *args, **kwargs):
        if not self.id:
            # New subscriber, send welcome
            logger.info('New subscriber: Team: {}, {}, {}'.format(
                self.team_name, self.phone_number, self.email))
            if self.phone_number:
                self.welcome_text()
            if self.email:
                self.welcome_email()
        super(Subscriber, self).save(*args, **kwargs)

    def score_update(self, hour, year):
        # Find team
        scores = Score.objects.filter(hour=hour).filter(year=year).filter(
            team_name__contains=self.team_name)
        if len(scores) > 1:
            logger.warning('Team name {} generated {} duplicates'.format(
                self.team_name, len(scores)))
            msg = ('Your team name {} matched multiple teams, '
                   'try being more specific. Matched teams: {}'.format(
                [score.team_name for score in scores]))
            self.error_msg = msg
            self.save()
            logger.warning(msg)
            # Select the first score
            score = scores[0]

        elif len(scores) == 0:
            msg = ('Your team name {} didn\'t match any teams.'.format(
                self.team_name))
            self.error_msg = msg
            self.save()
            logger.warning(msg)
            score = None
        else:
            score = scores[0]

        if self.contact_method in ('text', 'both'):
            self.score_text(score)

        if self.contact_method in ('email', 'both'):
            self.score_email(score)

    def score_text(self, score):
        logger.info(
            "Sending SMS to {}, {}".format(self.phone_number, self.team_name))
        client = _get_twilio_client()

        template = get_template('sms_score_update.txt')
        context = Context({'hour': score.hour, 'place': score.place,
                           'team_name': score.team_name,
                           'score': score.score})
        body = template.render(context)

        try:
            client.sms.messages.create(
                to=self.phone_number,
                from_=settings.TWILIO_NUMBER,
                body=body)
        except TwilioRestException:
            logger.exception(
                "SMS for user {0} failed.".format(self.user.username))

    def score_email(self, score):
        logger.info(
            "Sending SMS to {}, {}".format(self.phone_number, self.team_name))

        template = get_template('email_score_update.txt')
        html_template = get_template('email_score_update.html')
        context = Context({'hour': score.hour, 'place': score.place,
                           'team_name': score.team_name,
                           'score': score.score})
        body = template.render(context)
        html_body = html_template.render(context)
        subject = "TriviaStats Score Update For Hour {hour}: {team} is in "
        try:
            send_mail(subject, body, settings.FROM_EMAIL, [self.email],
                      html_message=html_body)
        except Exception:
            logger.exception(
                "Email for user {0} failed.".format(self.user.username))

    def welcome_text(self):
        c = Context({'number': self.phone_number,
                     'team_name': self.team_name})
        text = get_template('subscribe_sms.txt')
        logger.info('Sending welcome text to {}'.format(self.phone_number))
        _send_text(self.phone_number, text.render(c))

    def welcome_email(self):
        c = Context({'email': self.email,
                     'team_name': self.team_name})
        text = get_template('subscribe_email.txt')
        logger.info('Sending welcome email to {}'.format(self.email))
        _send_email(self.email, 'Welcome to TriviaStats!', text.render(c))

    def __str__(self):
        return "{}: {}, {}".format(self.team_name, self.phone_number,
                                   self.email)

    def __repr__(self):
        return self.__str__()


class SubscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscriber
        fields = ['id', 'email', 'phone_number', 'team_name']


class TeamListSerializer(serializers.Serializer):
    team_name = serializers.CharField(max_length=255)


class Score(models.Model):
    # This should be team_name for consistency..
    team_name = models.CharField(max_length=255, db_index=True)
    year = models.IntegerField()
    hour = models.IntegerField(db_index=True)
    place = models.IntegerField(db_index=True)
    score = models.IntegerField(db_index=True)

    def url(self):
        return self.team_name.replace(' ', '_')

    def __unicode__(self):
        return 'Team: {}, {} Hour {}'.format(
            self.team_name, self.year, self.hour)


    class Meta:
        unique_together = ("team_name", "hour", "year")


class ScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Score


class Scraper(object):
    # During Trivia, scrapes each minute to see if a new page is up yet.
    def scrape(self):
        """Scrape for the next hour."""
        if not during_trivia():
            logger.info('Not during trivia, not scraping')
            return

        # Scrape remaining hours until we find the next one
        for hour in remaining_hours():
            if self.scrape_year_hour(current_year(), hour):
                post_to_twitter("Hour {0} scores posted!".format(hour))
                return
        logger.info('No new hours.')

    def get_page(self, year, hour):
        if year <= 2012:
            page = page_template[str(year)] % (str(year), str(hour))
        else:
            page = page_template[str(year)] % (str(year))
        logger.info("Getting page: {0}".format(page))
        try:
            return urllib2.urlopen(page)
        except urllib2.HTTPError:
            # If hour 54, might need to use a special page for previous years.
            logger.info(
                "Checking for hour 54 page. year: {0}, hour: {1}".format(year,
                                                                         hour))
            logger.info("Hour 54 Finals: ", hour_54_page)
            if str(year) in hour_54_page and hour == 54:
                try:
                    page = hour_54_page[str(year)]
                    return urllib2.urlopen(page)
                except urllib2.HTTPError:
                    logger.error("Can't scrape either page 54 or final page.")
                    return False
            else:
                logger.info("No data for this hour (yet?): {0}".format(hour))
                return False

    def scrape_year_hour(self, year, hour, force=False):
        p = self.get_page(year, hour)
        if not p:
            return False

        soup = BeautifulSoup(''.join(p.read()))
        p.close()

        teams = soup.findAll('dd')
        place_score = soup.findAll('dt')
        hour = soup.findAll('h1')[0]
        hour = " ".join(hour.string.split()[5:])
        hour = text2int(hour.lower())

        query = Score.objects.filter(year=int(year)).filter(hour=int(hour))
        if len(query) != 0 and force is False:
            logger.info("Already in DB")
            return False

        bulk_list = []
        for team, score in zip(teams, place_score):
            bulk_list += self.build_team_score(team, score, year, hour)
        Score.objects.bulk_create(bulk_list)

        return True

    def build_team_score(self, team, score, year, hour):
        if len(score.contents) == 1:
            reg = re.findall(r'([0-9]+)',
                             score.contents[0].replace(',', ''))
            # Happens in first occurence only
        elif len(score.contents) == 2:
            reg = re.findall(r'[0-9]{1,6}',
                             score.contents[1].replace(',', ''))
        else:
            # Broken..
            return []

        place = reg[0]
        score = reg[1]

        scores = []
        for team in team.findAll('li'):
            name = sanitize_team_name(team.string)

            year = int(year)

            scores.append(
                Score(team_name=name, year=year, hour=hour, place=place,
                      score=score))
        return scores


def _get_twilio_client():
    global _twilio_client
    if _twilio_client is None:
        account = settings.TWILIO_ACCOUNT
        token = settings.TWILIO_AUTH
        _twilio_client = TwilioRestClient(account, token)

    return _twilio_client


def clean_number(number):
    return number.replace('(', '').replace(')', '').replace('-', '').replace(
        ' ', '')


def _send_text(number, msg):
    client = _get_twilio_client()
    try:
        client.sms.messages.create(
            to=number,
            from_=settings.TWILIO_NUMBER,
            body=msg)
    except TwilioRestException:
        logger.exception(
            "SMS {} for user {} failed.".format(msg, number))


def _send_email(email, subject, msg):
    send_mail(subject, msg, settings.FROM_EMAIL, [email])


def notify(year, hour):
    pass


def sanitize_team_name(name):
    return (name.replace('&#160;', ' ')
            .replace('&amp;', '&')
            .replace('&quot;', '"')
            .replace('&nbsp;', ' '))


def text2int(textnum, numwords=None):
    if not numwords:
        numwords = {}
        units = [
            "zero", "one", "two", "thouree", "four", "five", "six", "seven",
            "eight",
            "nine", "ten", "eleven", "twelve", "thirteen", "fourteen",
            "fifteen",
            "sixteen", "seventeen", "eighteen", "nineteen",
        ]

        tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty",
                "seventy", "eighty", "ninety"]

        scales = ["hundred", "thousand", "million", "billion", "trillion"]

        numwords["and"] = (1, 0)
        for idx, word in enumerate(units):
            numwords[word] = (1, idx)
        for idx, word in enumerate(tens):
            numwords[word] = (1, idx * 10)
        for idx, word in enumerate(scales):
            numwords[word] = (10 ** (idx * 3 or 2), 0)

    current = result = 0
    for word in textnum.split():
        if word not in numwords:
            raise Exception("Illegal word: " + word)

        scale, increment = numwords[word]
        current = current * scale + increment
        if scale > 100:
            result += current
            current = 0

    return result + current


def get_current_hour():
    if not during_trivia():
        return None

    now = datetime.datetime.now()
    start_str = "%d %s %s" % (
        trivia_start_hour, trivia_dates[str(now.year)], now.year)
    start = datetime.datetime.strptime(start_str, "%H %B %d %Y")

    diff = now - start
    return diff.days * 24 + diff.seconds / 3600


def current_year():
    return datetime.datetime.now().year


def during_trivia():
    now = datetime.datetime.now()
    return start_time() < now < end_time()


def last_hour():
    """Get last hour that scores were scraped"""
    return Score.objects.filter(year=last_year()).values_list(
        'hour',
        flat=True).distinct().order_by(
        '-hour')[0]


def last_year():
    return Score.objects.values_list('year', flat=True).distinct().order_by(
        '-year')[0]


def start_time():
    now = datetime.datetime.now()
    return "%d %s %s" % (
        trivia_start_hour, trivia_dates[str(now.year)], now.year)


def end_time():
    return start_time() + datetime.timedelta(hours=54)


def post_to_twitter(message):
    auth = twitter.OAuth(settings.TWITTER_TOKEN, settings.TWITTER_TOKEN_SECRET,
                         settings.TWITTER_CONSUMER_KEY,
                         settings.TWITTER_CONSUMER_SECRET)
    t = twitter.Twitter(auth=auth)
    t.account.verify_credentials()
    if settings.DEBUG:
        # Don't tweet in dev.
        logger.info("Would tweet message: {0}".format(message))
    else:
        logger.info(t.statuses.update(status=message))


def pad_hour(hour, year):
    if int(hour) < 10 and int(year) >= 2010:
        # Add 0 to the front
        return "0%d" % hour
    else:
        return str(hour)


def remaining_hours():
    year = current_year()
    return [pad_hour(hour, year) for hour in range(last_hour() + 1, 54)]


page_template = {
    '2015': 'http://90fmtrivia.org/TriviaScores%s/scorePages/results.html',
    '2014': 'http://90fmtrivia.org/TriviaScores%s/scorePages/results.html',
    '2013': 'http://90fmtrivia.org/TriviaScores%s/scorePages/results.htm',
    '2012': 'http://90fmtrivia.org/TriviaScores%s/scorePages/results%s.htm',
    '2011': 'http://90fmtrivia.org/TriviaScores%s/results%s.htm',
    '2010': 'http://90fmtrivia.org/scores_page/Scores%s/scores/results%s.htm',
    '2009': 'http://90fmtrivia.org/scores_page/Scores%s/results%s.htm'}

hour_54_page = {
    '2012': 'http://90fmtrivia.org/TriviaScores2012/scorePages/results.htm'}

# These are the dates of Trivia, with the year being the key, and the
# beginning day being the value.
trivia_dates = {"2011": "April 8", "2012": "April 20", "2013": "April 19",
                "2014": "April 11", "2015": "April 17",
                "2016": "April 15"}
# Start hour in 24 hour format http://90fmtrivia.org/scores_page/Scores2009
# /results2.htm
trivia_start_hour = 1876
