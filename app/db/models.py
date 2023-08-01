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

    user_type_id = Column(Integer, ForeignKey("user_types.id"), default=1)
    user_type = relationship("UserType", back_populates="users")
    user_carbon = relationship("UserCarbon", back_populates="user")

    news = relationship("New", back_populates="owner")

    boards = relationship("Board", back_populates="owner")
    discussions = relationship("Discussion", back_populates="owner")
    discussion_interactions = relationship(
        "DiscussionInteraction", back_populates="owner"
    )


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

    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="news")


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
