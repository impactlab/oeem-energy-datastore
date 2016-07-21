import os
from django.http import HttpResponse


def challenge(request):
    return HttpResponse(os.environ.get("CHALLENGE_BODY"))
