import base64
from typing import Any

import pytest
from django.db.models import Model

from play_with_gql.libraries.models.author import Author
from play_with_gql.libraries.models.book import Book
from play_with_gql.libraries.models.library import Library
from play_with_gql.schema import schema


@pytest.fixture
def library() -> Library:
    return Library.objects.create(name="Test Library")


@pytest.fixture
def author() -> Author:
    return Author.objects.create(name="Test Author", title="Professor")


@pytest.fixture
def book(library: Library, author: Author) -> Book:
    return Book.objects.create(title="Test Book", author=author, library=library, published_date="2024-01-01")


def to_global_id(instance: Model) -> str:
    return base64.b64encode(f"{instance.__class__.__name__}Node:{instance.pk}".encode()).decode()


def execute_query(query: str, variables: dict[str, Any] | None = None):
    """GraphQL 쿼리 실행을 위한 헬퍼 메서드"""
    return schema.execute_sync(query, variable_values=variables)


@pytest.mark.django_db
def test_get_library_with_books(library: Library, author: Author, book: Book):
    query = """
    query GetLibraryWithBooks($id: GlobalID!, $first: Int) {
      node(id: $id) {
        __typename
        ... on LibraryNode {
          id
          name
          books(first: $first) {
            edges {
              node {
                id
                title
                author {
                  id
                  name
                  title
                }
              }
            }
            pageInfo {
              hasNextPage
              hasPreviousPage
              startCursor
              endCursor
            }
            totalCount
          }
        }
      }
    }
    """

    variables = {"id": to_global_id(library), "first": 10}

    result = execute_query(query, variables)

    assert result.errors is None
    data = result.data["node"]

    # 응답 검증
    assert data["__typename"] == "LibraryNode"
    assert data["name"] == "Test Library"

    books = data["books"]
    assert books["totalCount"] == 1

    book_edge = books["edges"][0]["node"]
    assert book_edge["title"] == "Test Book"
    assert book_edge["author"]["name"] == "Test Author"
    assert book_edge["author"]["title"] == "Professor"


@pytest.mark.django_db
def test_get_author_with_books(library: Library, author: Author, book: Book):
    query = """
    query GetAuthorWithBooks($id: GlobalID!, $first: Int) {
      node(id: $id) {
        __typename
        ... on AuthorNode {
          id
          name
          title
          books(first: $first) {
            edges {
              node {
                id
                title
                library {
                  id
                  name
                }
              }
            }
            totalCount
          }
        }
      }
    }
    """

    variables = {"id": to_global_id(author), "first": 10}

    result = execute_query(query, variables)

    assert result.errors is None
    data = result.data["node"]

    # 응답 검증
    assert data["__typename"] == "AuthorNode"
    assert data["name"] == "Test Author"
    assert data["title"] == "Professor"

    books = data["books"]
    assert books["totalCount"] == 1

    book_edge = books["edges"][0]["node"]
    assert book_edge["title"] == "Test Book"
    assert book_edge["library"]["name"] == "Test Library"


@pytest.mark.django_db
def test_get_book_details(library: Library, author: Author, book: Book):
    query = """
    query GetBook($id: GlobalID!) {
      node(id: $id) {
        __typename
        ... on BookNode {
          id
          title
          publishedDate
          author {
            id
            name
            title
          }
          library {
            id
            name
          }
        }
      }
    }
    """

    variables = {"id": to_global_id(book)}

    result = execute_query(query, variables)

    assert result.errors is None
    data = result.data["node"]

    # 응답 검증
    assert data["__typename"] == "BookNode"
    assert data["title"] == "Test Book"
    assert data["author"]["name"] == "Test Author"
    assert data["library"]["name"] == "Test Library"


@pytest.mark.django_db
def test_introspection_query():
    query = """
    query GetTypes {
      __schema {
        types {
          name
          kind
          description
        }
      }
    }
    """

    result = execute_query(query)

    assert result.errors is None
    types = result.data["__schema"]["types"]

    # 주요 타입들이 존재하는지 확인
    type_names = [t["name"] for t in types]
    expected_types = ["LibraryNode", "BookNode", "AuthorNode", "Query"]

    for type_name in expected_types:
        assert type_name in type_names
