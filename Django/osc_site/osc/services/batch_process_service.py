from osc.models import BatchProcess
from django.db.models import Max
from django.utils import timezone

__all__ = ['start_batch_process', 'success_batch_process', 'fail_batch_process',
           'cancel_batch_process', 'get_latest_date_launched']


def start_batch_process(process_name, date_launched=None):
    process = BatchProcess(name=process_name, status='P', date_launched=date_launched)
    process.save()

    return process.id


def success_batch_process(process_id):
    process = BatchProcess.objects.get(pk=process_id)
    if process is not None:
        process.date_finished = timezone.now()
        process.status = 'S'
        process.save()


def cancel_batch_process(process_id):
    process = BatchProcess.objects.get(pk=process_id)
    if process is not None:
        process.date_finished = timezone.now()
        process.status = 'C'
        process.save()


def fail_batch_process(process_id):
    process = BatchProcess.objects.get(pk=process_id)
    if process is not None:
        process.date_finished = timezone.now()
        process.status = 'F'
        process.save()


def get_latest_date_launched(process_name):
    return BatchProcess.objects.filter(name=process_name, status='S').aggregate(max=Max('date_launched'))['max']
