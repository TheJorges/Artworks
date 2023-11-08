from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from collection import models as collectionModels


class Set:
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=256)
    created_on = models.DateTimeField(default=timezone.now)
    artworks = models.ManyToManyField(collectionModels.Artwork)

