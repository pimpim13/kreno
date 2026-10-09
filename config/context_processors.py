from django.conf import settings


def marque(request):
    return {'brand': settings.BRAND}
