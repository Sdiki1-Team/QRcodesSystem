from celery import shared_task
from django.utils import timezone
from datetime import date, datetime, timedelta
from .models import WorkStatic, Work

def is_schedule_active(work_static, current_time):
    repeat_every = work_static.repeat_every
    current_weekday = current_time.weekday()

    if repeat_every == 'workday':
        return current_weekday < 5 
    elif repeat_every == 'weekend':
        return current_weekday >= 5 
    elif repeat_every == 'weekly':
        return current_weekday == work_static.start_date.weekday()
    elif repeat_every == 'monthly':
        return current_time.day == work_static.start_date.day
    else:  
        return True


def should_create_work(work_static, current_time):
    current_time = current_time.replace(second=0, microsecond=0)
    current_time_t = current_time.time()

    if not (work_static.start_date <= current_time <= work_static.end_date):
        print("FALSE1")
        return False

    if not is_schedule_active(work_static, current_time):
        print("FALSE2")
        return False

    if not (work_static.daily_start_time <= current_time_t <= work_static.daily_end_time):
        print("FALSE3")
        return False

    if work_static.repeat_every in ['15m', '20m', '30m', '1h', '2h', '3h', '5h']:

        daily_start_datetime = datetime.combine(
            current_time.date(),
            work_static.daily_start_time
        )
        current_time = datetime.combine(current_time.date(), current_time.time())
        time_diff = current_time - daily_start_datetime
        
        if time_diff < timedelta(0):
            return False
        
        interval_str = work_static.repeat_every
        interval = int(interval_str[:-1])
        multiplier = 60 if 'h' in interval_str else 1
        print(multiplier, interval, interval_str)
        total_interval_seconds = interval * multiplier * 60
        
        if time_diff.total_seconds() % total_interval_seconds != 0:
            print("FALSE 4", time_diff.total_seconds() % total_interval_seconds )
            return False

    return True

@shared_task
def create_scheduled_works():
    print("TRY!!")
    
    now = timezone.now()
    print(now)
    current_time = now.replace(second=0, microsecond=0)
    
    for work_static in WorkStatic.objects.all():
        if should_create_work(work_static, current_time):
            Work.objects.create(
                name=work_static.name,
                description=work_static.description,
                worker_comment=work_static.worker_comment,
                object=work_static.object,
                user=work_static.user,
                start_time=current_time,
                work_static=work_static,
            )
