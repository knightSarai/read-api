from ninja import Schema


class UserRegisterSchema(Schema):
    username: str
    email: str
    password: str
    password_confirm: str


class UserOut(Schema):
    id: int
    username: str
    email: str


class UserLoginSchema(Schema):
    username: str
    password: str
