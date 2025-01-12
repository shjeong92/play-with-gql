from typing import Iterable

import strawberry_django
from strawberry import auto, relay
from strawberry_django.relay import ListConnectionWithTotalCount

from play_with_gql.libraries.models.author import Author
from play_with_gql.libraries.models.book import Book
from play_with_gql.libraries.models.library import Library


@strawberry_django.type(Library)
class LibraryNode(relay.Node):
    name: str

    @strawberry_django.connection(ListConnectionWithTotalCount["BookNode"])
    def books(self, root: Library, info) -> Iterable[Book]:
        return Book.objects.filter(library=root)


@strawberry_django.type(Author)
class AuthorNode(relay.Node):
    name: str
    title: str

    @strawberry_django.connection(ListConnectionWithTotalCount["BookNode"])
    def books(self, root: Author, info) -> Iterable[Book]:
        return Book.objects.filter(author=root)


@strawberry_django.type(Book)
class BookNode(relay.Node):
    title: str
    author: AuthorNode
    library: "LibraryNode"
    published_date: auto
