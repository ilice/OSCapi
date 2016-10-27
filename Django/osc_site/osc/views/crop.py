import ast
from osc.services import retrieve_crops_from_elastic
from django.http import JsonResponse


def obtain_crops_elastic_query(request):
    query = ast.literal_eval(request.body)

    crops = retrieve_crops_from_elastic(query)

    return JsonResponse({'status': 'SUCCESS',
                         'result': crops})
