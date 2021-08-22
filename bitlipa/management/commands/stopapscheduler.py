from django.core.management.base import BaseCommand


from bitlipa.utils.logger import logger


class Command(BaseCommand):
    help = "Stops APScheduler."

    def handle(self, *args, **options):
        logger('Stopping scheduler...', 'info')
        with open('apscheduler.log', 'w+') as f:
            f.write('stopped')
            f.close()
        logger('Scheduler shut down successfully!', 'info')
