from optparse import make_option

from django.core.management.base import BaseCommand
from website.models import Scraper


class Command(BaseCommand):
    can_import_settings = True
    option_list = BaseCommand.option_list + (
        make_option('--year', action="store", type="int", dest="year",
                    help="Year to scrape"),
        make_option('--hour', action="store", type="int", dest="hour",
                    help="Hour to scrape"),
        make_option('--force', action="store_true", dest="force",
                    help="Hour to scrape"),
    )
    args = '<--year year> <--hour hour>'
    help = 'Scrapes 90FM Trivia website, optionally limited to a year/hour'

    def handle(self, *args, **options):
        if 'year' in options and options['year']:
            year = options['year']
        else:
            year = 2012
        if 'hour' in options and options['hour']:
            hour = options['hour']
        else:
            hour = None
        if 'force' in options and options['force']:
            force = options['force']
        else:
            force = False
        scraper = Scraper()
        scraper.scrape_prev(year, hour=hour, force=force)
