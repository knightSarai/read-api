from django.contrib.auth import get_user_model
from ninja import Router
from ninja.errors import ValidationError

from .schemas import UserOut, UserRegisterSchema, UserLoginSchema

from django.contrib.auth import login as django_login

from rest_framework.authtoken.serializers import AuthTokenSerializer

from knox.views import LoginView as KnoxLoginView


router = Router()


@router.post("/login", auth=None)
def login(request, user_payload: UserLoginSchema):
    user_payload = user_payload.dict()

    serializer = AuthTokenSerializer(data=user_payload)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data['user']
    django_login(request, user)
    return KnoxLoginView().post(request, format=None).data


@router.post("/register", auth=None)
def register(request, user_payload: UserRegisterSchema, response=201):

    if user_payload.password != user_payload.password_confirm:
        raise ValidationError("Password does not match")

    User = get_user_model()
    email_exist = User.objects.filter(email=user_payload.email).exists()
    if email_exist:
        raise ValidationError("Email already exist")

    User.objects.create_user(
        username=user_payload.username,
        email=user_payload.email,
        password=user_payload.password
    )

    return
        
@router.get("/me", response=UserOut)
def me(request):
    print(request.auth)
    return request.user
