from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import logout
from django.shortcuts import get_object_or_404, render


def home(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('login/')
    return render(request, 'home.html', {})