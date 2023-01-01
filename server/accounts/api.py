from django.contrib.auth import get_user_model, login as django_login
from django.shortcuts import get_object_or_404
from knox.views import LoginView as KnoxLoginView
from ninja import Router, File, UploadedFile
from ninja.errors import ValidationError, HttpError
from rest_framework.authtoken.serializers import AuthTokenSerializer

from .models import Profile
from .schemas import UserRegisterSchema, UserLoginSchema, UserProfileSchema

router = Router()
profile_router = Router()


@router.post("/login", auth=None)
def login(request, user_payload: UserLoginSchema):
    try:
        user_payload = user_payload.dict()
        serializer = AuthTokenSerializer(data=user_payload)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        django_login(request, user)

        knox_data = KnoxLoginView().post(request, format=None).data
        return knox_data

    except Exception as e:
        raise HttpError(400, f"Invalid credentials")


@router.post("/register", auth=None)
def register(request, user_payload: UserRegisterSchema, response=201):
    if user_payload.password != user_payload.password_confirm:
        raise ValidationError([{"Password": "Password does not match"}])

    User = get_user_model()
    email_exist = User.objects.filter(email=user_payload.email).exists()
    if email_exist:
        raise ValidationError([{"Email": "Email already exist"}])

    User.objects.create_user(
        username=user_payload.username,
        email=user_payload.email,
        password=user_payload.password
    )

    return 201


@profile_router.get("", response=UserProfileSchema)
def me(request):
    return Profile.objects.get(user=request.user)


@profile_router.post("")
def create_userprofile(request, image: UploadedFile = File(default=None)):
    user = request.user

    if Profile.objects.filter(user=user).exists():
        raise ValidationError([{"Profile": "Profile already exist"}])

    Profile.objects.create(
        user=user,
        image=image
    )

    return 201


@profile_router.post("/image")
def update_userprofile_image(request, image: UploadedFile = File(...)):
    user = request.user
    profile = get_object_or_404(Profile, user=user)
    profile.image = image
    profile.save()

    return 200


@profile_router.delete("/image")
def delete_userprofile_image(request):
    user = request.user
    profile = Profile.objects.get(user=user)
    profile.image.delete()
    profile.save()

    return 200
