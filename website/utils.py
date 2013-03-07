from django.db import transaction
from pygooglechart import XYLineChart
from models import Settings, Score
from django.conf import settings
import datetime, time

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
    if settings.DEBUG_DURING:
        return True

    now = datetime.datetime.now()
    start_str = "%d %s %s" % (trivia_start_hour, trivia_dates[str(now.year)], now.year)
    start = datetime.datetime.strptime(start_str, "%H %B %d %Y")
    end = start + datetime.timedelta(hours=54)

    return (start < now < end)

def get_last_hour(self):
    ''' Get last hour that scores were scraped '''
    s = Settings.objects.all()
    if len(s) == 0:
        print "No settings models!?!"
        return None
    return s[0].lasthour

def get_last_year(self):
    s = Settings.objects.all()
    if len(s) == 0:
        print "No settings models!?!"
        return None
    return s[0].lastyear

def playing_this_year(self, team_name):
    ''' Find out if team is in this years competition. '''
    playing_this_year = False
    last_hour = self.get_last_hour()
    if last_hour is None:
        return None
    last_during_score = Score.objects.filter(team_name=team_name.upper()).filter(hour=last_hour).filter(year=datetime.datetime.now().year)
    if len(last_during_score) > 0:
        playing_this_year = True
    return playing_this_year

page_template = {'2012': 'http://90fmtrivia.org/TriviaScores%s/scorePages/results%s.htm', '2011': 'http://90fmtrivia.org/TriviaScores%s/results%s.htm', '2010': 'http://90fmtrivia.org/scores_page/Scores%s/scores/results%s.htm', '2009': 'http://90fmtrivia.org/scores_page/Scores%s/results%s.htm'}
#These are the dates of Trivia, with the year being the key, and the beginning day being the data.
trivia_dates = { "2011": "April 8", "2012": "April 20", "2013": "April 19", "2014": "April 11", "2015": "April 17", "2016": "April 15" }
#Start hour in 24 hour formathttp://90fmtrivia.org/scores_page/Scores2009/results2.htm
trivia_start_hour = 18