from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class User(BaseModel):
    id: int
    email: str
    _hashed_password: str
    name: str
    lastname: str
    mobile_phone: str
    user_type_id: int
    xp: int

    user_carbon: list

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


class UserCarbon(BaseModel):
    id: int
    user_id: int
    carbon_offset: float
    donate_amount: float
    fee: float

    created_at: datetime

    class Config:
        orm_mode = True


class UserCarbonCreate(BaseModel):
    user_id: int
    carbon_offset: float
    donate_amount: float
    fee: float

    class Config:
        orm_mode = True


class New(BaseModel):
    id: int
    title: str
    location: str
    description: str
    join_detail: str
    owner_id: int

    images: list

    created_at: datetime

    class Config:
        orm_mode = True


class NewImage(BaseModel):
    id: int
    new_id: int
    image: str

    created_at: datetime

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


class Board(BaseModel):
    id: int
    title: str
    body: str
    owner_id: int
    created_at: datetime

    discussions: list

    class Config:
        orm_mode = True


class BoardCreate(BaseModel):
    title: str
    body: str
    owner_id: int

    class Config:
        orm_mode = True


class Discussion(BaseModel):
    id: int
    body: str
    owner_id: int
    board_id: int

    details: list

    created_at: datetime

    class Config:
        orm_mode = True


class DiscussionCreate(BaseModel):
    body: str
    owner_id: int

    class Config:
        orm_mode = True


class DiscussionInteraction(BaseModel):
    id: int
    discussion_id: int
    user_id: int
    interaction_type: str

    created_at: datetime

    class Config:
        orm_mode = True


class DiscussionInteractionCreate(BaseModel):
    discussion_id: int
    user_id: int
    interaction_type: str

    class Config:
        orm_mode = True


class FacilityBase(BaseModel):
    name: str


class FacilityCreate(FacilityBase):
    pass


class Facility(FacilityBase):
    facility_id: int

    class Config:
        orm_mode = True


class HotelBase(BaseModel):
    name: str
    stars: int
    rating: int
    address: str
    city: str
    country: str
    description: str


class HotelCreate(HotelBase):
    pass


class Hotel(HotelBase):
    hotel_id: int
    facilities: List[Facility] = []

    class Config:
        orm_mode = True


class RoomBase(BaseModel):
    room_type: str
    price_per_night: int
    availability: int


class RoomCreate(RoomBase):
    pass


class Room(RoomBase):
    room_id: int
    hotel_id: int

    class Config:
        orm_mode = True


class BookingBase(BaseModel):
    room_id: int
    user_id: int
    check_in_date: datetime
    check_out_date: datetime
    guest_name: str
    guest_email: str


class BookingCreate(BookingBase):
    pass


class Booking(BookingBase):
    booking_id: int

    class Config:
        orm_mode = True


class EventBase(BaseModel):
    event_type: str
    name: str
    description: str
    location: str
    start_date: datetime
    end_date: datetime
    image: Optional[str]
    price: int
    capacity: int
    availability: int


class EventCreate(EventBase):
    pass


class Event(EventBase):
    event_id: int

    class Config:
        orm_mode = True


class EventBookingBase(BaseModel):
    event_id: int
    user_id: int
    guest_name: str
    guest_email: str


class EventBookingCreate(EventBookingBase):
    amount: int
    pass


class EventBooking(EventBookingBase):
    booking_id: int

    class Config:
        orm_mode = True
