import traceback
from typing import Any, List, Union

from asgiref.sync import sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.backends.db import SessionStore
from django.http import HttpRequest, HttpResponse
from strawberry.django.views import AsyncGraphQLView as BaseAsyncGraphQLView
from strawberry.http import GraphQLHTTPResponse
from strawberry.types import ExecutionResult

from play_with_gql.users.models import User


class AsyncGraphQLView(BaseAsyncGraphQLView):
    async def process_result(self, request: HttpRequest, result: ExecutionResult) -> GraphQLHTTPResponse:
        return await super().process_result(request, result)

    async def get_context(self, request: HttpRequest, response: HttpResponse):
        # 세션 ID를 쿠키에서 가져옴
        session_key = request.COOKIES.get("sessionid")

        if session_key:
            # 세션 스토어 생성
            session = SessionStore(session_key=session_key)

            # 세션에서 user_id 가져오기
            user_id = await sync_to_async(session.get)("_auth_user_id")

            if user_id:
                # user_id로 사용자 조회
                try:
                    user = await sync_to_async(User.objects.get)(id=user_id)
                except User.DoesNotExist:
                    user = AnonymousUser()
            else:
                user = AnonymousUser()
        else:
            user = AnonymousUser()

        context = await super().get_context(request, response)
        context.request = request
        context.user = user
        return context
