import strawberry
import strawberry_django
from strawberry import relay

from play_with_gql.api.libraries.nodes import BookNode
from play_with_gql.libraries.models.book import Book


@strawberry.type
class UpdateBookMutation:
    @strawberry_django.mutation
    def update_book(
        self,
        id: relay.GlobalID,
        title: str | None = None,
        published_date: str | None = None,
    ) -> BookNode:
        book = Book.objects.get(pk=id.node_id)

        if title is not None:
            book.title = title
        if published_date is not None:
            book.published_date = published_date

        book.save()
        return book


@strawberry.type
class DeleteBookMutation:
    @strawberry_django.mutation
    def delete_book(self, id: relay.GlobalID) -> bool:
        book = Book.objects.get(pk=id.node_id)
        book.delete()
        return True
