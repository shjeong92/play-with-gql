import strawberry

from play_with_gql.api.libraries.mutations import DeleteBookMutation, UpdateBookMutation
from play_with_gql.api.libraries.queries import GetLibraryQuery, GetNodeQuery


@strawberry.type
class Query(GetNodeQuery, GetLibraryQuery):
    pass


@strawberry.type
class Mutation(UpdateBookMutation, DeleteBookMutation):
    pass


schema = strawberry.Schema(query=Query, mutation=Mutation)
