90fm_trivia_stats
=================

Statistics scraping for the World's Largest Trivia Contest held in Stevens Point, WI ever year. Written in Python using the Django framework.

Copyright 2013 Josh Gachnang. Released under the GPLv3 Open Source License.

Running
-------

Requires MySQL 5.6 or MyISAM to support full text search

You can add a full text search with the command:

    "ALTER TABLE website_score ADD FULLTEXT INDEX `FullText` (`team_name` ASC);"

Using the API
-------------

The Trivia Stats API can be found at https://api.triviastats.com/api/v1/.

## /api/v1/scores/

The list of scores for all teams, all years.

You can use a couple different query parameters to filter results for scores.

For example:

'/api/v1/scores/?search=wii&year=2014&ordering=-hour' will get all scores
for the team 'WII CAME IN LIKE A WRECKIN BALL' in 2014 in reverse order.

### Valid query params:

#### Filter

Filter fields in the results, valid arguments are 'team_name' (case insensitive, needs to be a URL
encoded exact match), 'hour', and 'year'

    ?team_name=TIN%20MAN

Filters can be chained:

    ?team_name=TIN%20MAN&year=2013

#### Search

Does a full text search on 'team_name', case insensitive.

    ?search=network  # Get all teams with 'network' in their name

#### Ordering

Orders results, valid arguments are 'score', 'place', 'year', and 'hour'. These can
be combined.

    ?ordering=-hour  # Sort results by hour in descending order, with hour 54

Ordering can be chained:

    ? ordering=-year,-hour  # Sort results by year in descending order, with the latest year first, then by hour in descending order
