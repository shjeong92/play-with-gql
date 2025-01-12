from django.db import models


class Author(models.Model):
    title = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
