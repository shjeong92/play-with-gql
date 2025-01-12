from django.contrib import admin

from play_with_gql.libraries.models import Library


@admin.register(Library)
class LibraryAdmin(admin.ModelAdmin):
    pass
