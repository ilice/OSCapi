from osc.models import BatchProcess
from django.db.models import Max


def start_batch_process(process_name, date_launched):
    process = BatchProcess(name=process_name, status='P', date_launched=date_launched)
    process.save()

    return process.id


def success_batch_process(process_id):
    process = BatchProcess.objects.get(pk=process_id)
    if process is not None:
        process.status = 'S'
        process.save()


def fail_batch_process(process_id):
    process = BatchProcess.objects.get(pk=process_id)
    if process is not None:
        process.status = 'F'
        process.save()


def get_latest_date_launched(process_name):
    return BatchProcess.objects.filter(name=process_name, status='S').aggregate(max=Max('date_launched'))['max']
