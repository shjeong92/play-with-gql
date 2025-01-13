import strawberry

from play_with_gql.api.libraries.queries import GetLibraryQuery, GetNodeQuery


@strawberry.type
class Query(GetNodeQuery, GetLibraryQuery):
    pass


schema = strawberry.Schema(query=Query)
