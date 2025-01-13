import base64
from typing import Any

import strawberry
import strawberry_django
from strawberry import auto, relay
from strawberry.types import Info

from play_with_gql.api.libraries.nodes import BookNode, LibraryNode
from play_with_gql.api.libraries.permissions import IsAuthenticated, IsLibrarian
from play_with_gql.libraries.models.book import Book
from play_with_gql.libraries.models.library import Library


@strawberry.type
class GetNodeQuery:
    node: relay.Node = relay.node()

    @strawberry.field
    async def me(self, info: Info) -> str | None:
        context = info.context
        if context.user.is_authenticated:
            return context.user.username

        return None


@strawberry.type
class GetLibraryQuery:
    @strawberry.field(permission_classes=[IsAuthenticated, IsLibrarian])
    async def library(self, info: Info, node_id: str) -> LibraryNode:
        # base64로 인코딩된 ID에서 실제 ID 부분만 추출
        try:
            decoded = base64.b64decode(node_id).decode()
            real_id = decoded.split(":")[-1]
            library = await Library.objects.aget(id=real_id)
            return library
        except (ValueError, IndexError):
            raise ValueError("Invalid library ID format")


@strawberry_django.filter(Book, lookups=True)
class BookFilter:
    title: auto


@strawberry.type
class GetBooksQuery:
    books: list[BookNode] = strawberry_django.field(filters=BookFilter)
