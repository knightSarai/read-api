from django.conf import settings

from ninja import NinjaAPI
from ninja import NinjaAPI 
from knox.auth import TokenAuthentication


from ninja.security import APIKeyHeader, django_auth

from accounts.api import router as accounts_router


class AppTokenAuthentication(APIKeyHeader):
    param_name = "Authorization"
    

    def __call__(self, request):
        return self.authenticate(request)

    def authenticate(self, request):
        return TokenAuthentication().authenticate(request)


api = NinjaAPI(auth=AppTokenAuthentication())



api.add_router("/auth", accounts_router)
