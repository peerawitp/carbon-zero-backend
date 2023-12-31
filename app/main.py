from fastapi import Depends, FastAPI, HTTPException, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse

from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session

import base64
import io
import random
import string

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
    version="1.2.0",
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

app.mount("/imgs", StaticFiles(directory="app/imgs"), name="imgs")


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
    "/carbon",
    response_model=list[schemas.UserCarbon],
    summary="Read User Carbon",
    tags=["Carbon"],
)
def read_user_carbon(user_id: int, db: Session = Depends(get_db)):
    user_carbon = crud.get_user_carbon(db, user_id=user_id)
    if user_carbon is None:
        raise HTTPException(status_code=404, detail="No donate not found")
    return user_carbon


@app.post(
    "/carbon",
    response_model=schemas.UserCarbon,
    summary="Create User Carbon Donate",
    tags=["Carbon"],
)
def create_user_carbon(
    user_carbon: schemas.UserCarbonCreate, db: Session = Depends(get_db)
):
    user_carbon = crud.create_user_carbon(db=db, user_carbon=user_carbon)
    if user_carbon is None:
        raise HTTPException(status_code=400, detail="Invalid user_id")
    return user_carbon


# get all sum carbon offset
@app.get("/carbon/all", summary="Get All Carbon Details", tags=["Carbon"])
def get_all_carbon(db: Session = Depends(get_db)):
    all_carbon = crud.get_all_carbon(db)
    return all_carbon


@app.get(
    "/news", response_model=list[schemas.New], summary="Read All News", tags=["News"]
)
def read_news(db: Session = Depends(get_db)):
    news = crud.get_news(db)
    return news


@app.post("/news", response_model=schemas.New, summary="Create News", tags=["News"])
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


@app.get(
    "/cert",
    summary="Get Certificate",
    tags=["Certificate"],
    response_class=FileResponse,
)
def get_certificate(name: str, co2_amount: str, date: str, cert_id: str):
    base64_encoded_image = crud.get_certificate(name, co2_amount, date, cert_id)
    base64_decoded_image = base64.b64decode(base64_encoded_image)
    return StreamingResponse(io.BytesIO(base64_decoded_image), media_type="image/png")


@app.get(
    "/cert/{carbon_id}", summary="Get Certificate with carbon_id", tags=["Certificate"]
)
def get_cert_by_carbon_id(carbon_id: int, db: Session = Depends(get_db)):
    cert = crud.get_cert_by_carbon_id(db, carbon_id)
    if cert is None:
        raise HTTPException(status_code=404, detail="Certificate not found")
    base64_decoded_image = base64.b64decode(cert)
    return StreamingResponse(io.BytesIO(base64_decoded_image), media_type="image/png")


@app.post(
    "/uploadNewImage",
    summary="Upload New Image",
    tags=["Upload"],
)
def upload_new_image(
    news_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    check = crud.get_news_by_id(db, news_id)
    if check is None:
        raise HTTPException(status_code=404, detail="News not found")

    if file.content_type not in ["image/jpeg", "image/jpg"]:
        raise HTTPException(
            status_code=400, detail="Invalid file type, only jpeg accept"
        )

    uploadname = "new_" + "".join(random.choices(string.ascii_lowercase, k=10))
    if file:
        with open(f"app/imgs/{uploadname}.jpg", "wb") as buffer:
            buffer.write(file.file.read())

        upload = crud.upload_new_image(db, news_id, uploadname)

    return upload


@app.get(
    "/hotels",
    summary="Get All Hotels",
    tags=["Hotels"],
)
def get_all_hotels(db: Session = Depends(get_db)):
    hotels = crud.get_all_hotels(db)
    get_cheapest_rooms = crud.get_cheapest_rooms(db)

    return {"hotels": hotels, "cheapest_rooms": get_cheapest_rooms}


@app.get(
    "/availableRooms/{hotel_id}",
    summary="Get Available Rooms",
    tags=["Hotels"],
    response_model=list[schemas.Room],
)
def get_available_rooms(hotel_id: int, db: Session = Depends(get_db)):
    rooms = crud.get_available_rooms(db, hotel_id)
    return rooms


@app.get(
    "/getRoomInfo/{room_id}",
    summary="Get Info by Room ID",
    tags=["Hotels"],
)
def get_info_by_room_id(room_id: int, db: Session = Depends(get_db)):
    info = crud.get_info_by_room_id(db, room_id)
    return info


@app.get(
    "/bookings/{user_id}",
    summary="Get Bookings",
    tags=["Bookings"],
    response_model=list[schemas.Booking],
)
def get_bookings_by_user_id(user_id: int, db: Session = Depends(get_db)):
    bookings = crud.get_bookings_by_user_id(db, user_id)
    return bookings


@app.get(
    "/bookings",
    summary="Get All Bookings",
    tags=["Bookings"],
    response_model=list[schemas.Booking],
)
def get_all_bookings(db: Session = Depends(get_db)):
    bookings = crud.get_all_bookings(db)
    return bookings


@app.get("/summaryHotel/{hotel_id}", summary="Get Summary of Hotel", tags=["Hotels"])
def get_summary_hotel(hotel_id: int, db: Session = Depends(get_db)):
    summary = crud.get_summary_hotel(db, hotel_id)
    return {"summary_income": summary}


@app.post(
    "/book",
    summary="Book Room",
    tags=["Bookings"],
    response_model=schemas.Booking,
)
def book_room(booking: schemas.BookingCreate, db: Session = Depends(get_db)):
    booking = crud.book_room(db, booking)
    return booking


@app.get("/events", summary="Get All Events", tags=["Events"])
def get_all_events(db: Session = Depends(get_db)):
    events = crud.get_all_events(db)
    return events


@app.post(
    "/bookEvent",
    summary="Book Event",
    tags=["Events"],
    response_model=list[schemas.EventBooking],
)
def book_event(event: schemas.EventBookingCreate, db: Session = Depends(get_db)):
    event = crud.book_event(db, event)
    return event


@app.get(
    "/getAllEventBookings",
    summary="Get All Event Bookings",
    tags=["Events"],
    response_model=list[schemas.EventBooking],
)
def get_all_event_bookings(db: Session = Depends(get_db)):
    event_bookings = crud.get_all_event_bookings(db)
    return event_bookings


@app.get("/summaryEvent/{event_id}", summary="Get Summary of Event", tags=["Events"])
def get_summary_event(event_id: int, db: Session = Depends(get_db)):
    summary = crud.get_summary_event(db, event_id)
    return {"summary_income": summary}


@app.get(
    "/getUserBookedEvent/{user_id}",
    summary="Get User Booked Event",
    tags=["Users"],
)
def get_user_booked_event(user_id: int, db: Session = Depends(get_db)):
    events = crud.get_user_booked_event(db, user_id)
    return events

@app.get("/getUserBookedHotel/{user_id}", summary="Get User Booked Hotel", tags=["Users"])
def get_user_booked_hotel(user_id: int, db: Session = Depends(get_db)):
    hotels = crud.get_user_booked_hotel(db, user_id)
    return hotels