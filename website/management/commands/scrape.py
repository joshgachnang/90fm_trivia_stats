
from django.core.management.base import BaseCommand
from website.models import Scraper


class Command(BaseCommand):
    can_import_settings = True

    def handle(self, *args, **options):
        scraper = Scraper()
        scraper.scrape()
