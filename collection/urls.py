from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("accounts/profile/", views.index, name="index"),
    path("artwork/<int:artwork_id>", views.artwork, name="pinturas_detail"),
    path("accounts/register/", views.register, name="register"),
    path("accounts/autor/", views.author, name="author")
]
