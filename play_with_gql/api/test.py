import base64
from typing import Any

import pytest
from asgiref.sync import sync_to_async
from django.db.models import Model
from django.test.client import AsyncClient
from factory.fuzzy import FuzzyText

from play_with_gql.libraries.models.author import Author
from play_with_gql.libraries.models.book import Book
from play_with_gql.libraries.models.librarian import Librarian
from play_with_gql.libraries.models.library import Library
from play_with_gql.schema import schema
from play_with_gql.users.models import User


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


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_me_query_with_auth(admin_user):
    admin_user = await sync_to_async(User.objects.create_superuser)(
        username=FuzzyText().fuzz(), email="bdmin@example.com", password="password123"
    )
    client = AsyncClient()
    await client.aforce_login(admin_user)
    query = """
    query {
      me
    }
    """

    response = await client.post("/graphql/", {"query": query}, content_type="application/json")

    assert response.status_code == 200
    data = response.json()
    assert data["data"]["me"] == admin_user.username


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_me_query_without_auth():
    client = AsyncClient()
    query = """
    query {
      me
    }
    """

    response = await client.post("/graphql/", {"query": query}, content_type="application/json")

    assert response.status_code == 200
    data = response.json()
    assert data["data"]["me"] is None


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_me_query_with_invalid_session():
    client = AsyncClient()
    query = """
    query {
      me
    }
    """

    # 잘못된 세션 ID로 요청
    response = await client.post(
        "/graphql/", {"query": query}, content_type="application/json", HTTP_COOKIE="sessionid=invalid_session_id"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["data"]["me"] is None


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_get_library_with_librarian_permission():
    # 테스트 데이터 생성
    library = await sync_to_async(Library.objects.create)(name="Test Library")
    user = await sync_to_async(User.objects.create_user)(
        username=FuzzyText().fuzz(), email="librarian@example.com", password="password123"
    )

    # Librarian 생성
    await sync_to_async(Librarian.objects.create)(user=user, library=library)

    # 로그인
    client = AsyncClient()
    await client.aforce_login(user)

    query = """
    query GetLibrary($nodeId: String!) {
      library(nodeId: $nodeId) {
        name
      }
    }
    """

    variables = {"nodeId": to_global_id(library)}

    response = await client.post(
        "/graphql/", {"query": query, "variables": variables}, content_type="application/json"
    )

    assert response.status_code == 200
    data = response.json()
    assert data.get("errors") is None
    assert data["data"]["library"]["name"] == library.name


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_get_library_without_librarian_permission():
    # 일반 사용자 생성
    library = await sync_to_async(Library.objects.create)(name="Test Library")
    user = await sync_to_async(User.objects.create_user)(
        username=FuzzyText().fuzz(), email="user@example.com", password="password123"
    )

    # 로그인
    client = AsyncClient()
    await client.aforce_login(user)

    query = """
    query GetLibrary($nodeId: String!) {
      library(nodeId: $nodeId) {
        id
        name
      }
    }
    """

    variables = {"nodeId": to_global_id(library)}

    response = await client.post(
        "/graphql/", {"query": query, "variables": variables}, content_type="application/json"
    )

    assert response.status_code == 200
    data = response.json()
    assert data.get("errors") is not None  # 권한 에러가 발생해야 함
    assert "errors" in data
    assert any("Forbidden" in error.get("message", "") for error in data["errors"])


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_get_library_without_auth():
    # 인증되지 않은 사용자 테스트
    library = await sync_to_async(Library.objects.create)(name="Test Library")
    client = AsyncClient()

    query = """
    query GetLibrary($nodeId: String!) {
      library(nodeId: $nodeId) {
        id
        name
      }
    }
    """

    variables = {"nodeId": to_global_id(library)}

    response = await client.post(
        "/graphql/", {"query": query, "variables": variables}, content_type="application/json"
    )

    assert response.status_code == 200
    data = response.json()
    assert data.get("errors") is not None  # 인증 에러가 발생해야 함
    assert "errors" in data
    assert any("Unauthenticated" in error.get("message", "") for error in data["errors"])


@pytest.mark.django_db
def test_update_book_mutation(book: Book):
    query = """
    mutation UpdateBook($id: GlobalID!, $title: String) {
      updateBook(id: $id, title: $title) {
        id
        title
        publishedDate
      }
    }
    """

    variables = {"id": to_global_id(book), "title": "Updated Book Title"}

    result = execute_query(query, variables)

    assert result.errors is None
    data = result.data["updateBook"]
    assert data["title"] == "Updated Book Title"

    # DB에서 실제로 업데이트되었는지 확인
    updated_book = Book.objects.get(id=book.id)
    assert updated_book.title == "Updated Book Title"


@pytest.mark.django_db
def test_update_book_partial_mutation(book: Book):
    query = """
    mutation UpdateBook($id: GlobalID!, $title: String) {
      updateBook(id: $id, title: $title) {
        id
        title
        publishedDate
      }
    }
    """

    variables = {"id": to_global_id(book), "title": "Only Title Updated"}

    result = execute_query(query, variables)

    assert result.errors is None
    data = result.data["updateBook"]
    assert data["title"] == "Only Title Updated"
    assert data["publishedDate"] == "2024-01-01"  # 원래 날짜가 유지되어야 함

    # DB에서 실제로 업데이트되었는지 확인
    updated_book = Book.objects.get(id=book.id)
    assert updated_book.title == "Only Title Updated"
    assert str(updated_book.published_date) == "2024-01-01"


@pytest.mark.django_db
def test_delete_book_mutation(book: Book):
    query = """
    mutation DeleteBook($id: GlobalID!) {
      deleteBook(id: $id)
    }
    """

    variables = {"id": to_global_id(book)}

    result = execute_query(query, variables)

    assert result.errors is None
    assert result.data["deleteBook"] is True

    # DB에서 실제로 삭제되었는지 확인
    assert not Book.objects.filter(id=book.id).exists()


@pytest.mark.django_db
def test_update_book_with_invalid_id():
    query = """
    mutation UpdateBook($id: GlobalID!, $title: String) {
      updateBook(id: $id, title: $title) {
        id
        title
      }
    }
    """

    variables = {
        "id": to_global_id(Book(id=99999)),  # 존재하지 않는 ID
        "title": "This Should Fail",
    }

    result = execute_query(query, variables)

    assert result.errors is not None
    assert len(result.errors) > 0
    assert "Book matching query does not exist" in str(result.errors[0])


@pytest.mark.django_db
def test_delete_book_with_invalid_id():
    query = """
    mutation DeleteBook($id: GlobalID!) {
      deleteBook(id: $id)
    }
    """

    variables = {
        "id": to_global_id(Book(id=99999))  # 존재하지 않는 ID
    }

    result = execute_query(query, variables)

    assert result.errors is not None
    assert len(result.errors) > 0
    assert "Book matching query does not exist" in str(result.errors[0])


@pytest.mark.django_db
def test_get_books_filtered_by_title_icontains(library: Library, author: Author):
    # 테스트용 책들 생성
    Book.objects.create(title="Python Programming", author=author, library=library, published_date="2024-01-01")
    Book.objects.create(title="Python Web Development", author=author, library=library, published_date="2024-01-01")
    Book.objects.create(title="Java Programming", author=author, library=library, published_date="2024-01-01")

    query = """
    query GetBooksByTitle($title: String!) {
      books(filters: { title: { iContains: $title } }) {
        id
        title
        publishedDate
        author {
          name
        }
      }
    }
    """

    # "Python"이 포함된 책들 검색
    variables = {"title": "Python"}
    result = execute_query(query, variables)

    assert result.errors is None
    books = result.data["books"]
    assert len(books) == 2  # "Python"이 포함된 책 2개
    assert all("Python" in book["title"] for book in books)


@pytest.mark.django_db
def test_get_books_with_exact_title(library: Library, author: Author):
    # 테스트용 책들 생성
    Book.objects.create(title="Python Programming", author=author, library=library, published_date="2024-01-01")
    Book.objects.create(title="Python Programming Guide", author=author, library=library, published_date="2024-01-01")

    query = """
    query GetBooksByExactTitle($title: String!) {
      books(filters: { title: { exact: $title } }) {
        id
        title
      }
    }
    """

    variables = {"title": "Python Programming"}
    result = execute_query(query, variables)

    assert result.errors is None
    books = result.data["books"]
    assert len(books) == 1
    assert books[0]["title"] == "Python Programming"


@pytest.mark.django_db
def test_get_books_with_no_matches(library: Library, author: Author):
    # 테스트용 책들 생성
    Book.objects.create(title="Python Programming", author=author, library=library, published_date="2024-01-01")
    Book.objects.create(title="Java Programming", author=author, library=library, published_date="2024-01-01")

    query = """
    query GetBooksByTitle($title: String!) {
      books(filters: { title: { iContains: $title } }) {
        id
        title
      }
    }
    """

    variables = {"title": "Ruby"}
    result = execute_query(query, variables)

    assert result.errors is None
    books = result.data["books"]
    assert len(books) == 0  # 매칭되는 책이 없어야 함
