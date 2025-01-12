from django.db import models


class Book(models.Model):
    library = models.ForeignKey("libraries.Library", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    author = models.ForeignKey("libraries.Author", on_delete=models.CASCADE)
    published_date = models.DateField()
