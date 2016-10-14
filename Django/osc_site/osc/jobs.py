from django_cron import CronJobBase, Schedule
from batch_process import update_inforiego_daily_batch


class UpdateInforiegoDaily(CronJobBase):
    RUN_AT_TIMES = ['23:30']

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code='jobs.update_inforiego_daily'

    def do(self):
        update_inforiego_daily_batch()
