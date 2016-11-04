import ast
from osc.services import retrieve_crops_from_elastic, update_crops_in_elastic, index_crops_in_elastic
from django.http import JsonResponse


def obtain_crops_elastic_query(request):
    query = ast.literal_eval(request.body)

    try:
        crops = retrieve_crops_from_elastic(query)
        return JsonResponse({'status': 'SUCCESS',
                             'result': crops})
    except Exception as e:
        return JsonResponse({'status': 'FAILURE',
                             'message': e.message})


def update_crops_elastic(request, crop_id):
    query = ast.literal_eval(request.body)

    try:
        update_crops_in_elastic(crop_id, query)
        return JsonResponse({'status': 'SUCCESS'})
    except Exception as e:
        return JsonResponse({'status': 'FAILURE',
                             'message': e.message})


def index_crops_elastic(request, crop_id):
    query = ast.literal_eval(request.body)

    try:
        index_crops_in_elastic(crop_id, query)
        return JsonResponse({'status': 'SUCCESS'})
    except Exception as e:
        return JsonResponse({'status': 'FAILURE',
                             'message': e.message})


