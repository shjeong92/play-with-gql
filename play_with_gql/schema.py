import strawberry

from play_with_gql.api.libraries.queries import GetNodeQuery


@strawberry.type
class Query(GetNodeQuery):
    pass


schema = strawberry.Schema(query=Query)
