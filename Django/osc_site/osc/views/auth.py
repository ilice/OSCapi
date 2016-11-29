from django.http import JsonResponse


def get_token(request):
    # google_token
    google_token = request.GET.get('google_token')

