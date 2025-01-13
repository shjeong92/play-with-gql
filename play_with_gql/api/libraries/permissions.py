import base64
from typing import Any

from asgiref.sync import sync_to_async
from strawberry.exceptions import StrawberryGraphQLError
from strawberry.permission import BasePermission
from strawberry.types import Info

from play_with_gql.libraries.models.librarian import Librarian


class GraphQLError(StrawberryGraphQLError):
    message: str
    code: str | None = None

    def __init__(self, message: str | None = None):
        super().__init__(
            message=message or self.message,
            extensions={
                "code": self.code,
            },
        )


class IsAuthenticated(BasePermission):
    @sync_to_async
    def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        if not info.context.request.user.is_authenticated:
            raise GraphQLError("Unauthenticated")
        return True


class IsLibrarian(BasePermission):
    @sync_to_async
    def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        node_id = kwargs["node_id"]
        decoded = base64.b64decode(node_id).decode()
        database_id = decoded.split(":")[-1]
        if not Librarian.objects.filter(library_id=database_id, user=info.context.user).exists():
            raise GraphQLError("Forbidden")
        return True
