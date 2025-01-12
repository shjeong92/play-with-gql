import strawberry
from strawberry import relay


@strawberry.type
class GetNodeQuery:
    node: relay.Node = relay.node()
