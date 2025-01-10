from django.contrib import admin

from play_with_gql.library.models import Author


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    pass
