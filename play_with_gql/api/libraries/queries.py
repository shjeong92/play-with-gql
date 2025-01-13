import base64
from typing import Any

import strawberry
from strawberry import relay
from strawberry.types import Info

from play_with_gql.api.libraries.nodes import LibraryNode
from play_with_gql.api.libraries.permissions import IsAuthenticated, IsLibrarian
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
