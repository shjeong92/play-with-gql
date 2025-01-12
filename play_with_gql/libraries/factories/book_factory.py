from factory import Faker, SubFactory
from factory.django import DjangoModelFactory

from play_with_gql.libraries.factories.author_factory import AuthorFactory
from play_with_gql.libraries.factories.library_factory import LibraryFactory
from play_with_gql.libraries.models.book import Book


class BookFactory(DjangoModelFactory):
    class Meta:
        model = Book

    title = Faker("name")
    author = SubFactory(AuthorFactory)
    library = SubFactory(LibraryFactory)
