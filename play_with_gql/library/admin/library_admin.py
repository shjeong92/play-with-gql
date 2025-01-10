from django.contrib import admin

from play_with_gql.library.models import Library


@admin.register(Library)
class LibraryAdmin(admin.ModelAdmin):
    pass
