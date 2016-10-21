from django_cron import CronJobBase, Schedule
from django_cron.models import CronJobLog
from django.db.models import Max
from datetime import datetime, timedelta
from django.core.management import call_command

import osc.services.importer.inforiego as inforiego
import osc.services.importer.cadastre as cadastre


class UpdateInforiegoDaily(CronJobBase):
    RUN_EVERY_MINS = 24*60

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'jobs.update_inforiego_daily'

    def do(self, last_update_date=None):
        if last_update_date is None:
            last_date_launched = CronJobLog.objects.filter(code=UpdateInforiegoDaily.code,
                                                           is_success=True).aggregate(max=Max('end_time'))['max']
            if last_date_launched is not None:
                last_update_date = (last_date_launched - timedelta(days=1)).strftime('%d/%m/%Y')

        if last_update_date is None:
            default_date = datetime.now() - timedelta(weeks=2)
            last_update_date = default_date.strftime('%d/%m/%Y')

        inforiego.insert_all_stations_inforiego_daily(fecha_ultima_modificacion=last_update_date)


class UpdateCadastreParcels(CronJobBase):
    # RUN_EVERY_MINS = 24*60*30
    #
    # schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'jobs.update_cadastre_parcels'

    def do(self):
        call_command('import_parcels')
