import strawberry
import strawberry_django
from strawberry import relay

from play_with_gql.api.libraries.nodes import AuthorNode, BookNode, LibraryNode


@strawberry.type
class GetNodeQuery:
    node: relay.Node = relay.node()
