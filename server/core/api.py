from ninja import NinjaAPI

from accounts.api import router as accounts_router, profile_router
from books.api import router as books_router
from core.auth import AppTokenAuthentication
from userbooks.api import router as userbooks_router

api = NinjaAPI(auth=AppTokenAuthentication())

api.add_router("/auth", accounts_router)
api.add_router("/user/profile", profile_router)
api.add_router("/books", books_router)
api.add_router('/user', userbooks_router)
