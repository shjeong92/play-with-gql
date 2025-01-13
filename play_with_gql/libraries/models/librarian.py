from django.db import models


class Librarian(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="librarians")
    name = models.CharField(max_length=255)
    library = models.ForeignKey("libraries.Library", on_delete=models.CASCADE, related_name="librarians")
