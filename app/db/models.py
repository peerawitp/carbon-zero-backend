from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)

    name = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    mobile_phone = Column(String, nullable=False)

    user_type_id = Column(Integer, ForeignKey("user_types.id"), default=1)
    user_type = relationship("UserType", back_populates="users")


class UserType(Base):
    __tablename__ = "user_types"

    id = Column(Integer, primary_key=True, index=True)  # 0: admin, 1: user
    name = Column(String)

    users = relationship("User", back_populates="user_type")


class New(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    location = Column(String)
    description = Column(String)
    join_detail = Column(String)

    owner_id = Column(Integer, ForeignKey("users.id"))
