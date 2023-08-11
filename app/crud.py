from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.utils.certificate import make_certificate

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


def get_user_carbon(db: Session, user_id: int):
    return (
        db.query(models.UserCarbon).filter(models.UserCarbon.user_id == user_id).all()
    )


def create_user_carbon(db: Session, user_carbon: schemas.UserCarbonCreate):
    db_user_carbon = models.UserCarbon(
        user_id=user_carbon.user_id,
        carbon_offset=user_carbon.carbon_offset,
        donate_amount=user_carbon.donate_amount,
        fee=user_carbon.fee,
    )
    db.add(db_user_carbon)
    db.commit()
    db.refresh(db_user_carbon)

    db_user = get_user(db, user_id=user_carbon.user_id)
    db_user.xp += 0.2 * user_carbon.donate_amount
    db.commit()
    db.refresh(db_user)

    return db_user_carbon


def get_all_carbon(db: Session):
    all_carbon = db.query(models.UserCarbon).all()
    all_carbon_offset = sum([carbon.carbon_offset for carbon in all_carbon])
    return {"all_carbon_offset": all_carbon_offset, "all_carbon": all_carbon}


def get_news(db: Session):
    return db.query(models.New).all()


def get_news_by_id(db: Session, new_id: int):
    return db.query(models.New).filter(models.New.id == new_id).first()


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
    return (
        db.query(models.Discussion).filter(models.Discussion.board_id == board_id).all()
    )


def create_discussion(db: Session, board_id: int, discussion: schemas.DiscussionCreate):
    discussion_owner = get_user(db, user_id=discussion.owner_id)
    if discussion_owner is None:
        return None
    db_discussion = models.Discussion(
        body=discussion.body, owner_id=discussion.owner_id, board_id=board_id
    )
    db.add(db_discussion)
    db.commit()
    db.refresh(db_discussion)
    return db_discussion


def create_discussion_interaction(
    db: Session,
    discussion_id: int,
    discussion_interaction: schemas.DiscussionInteractionCreate,
):
    discussion_interaction_owner = get_user(db, user_id=discussion_interaction.user_id)
    if discussion_interaction_owner is None:
        return None

    # check if user ever interacted with this discussion
    db_discussion_interaction = (
        db.query(models.DiscussionInteraction)
        .filter(
            models.DiscussionInteraction.user_id == discussion_interaction.user_id,
            models.DiscussionInteraction.discussion_id == discussion_id,
        )
        .first()
    )

    if db_discussion_interaction is None:
        db_discussion_interaction = models.DiscussionInteraction(
            user_id=discussion_interaction.user_id,
            discussion_id=discussion_id,
            interaction_type=discussion_interaction.interaction_type,
        )
        db.add(db_discussion_interaction)
        db.commit()
        db.refresh(db_discussion_interaction)
        return db_discussion_interaction
    else:
        db_discussion_interaction.interaction_type = (
            discussion_interaction.interaction_type
        )
        db.commit()
        db.refresh(db_discussion_interaction)
        return db_discussion_interaction


def get_certificate(name: str, co2_amount: str, date: str, cert_id: str):
    return make_certificate(name, co2_amount, date, cert_id)


def get_cert_by_carbon_id(db: Session, carbon_id: int):
    detail = (
        db.query(models.UserCarbon, models.User)
        .join(models.User, models.UserCarbon.user_id == models.User.id)
        .filter(models.UserCarbon.id == carbon_id)
        .first()
    )
    if detail is None:
        return None
    cert = get_certificate(
        name=detail.User.name + " " + detail.User.lastname,
        co2_amount=str(detail.UserCarbon.carbon_offset),
        date=str(detail.UserCarbon.created_at.strftime("%d/%m/%Y")),
        cert_id="RCC" + str(detail.UserCarbon.id).zfill(10),
    )

    return cert


def upload_new_image(db: Session, new_id: int, image_path: str):
    db_new_image = models.NewImage(image=image_path + ".jpg", new_id=new_id)
    db.add(db_new_image)
    db.commit()
    db.refresh(db_new_image)

    return db_new_image


def get_all_hotels(db: Session):
    return db.query(models.Hotel).all()


def get_cheapest_rooms(db: Session):
    return (
        db.query(models.Room, models.Hotel)
        .join(models.Hotel, models.Room.hotel_id == models.Hotel.hotel_id)
        .order_by(models.Room.price_per_night)
        .all()
    )


def get_info_by_room_id(db: Session, room_id: int):
    return (
        db.query(models.Room, models.Hotel, models.Booking)
        .join(models.Hotel, models.Room.hotel_id == models.Hotel.hotel_id)
        .join(models.Booking, models.Room.room_id == models.Booking.room_id)
        .filter(models.Room.room_id == room_id)
        .first()
    )


def get_available_rooms(db: Session, hotel_id: int):
    return db.query(models.Room).filter(models.Room.hotel_id == hotel_id).all()


def get_bookings_by_user_id(db: Session, user_id: int):
    return db.query(models.Booking).filter(models.Booking.user_id == user_id).all()


def get_all_bookings(db: Session):
    return db.query(models.Booking).all()


def book_room(db: Session, booking: schemas.BookingCreate):
    db_booking = models.Booking(
        user_id=booking.user_id,
        room_id=booking.room_id,
        check_in_date=booking.check_in_date,
        check_out_date=booking.check_out_date,
        guest_name=booking.guest_name,
        guest_email=booking.guest_email,
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)

    if db_booking is None:
        return None

    # update room availability
    db_room = (
        db.query(models.Room).filter(models.Room.room_id == booking.room_id).first()
    )
    db_room.availability -= 1
    db.commit()
    db.refresh(db_room)

    return db_booking


def get_all_events(db: Session):
    return db.query(models.Event).all()


def book_event(db: Session, booking: schemas.EventBookingCreate):
    bookArr = []
    for i in range(booking.amount):
        db_booking = models.EventBooking(
            user_id=booking.user_id,
            event_id=booking.event_id,
            guest_name=booking.guest_name,
            guest_email=booking.guest_email,
        )
        db.add(db_booking)
        db.commit()
        db.refresh(db_booking)
        bookArr.append(db_booking)

    if bookArr is None:
        return None

    # update event availability
    db_event = (
        db.query(models.Event).filter(models.Event.event_id == booking.event_id).first()
    )
    db_event.availability -= booking.amount
    db.commit()
    db.refresh(db_event)

    return bookArr


def get_all_event_bookings(db: Session):
    return db.query(models.EventBooking).all()


def get_summary_hotel(db: Session, hotel_id: int):
    # get sum of all bookings for a hotel
    total_bookings = (
        db.query(func.sum(models.Room.price_per_night))
        .join(models.Booking, models.Room.room_id == models.Booking.room_id)
        .filter(models.Room.hotel_id == hotel_id)
        .scalar()
    )
    return total_bookings


def get_summary_event(db: Session, event_id: int):
    # get sum of all bookings for a hotel
    total_bookings = (
        db.query(func.sum(models.Event.price))
        .join(
            models.EventBooking, models.Event.event_id == models.EventBooking.event_id
        )
        .filter(models.Event.event_id == event_id)
        .scalar()
    )
    return total_bookings


def get_user_booked_event(db: Session, user_id: int):
    return (
        # get with event detail
        db.query(models.Event, models.EventBooking)
        .join(
            models.EventBooking, models.Event.event_id == models.EventBooking.event_id
        )
        .filter(models.EventBooking.user_id == user_id)
        .all()
    )


def get_user_booked_hotel(db: Session, user_id: int):
    return (
        # get with hotel detail
        db.query(models.Hotel, models.Room, models.Booking)
        .join(models.Room, models.Hotel.hotel_id == models.Room.hotel_id)
        .join(models.Booking, models.Room.room_id == models.Booking.room_id)
        .filter(models.Booking.user_id == user_id)
        .all()
    )
