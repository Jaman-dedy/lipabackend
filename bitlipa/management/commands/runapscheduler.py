import time
from django.conf import settings
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util

from bitlipa.utils.logger import logger
from bitlipa.apps.currency_exchange.tasks import update_exchange_rates


# The `close_old_connections` decorator ensures that database connections, that have become
# unusable or are obsolete, are closed before and after our job has run.
@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    """
    This job deletes APScheduler job execution entries older than `max_age` from the database.
    It helps to prevent the database from filling up with old historical records that are no
    longer useful.

    :param max_age: The maximum length of time to retain historical job execution records.
                    Defaults to 7 days.
    """
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


def stop_apscheduler(scheduler):
    logger('Stopping scheduler...', 'info')
    scheduler.shutdown()
    logger('Scheduler shut down successfully!', 'info')


def is_apscheduler_running(scheduler) -> bool:
    is_running = False
    with open('apscheduler.log', 'r') as f:
        for line in f:
            is_running = line == 'running'
            break
        f.close()
    if is_running is False and scheduler:
        stop_apscheduler(scheduler)
    return is_running


class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # update_exchange_rates
        scheduler.add_job(
            update_exchange_rates,
            trigger=CronTrigger(hour="*/1"),
            id="update_exchange_rates",
            max_instances=1,
            replace_existing=True,
        )

        # delete_old_job_executions
        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(day_of_week="mon", hour="00", minute="00"),  # Midnight on Monday, before start of the next work week.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        try:
            logger('Starting scheduler...', 'info')
            scheduler.start()
            with open('apscheduler.log', 'w+') as f:
                f.write('running')
                f.close()
            logger('Scheduler started', 'info')
            while is_apscheduler_running(scheduler):
                time.sleep(10)
        except KeyboardInterrupt:
            stop_apscheduler(scheduler)
