from sqlalchemy.orm import Session

from .db import models, schemas

from .utils import authentication as auth


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def get_user_type(db: Session):
    return db.query(models.UserType).all()


def login_user(db: Session, email: str, password: str):
    db_user = get_user_by_email(db, email=email)
    if db_user is None:
        return None
    if not auth.verify_password(password, db_user.hashed_password):
        return None
    token = auth.get_access_token({"sub": db_user.id})
    return {"access_token": token, "data": db_user}


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        email=user.email,
        hashed_password=auth.get_password_hash(user.password),
        name=user.name,
        lastname=user.lastname,
        mobile_phone=user.mobile_phone,
        user_type_id=1,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_news(db: Session):
    return db.query(models.New).all()


def create_news(db: Session, news: schemas.NewCreate):
    new_owner = get_user(db, user_id=news.owner_id)
    if new_owner is None:
        return None
    db_news = models.New(
        title=news.title,
        location=news.location,
        description=news.description,
        join_detail=news.join_detail,
        owner_id=news.owner_id,
    )
    db.add(db_news)
    db.commit()
    db.refresh(db_news)
    return db_news


def get_boards(db: Session):
    return db.query(models.Board).all()


def get_board_by_id(db: Session, board_id: int):
    return db.query(models.Board).filter(models.Board.id == board_id).first()


def create_board(db: Session, board: schemas.BoardCreate):
    board_owner = get_user(db, user_id=board.owner_id)
    if board_owner is None:
        return None
    db_board = models.Board(
        title=board.title,
        body=board.body,
        owner_id=board.owner_id,
    )
    db.add(db_board)
    db.commit()
    db.refresh(db_board)
    return db_board


def get_discussions_by_board_id(db: Session, board_id: int):
    return db.query(models.Discussion).filter(models.Discussion.board_id == board_id)
