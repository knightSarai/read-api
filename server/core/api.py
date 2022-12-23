from knox.auth import TokenAuthentication
from ninja import NinjaAPI
from ninja.security import APIKeyHeader

from accounts.api import router as accounts_router
from books.api import router as books_router


class AppTokenAuthentication(APIKeyHeader):
    param_name = "Authorization"

    def __call__(self, request):
        return self.authenticate(request)

    def authenticate(self, request):
        user = None
        authed = TokenAuthentication().authenticate(request)
        if authed:
            user, _ = authed
        request.user = user
        return user


api = NinjaAPI(auth=AppTokenAuthentication())

api.add_router("/auth", accounts_router)
api.add_router("/books", books_router)
