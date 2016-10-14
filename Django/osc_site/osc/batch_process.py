from osc.services.batch_process_service import *
from osc.models import BatchProcess
import osc.services.importer.inforiego as inforiego
from datetime import datetime, timedelta


def update_inforiego_daily_batch(last_update_date=None):
    if last_update_date is None:
        latest_date_launched = get_latest_date_launched(BatchProcess.P_INFORIEGO_DAILY)
        if latest_date_launched is not None:
            last_update_date = (latest_date_launched - timedelta(days=1)).strftime('%d/%m/%Y')

    if last_update_date is None:
        default_date = datetime.now() - timedelta(weeks=2)
        last_update_date = default_date.strftime('%d/%m/%Y')

    p_id = start_batch_process(BatchProcess.P_INFORIEGO_DAILY)
    try:
        inforiego.insert_all_stations_inforiego_daily(fecha_ultima_modificacion=last_update_date)
        success_batch_process(p_id)

        return None
    except Exception as e:
        fail_batch_process(p_id)

        return e.message

