from factory import Faker, fuzzy
from factory.django import DjangoModelFactory

from play_with_gql.libraries.models.author import Author


class AuthorFactory(DjangoModelFactory):
    class Meta:
        model = Author

    title = fuzzy.FuzzyChoice(["Mr", "Ms", "Dr"])
    name = Faker("name")
