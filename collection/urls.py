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
    path("collections/", views.collections, name="collections"),
    path("collection_list/", views.collection_list, name="collection_list"),
    path("collection/add", views.collection_add, name="collection_add"),
    path('collection/',views.collection_items, name='collection_items'),
    path("collection/delete/<int:collection_id>", views.eliminar_coleccion, name="eliminar_coleccion"),
    path('collection/delete-item/<int:collection>/<int:artwork>', views.delete_from_collection, name='delete_from_collection'),
    path('collection/copy_item/<int:from_id>/<int:to_id>/<int:artwork_id>',views.copy_to_collection, name='copy_to_collection'),
    path('collection/move_item/<int:from_id>/<int:to_id>/<int:artwork_id>',views.move_to_collection, name='move_to_collection'),
    path('edit_collection/<int:coleccion_id>/',views.editar_coleccion, name='edit_collection'),

]

