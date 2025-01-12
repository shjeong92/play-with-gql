from django.contrib import admin

from play_with_gql.libraries.models import Author


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    pass
