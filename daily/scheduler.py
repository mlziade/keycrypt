from apscheduler.schedulers.background import BackgroundScheduler
from django.core import management
import logging

logger = logging.getLogger(__name__)

def start():
    """
    Start the APScheduler to run the create_daily_llm_challenge command every hour.
    """
    scheduler = BackgroundScheduler()

    # Schedule job to run every hour
    scheduler.add_job(
        lambda: management.call_command('create_daily_llm_challenge'),
        'interval',
        hours=1,
        id='create_daily_llm_challenge_hourly',
        replace_existing=True
    )

    # Log when the next run will happen
    scheduler.start()

    for job in scheduler.get_jobs():
        logger.info(f"Job '{job.id}' scheduled to run next at: {job.next_run_time}")
