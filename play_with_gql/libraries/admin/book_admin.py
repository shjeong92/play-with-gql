from django.contrib import admin

from play_with_gql.libraries.models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    pass
