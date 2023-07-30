from pydantic import BaseModel


class User(BaseModel):
    id: int
    email: str
    _hashed_password: str
    name: str
    lastname: str
    mobile_phone: str
    user_type_id: int

    class Config:
        underscore_attrs_are_private = True
        orm_mode = True


class UserCreate(BaseModel):
    email: str
    password: str
    name: str
    lastname: str
    mobile_phone: str

    class Config:
        orm_mode = True


class LoginResponse(BaseModel):
    access_token: str
    data: User


class New(BaseModel):
    id: int
    title: str
    location: str
    description: str
    join_detail: str
    owner_id: int

    class Config:
        orm_mode = True


class NewCreate(BaseModel):
    title: str
    location: str
    description: str
    join_detail: str
    owner_id: int

    class Config:
        orm_mode = True
