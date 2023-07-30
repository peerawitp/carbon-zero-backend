from fastapi import Depends, FastAPI, HTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware
from sqlalchemy.orm import Session

from . import crud
from .db import models
from .db import schemas

from .db.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

# Create user types if not exists
# 0: admin, 1: user
userType = crud.get_user_type(SessionLocal())
if len(userType) == 0:
    db = SessionLocal()
    db_user_type = models.UserType(id=0, name="admin")
    db.add(db_user_type)
    db.commit()
    db.refresh(db_user_type)
    db_user_type = models.UserType(id=1, name="user")
    db.add(db_user_type)
    db.commit()
    db.refresh(db_user_type)
    db.close()

# Initial FastAPI
app = FastAPI(
    title="carbon-zero-backend",
    version="1.0.0",
    description="very very urgent project :3",
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get(
    "/users/{user_id}",
    response_model=schemas.User,
    summary="Read User by ID",
)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post(
    "/users/",
    response_model=schemas.User,
    summary="Create User",
)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.post(
    "/login/",
    response_model=schemas.LoginResponse,
    summary="Login with Email and Password",
)
def login(email: str, password: str, db: Session = Depends(get_db)):
    db_user = crud.login_user(db, email=email, password=password)
    if db_user is None:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    return db_user


@app.get("/news/", response_model=list[schemas.New], summary="Read All News")
def read_news(db: Session = Depends(get_db)):
    news = crud.get_news(db)
    return news


@app.post("/news/", response_model=schemas.NewCreate)
def create_news(news: schemas.NewCreate, db: Session = Depends(get_db)):
    news = crud.create_news(db=db, news=news)
    if news is None:
        raise HTTPException(status_code=400, detail="Incorrent owner_id")
    return news


origins = ["*"]
app = CORSMiddleware(
    app,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
