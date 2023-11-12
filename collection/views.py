from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from . import models
from collection.models import Artwork, Collection
from collection.models import Artist
from django.contrib.postgres import search
from django.core.paginator import Paginator
from .forms import CollectionForm
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

def author(request, author_name):
    author = Artist.objects.get(name=author_name)
    artworks = Artwork.objects.filter(author=author)
    return render(request, 'collection/author.html', {'author': author,'artworks': artworks})

def random_artworks(request):
    artwork_count = Artwork.objects.count()
    num_artworks_to_display = 4

    if artwork_count <= num_artworks_to_display:
        random_works = list(Artwork.objects.all())
    else:
        # Genera un conjunto de índices aleatorios únicos para seleccionar obras de arte
        random_indexes = random.sample(range(artwork_count), num_artworks_to_display)
        random_works = [Artwork.objects.all()[index] for index in random_indexes]

    return render(request, 'collection/artwork_search.html', {'artworks': random_works})

def search_artworks(request):
    if request.method == 'GET':
        value = request.GET.get('search')  # Cambiar a request.GET.get para manejar la ausencia de 'search'
        if value:
            artwork = ft_artworks(value)
            print(value)
            print(artwork)
            paginator = Paginator(artwork, 4)
            page_number = request.GET.get("page")
            page_obj = paginator.get_page(page_number)

            return render(request, 'collection/artwork_search.html', {'page_obj': page_obj, 'search_value': value})

    # Agregar una respuesta de página de error u otra respuesta apropiada aquí si es necesario
    return render(request, 'collection/error.html')  # Esto es solo un ejemplo, puedes personalizarlo


def ft_artworks(value):
    vector = (
        search.SearchVector("title", weight="A")
        + search.SearchVector("author__name", weight="B")  # Usar "author__name" en lugar de "author_name"
        + search.SearchVector("style", weight="C")
        + search.SearchVector("genre", weight="C")
    )
    query = search.SearchQuery(value, search_type="websearch")
    return (
        Artwork.objects.annotate(
            search=vector,
            rank=search.SearchRank(vector, query),
        )
        .filter(search=query)
        .order_by("-rank")
    )

def collections(request):
    collections = Collection.objects.filter(owner=request.user)
    return render(request, 'collection/collections.html',
                  {'collections': collections})


def collection_list(request):
    collections = Collection.objects.filter(owner=request.user)
    return render(request, 'collection/collection_list.html',
                  {'collections': collections})


def collection_add(request):
    form = None
    if request.method == 'POST':
        form = CollectionForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            collection = Collection(
                    name=name,
                    description=description,
                    owner=request.user)
            collection.save()
            return HttpResponse(status=204,
                                headers={'HX-Trigger': 'listChanged'})

    return render(request,
                  'collection/collection_form.html',
                  {'form': form})

@login_required
def collection_items(request):
        print('hola')
        if (request.user.is_authenticated):
            collection_id = request.GET.get('id')
            if id:
                collection = models.Collection.objects.filter(id=collection_id).first()
                if collection.owner == request.user:
                    return render(request, 'collection/collection_items.html', {'collection': collection,'items':collection.artworks.all()})

        return render(request, 'collection/collection_items.html', {'collection': None,'items':None})

