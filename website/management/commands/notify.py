from django.core.management.base import BaseCommand, CommandError
from website.models import Scraper, TwilioManager, EmailSubscriber, EmailManager, SMSSubscriber
from optparse import make_option

class Command(BaseCommand):
    can_import_settings = True
    option_list = BaseCommand.option_list + (
        make_option('--sms', action="store_true", dest="sms", help="Sends out SMS notifications"),
        make_option('--email', action="store_true", dest="email", help="Sends out Email notifications"),
        make_option('--debug', action="store_true", dest="debug", default=False, help="Debugging"),
    )
    args = '<--force year hour> '
    help = 'Forces resending notifications.'

    def handle(self, *args, **options):

        if options['sms']:
            tm = TwilioManager()
            tm.sms_notify(debug=options['debug'])
            print "Sent SMS."
        if options['email']:
            em = EmailManager()
            print options['debug']
            em.email_notify(debug=options['debug'])
            print "Sent emails."