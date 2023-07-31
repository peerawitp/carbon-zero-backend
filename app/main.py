from fastapi import Depends, FastAPI, HTTPException

from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

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

# CORS
origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    tags=["Users"],
)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post(
    "/users",
    response_model=schemas.User,
    summary="Create User",
    tags=["Users"],
)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.post(
    "/login",
    response_model=schemas.LoginResponse,
    summary="Login with Email and Password",
    tags=["Users"],
)
def login(email: str, password: str, db: Session = Depends(get_db)):
    db_user = crud.login_user(db, email=email, password=password)
    if db_user is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return db_user


@app.get(
    "/news", response_model=list[schemas.New], summary="Read All News", tags=["News"]
)
def read_news(db: Session = Depends(get_db)):
    news = crud.get_news(db)
    return news


@app.post(
    "/news", response_model=schemas.NewCreate, summary="Create News", tags=["News"]
)
def create_news(news: schemas.NewCreate, db: Session = Depends(get_db)):
    news = crud.create_news(db=db, news=news)
    if news is None:
        raise HTTPException(status_code=400, detail="Invalid owner_id")
    return news


@app.get(
    "/boards",
    response_model=list[schemas.Board],
    summary="Read All Boards",
    tags=["Boards"],
)
def read_boards(db: Session = Depends(get_db)):
    boards = crud.get_boards(db)
    return boards


@app.get(
    "/boards/{board_id}",
    response_model=schemas.Board,
    summary="Read Board by ID",
    tags=["Boards"],
)
def read_board(board_id: int, db: Session = Depends(get_db)):
    board = crud.get_board_by_id(db, board_id=board_id)
    if board is None:
        raise HTTPException(status_code=404, detail="Board not found")
    return board


@app.post(
    "/boards", response_model=schemas.Board, summary="Create Board", tags=["Boards"]
)
def create_board(board: schemas.BoardCreate, db: Session = Depends(get_db)):
    board = crud.create_board(db=db, board=board)
    if board is None:
        raise HTTPException(status_code=400, detail="Invalid owner_id")
    return board


@app.post(
    "/boards/{board_id}/discussion",
    response_model=schemas.Discussion,
    tags=["Discussions"],
)
def create_discussion(
    board_id: int, discussion: schemas.DiscussionCreate, db: Session = Depends(get_db)
):
    discussion = crud.create_discussion(db=db, board_id=board_id, discussion=discussion)
    if discussion is None:
        raise HTTPException(status_code=400, detail="Invalid owner_id or board_id")
    return discussion


@app.get(
    "/boards/{board_id}/discussions",
    response_model=list[schemas.Discussion],
    tags=["Discussions"],
)
def read_discussions(board_id: int, db: Session = Depends(get_db)):
    discussions = crud.get_discussions_by_board_id(db, board_id=board_id)
    return discussions


@app.post(
    "/discussions/{discussion_id}/interaction",
    response_model=schemas.DiscussionInteraction,
    tags=["Discussions"],
)
def create_discussion_interaction(
    discussion_id: int,
    interaction: schemas.DiscussionInteractionCreate,
    db: Session = Depends(get_db),
):
    interaction = crud.create_discussion_interaction(
        db=db,
        discussion_id=discussion_id,
        discussion_interaction=interaction,
    )
    if interaction is None:
        raise HTTPException(status_code=400, detail="Invalid user_id or discussion_id")
    return interaction
