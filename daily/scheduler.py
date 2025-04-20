from apscheduler.schedulers.background import BackgroundScheduler
from django.core import management
import logging

logger = logging.getLogger(__name__)

def start():
    """
    Start the APScheduler to run the generate_daily_challenge command twice a day at 12:00 PM and 12:00 AM
    """
    scheduler = BackgroundScheduler()
    
    # Schedule job to run at noon (12:00 PM)
    scheduler.add_job(
        lambda: management.call_command('generate_daily_challenge'),
        'cron', 
        hour=12,
        minute=0,
        id='generate_daily_challenge_noon',
        replace_existing=True
    )
    
    # Schedule job to run at midnight (12:00 AM)
    scheduler.add_job(
        lambda: management.call_command('generate_daily_challenge'),
        'cron', 
        hour=0,
        minute=0,
        id='generate_daily_challenge_midnight',
        replace_existing=True
    )
    
    # Log when the next run will happen
    scheduler.start()
    
    for job in scheduler.get_jobs():
        logger.info(f"Job '{job.id}' scheduled to run next at: {job.next_run_time}")