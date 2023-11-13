from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from . import models
from collection.models import Artwork, Collection
from collection.models import Artist
from django.contrib.postgres import search
from django.core.paginator import Paginator
from .forms import CollectionForm, AgregarAColeccionForm

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

@login_required
def artwork(request, artwork_id):
    pintura = Artwork.objects.get(pk=artwork_id)
    collections = Collection.objects.filter(owner=request.user)
    list_collections(request)
    if request.method == 'POST':
        print("post")
        form = AgregarAColeccionForm(request.user, request.POST)
        if form.is_valid():
            selected_collection = form.cleaned_data['collection']
            if selected_collection:
                selected_collection.artworks.add(pintura)
    else:
        print("nopost")
        form = AgregarAColeccionForm(request.user)
    
    return render(request, 'collection/pinturas_detail.html', {'artwork': pintura, 'collections': collections, 'form': form})

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

        if (request.user.is_authenticated):
            user_collections= Collection.objects.filter(owner= request.user)
            collection_id = request.GET.get('id')
            if id:
                collection = models.Collection.objects.filter(id=collection_id).first()
                if collection.owner == request.user:
                    return render(request, 'collection/collection_items.html', {'collections':user_collections,'collection': collection,'items':collection.artworks.all()})

        return render(request, 'collection/collection_items.html', {'collection': None,'items':None})

@login_required
def delete_from_collection(request, collection, artwork):
    if request.user.is_authenticated:
        user_collections = Collection.objects.filter(owner=request.user)
        if request.method == 'GET':

            collection = Collection.objects.filter(id=collection).first()

            if collection:
                print('acuya')
                artworks = collection.artworks.all()
                try:
                    collection.artworks.remove(artworks.filter(id=artwork).first())
                except:
                    print('Item not found')

                return render(request, 'collection/collection_items.html', {'collections':user_collections,'collection': collection, 'items': artworks})
    return render(request, 'collection/collection_items.html', {'collection': None, 'items': None})

@login_required
def copy_to_collection(request, from_id, to_id, artwork_id):
    if request.user.is_authenticated:
        if request.method == 'GET':
            collection_from = Collection.objects.filter(id=from_id).first()
            collection_to = Collection.objects.filter(id=to_id).first()
            if(collection_to):
                artworks = collection_from.artworks.all()
                artwork = Artwork.objects.filter(id=artwork_id).first()
                if artwork:
                    collection_to.artworks.add(artwork)
                    return render(request, 'collection/collection_items.html', {'collection': collection_from, 'items': artworks})

    return render(request, 'collection/collection_items.html', {'collection': None, 'items': None})

@login_required
def move_to_collection(request, from_id, to_id, artwork_id):
    if request.user.is_authenticated:
        if request.method == 'GET':
            collection_from = Collection.objects.filter(id=from_id).first()
            collection_to = Collection.objects.filter(id=to_id).first()
            if(collection_to):
                artworks = collection_from.artworks.all()
                artwork = Artwork.objects.filter(id=artwork_id).first()
                if artwork:
                    collection_to.artworks.add(artwork)
                    to_delete = collection_from.artworks.filter(id= artwork_id)
                    for element in to_delete:
                        collection_from.artworks.remove(element)
                    return render(request, 'collection/collection_items.html', {'collection': collection_from, 'items': artworks})

    return render(request, 'collection/collection_items.html', {'collection': None, 'items': None})

def list_collections(request):
    collections = Collection.objects.filter(owner=request.user)

    for collection in collections:
        print(f"Nombre de la colección: {collection.name}")
        for artwork in collection.artworks.all():
            print(f"- {artwork.title}")


def agregar_obra(request, pintura_id):
    if request.method == 'POST':
        selected_collection_id = request.POST.get('collection')

        if selected_collection_id:
            try:
                selected_collection = Collection.objects.get(id=selected_collection_id, owner=request.user)
                pintura = Artwork.objects.get(pk=pintura_id)
                selected_collection.artworks.add(pintura)
            except Collection.DoesNotExist:
                # Manejar el caso en el que la colección no existe
                pass

    return redirect('pinturas_detail', pintura_id=pintura_id)

def eliminar_coleccion(request, collection_id):
    collection = get_object_or_404(Collection, pk=collection_id)
    
    # Agrega aquí la lógica para verificar si el usuario tiene permisos para eliminar esta colección.
    
    collection.delete()
    return HttpResponse(status=204, headers={'HX-Trigger': 'listChanged'})

def editar_coleccion(request, coleccion_id):
    coleccion = get_object_or_404(Collection, id=coleccion_id)

    if request.method == 'POST':
        # Caso de redirección
        coleccion.name = request.POST.get('name', '')
        coleccion.description = request.POST.get('description', '')
        coleccion.save()
        return HttpResponseRedirect('/collections/')
    else:
        # Caso de mostrar el formulario en la misma página
        return render(request, 'collection/edit_collection.html', {'coleccion': coleccion})