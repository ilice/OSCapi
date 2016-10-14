from django.http import JsonResponse
from osc.batch_process import update_inforiego_daily_batch


def update_inforiego_daily(request):
    last_update_date = request.GET.get('last_update_date', None)

    res = update_inforiego_daily_batch(last_update_date)

    return JsonResponse({'status': 'SUCCESS'}) if res is None else JsonResponse({'status': 'FAILED', 'reason': res})

