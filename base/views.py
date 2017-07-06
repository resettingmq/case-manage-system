from django.shortcuts import render
from django.views import generic

from . import models

# Create your views here.


def index(request):
    return render(request, 'base/index.html')


class ClientListView(generic.ListView):
    model = models.Client
    template_name = 'base/client_list.html'
