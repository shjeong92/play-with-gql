from factory import Faker
from factory.django import DjangoModelFactory

from play_with_gql.libraries.models.library import Library


class LibraryFactory(DjangoModelFactory):
    class Meta:
        model = Library

    name = Faker("name")
