from django.db import models


class Book(models.Model):
    library = models.ForeignKey("libraries.Library", on_delete=models.CASCADE, related_name="books")
    title = models.CharField(max_length=255)
    author = models.ForeignKey("libraries.Author", on_delete=models.CASCADE, related_name="books")
    published_date = models.DateField()
