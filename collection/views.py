from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from . import models
from collection.models import Artwork
import random

def register(request):
    if request.method == 'POST':
        f = UserCreationForm(request.POST)
        if f.is_valid():
            f.save()
            username = f.cleaned_data.get('username')
            raw_password = f.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)

            return HttpResponseRedirect('/')

    else:
        f = UserCreationForm()

    return render(request, 'registration/registration_form.html', {'form': f})


def index(request):
    artworks = list(Artwork.objects.all())
    random_works = []
    if artworks:
        random_works = random.sample(artworks, 16)
    return render(request, 'collection/index.html', {'artworks': random_works})

def artwork(request, artwork_id):

    artwork = Artwork.objects.get(pk=artwork_id)

    return render(request, 'collection/pinturas_detail.html', {'artwork': artwork})

def author(request, artwork_id):

    artwork = Artwork.objects.get(pk=artwork_id)

    return render(request, 'collection/pinturas_detail.html', {'artwork': artwork})