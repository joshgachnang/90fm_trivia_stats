import re

from BeautifulSoup import BeautifulStoneSoup, BeautifulSoup
import urllib

# REGEX
# b = re.findall(r'\d+',a)
# place = b[0]
# points = b[1]

page = "http://90fmtrivia.org/scores_page/Scores2010/scores/results54.htm"

p = urllib.urlopen(page)
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
    points = reg[1]
    # Generate teams list
    teams_list = teams[i].findAll('li')

    for j in range(0, len(teams_list)):
        # Isn't this uggggggggly?
        # Creates a list, with format noted above first for loop.
        # Replaces ugly HTML with chars.
        db.append(
            (teams_list[j].string.replace('&#160;', ' ').replace('&amp;', '&').replace('&quot;', '"'), points, place))

for a in db:
    print a[0] + " " + a[1] + " " + a[2]

# def getURL(int year, int hour):
#  return "http://90fmtrivia.org/scores_page/Scores%d/scores/results%d.htm" % (year, hour)
