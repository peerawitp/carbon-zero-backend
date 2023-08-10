from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)

    name = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    mobile_phone = Column(String, nullable=False)

    xp = Column(Integer, default=0)

    user_type_id = Column(Integer, ForeignKey("user_types.id"), default=1)
    user_type = relationship("UserType", back_populates="users")
    user_carbon = relationship("UserCarbon", back_populates="user")

    news = relationship("New", back_populates="owner")

    boards = relationship("Board", back_populates="owner")
    discussions = relationship("Discussion", back_populates="owner")
    discussion_interactions = relationship(
        "DiscussionInteraction", back_populates="owner"
    )

    booking = relationship("Booking", back_populates="owner")


class UserType(Base):
    __tablename__ = "user_types"

    id = Column(Integer, primary_key=True, index=True)  # 0: admin, 1: user
    name = Column(String)

    users = relationship("User", back_populates="user_type")


class UserCarbon(Base):
    __tablename__ = "user_carbon"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="user_carbon")

    carbon_offset = Column(Float)
    donate_amount = Column(Float)
    fee = Column(Float)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)


class New(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    location = Column(String)
    description = Column(String)
    join_detail = Column(String)

    images = relationship("NewImage", back_populates="new")

    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="news")


class NewImage(Base):
    __tablename__ = "new_images"

    id = Column(Integer, primary_key=True, index=True)
    image = Column(String)

    new_id = Column(Integer, ForeignKey("news.id"))
    new = relationship("New", back_populates="images")

    created_at = Column(DateTime, server_default=func.now(), nullable=False)


class Board(Base):
    __tablename__ = "boards"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    body = Column(String)

    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="boards")

    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    discussions = relationship("Discussion", back_populates="board")


class Discussion(Base):
    __tablename__ = "discussions"

    id = Column(Integer, primary_key=True, index=True)
    body = Column(String)

    owner_id = Column(Integer, ForeignKey("users.id"))
    board_id = Column(Integer, ForeignKey("boards.id"))

    details = relationship("DiscussionInteraction", back_populates="discussion")

    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    owner = relationship("User", back_populates="discussions")
    board = relationship("Board", back_populates="discussions")


class DiscussionInteraction(Base):
    __tablename__ = "discussion_interactions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    discussion_id = Column(Integer, ForeignKey("discussions.id"))
    interaction_type = Column(String)  # dislike, like

    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    owner = relationship("User", back_populates="discussion_interactions")
    discussion = relationship("Discussion", back_populates="details")


class Hotel(Base):
    __tablename__ = "hotels"

    hotel_id = Column(Integer, primary_key=True)
    name = Column(String)
    stars = Column(Integer)
    rating = Column(Integer)
    address = Column(String)
    city = Column(String)
    country = Column(String)
    description = Column(String)

    facilities = relationship("Facility", secondary="hotel_facilities")


class Facility(Base):
    __tablename__ = "facilities"

    facility_id = Column(Integer, primary_key=True)
    name = Column(String)


class HotelFacility(Base):
    __tablename__ = "hotel_facilities"

    hotel_id = Column(Integer, ForeignKey("hotels.hotel_id"), primary_key=True)
    facility_id = Column(
        Integer, ForeignKey("facilities.facility_id"), primary_key=True
    )


class Room(Base):
    __tablename__ = "rooms"

    room_id = Column(Integer, primary_key=True)
    hotel_id = Column(Integer, ForeignKey("hotels.hotel_id"))
    room_type = Column(String)
    price_per_night = Column(Integer)
    availability = Column(Integer)


class Booking(Base):
    __tablename__ = "bookings"

    booking_id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey("rooms.room_id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    check_in_date = Column(DateTime)
    check_out_date = Column(DateTime)
    guest_name = Column(String)
    guest_email = Column(String)

    owner = relationship("User", back_populates="booking")
