from django.http import JsonResponse

import osc.jobs as jobs


def update_inforiego_daily(request):
    last_update_date = request.GET.get('last_update_date', None)

    job = jobs.UpdateInforiegoDaily()
    try:
        job.do(last_update_date)

        return JsonResponse({'status': 'SUCCESS'})
    except Exception as e:

        return JsonResponse({'status': 'FAILED', 'reason': str(e)})

