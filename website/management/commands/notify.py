from django.core.management.base import BaseCommand, CommandError
from website.models import Scraper, TwilioManager, EmailSubscriber, EmailManager, SMSSubscriber
from optparse import make_option

class Command(BaseCommand):
    can_import_settings = True
    option_list = BaseCommand.option_list + (
        make_option('--sms', action="store_true", dest="sms", help="Sends out SMS notifications"),
        make_option('--email', action="store_true", dest="email", help="Sends out Email notifications"),
    )
    args = '<--force year hour> '
    help = 'Forces resending notifications.'

    def handle(self, *args, **options):
        if options['sms']:
            tm = TwilioManager()
            tm.sms_notify()
        if options['email']:
            em = EmailManager()
            em.email_notify()