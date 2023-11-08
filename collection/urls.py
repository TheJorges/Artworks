from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("accounts/profile/", views.index, name="profile"),
    path("artwork/<int:artwork_id>", views.artwork, name="pinturas_detail"),
    path("accounts/register/", views.register, name="register"),
    path("author/<str:author_name>/", views.author, name="author"),
    path("artwork_search/", views.search_artworks, name="artwork_search"),
    path("artwork/random/", views.random_artworks, name="random_artworks"),
]
