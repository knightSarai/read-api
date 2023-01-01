from knox.auth import TokenAuthentication
from ninja.security import APIKeyHeader


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
