from PIL import Image, ImageFont, ImageDraw
import os
from io import BytesIO
import base64


def make_certificate(name: str, co2_amount: str, date: str, cert_id: str):
    my_path = os.path.dirname(__file__)

    MAIN_FONT = my_path + r"/../assets/font/Alegreya.ttf"
    OTHER_FONT = my_path + r"/../assets/font/OpenSans.ttf"
    NAME_COLOR = "#C8931D"
    CO2_AMOUNT_COLOR = "#C8931D"
    DATE_COLOR = "#6F4C00"
    CERT_ID_COLOR = "#6F4C00"

    TEMPLATE = Image.open(my_path + r"/../assets/cert_template.png")
    WIDTH, HEIGHT = TEMPLATE.size

    name_font = ImageFont.truetype(MAIN_FONT, 100)
    co2_amount_font = ImageFont.truetype(MAIN_FONT, 60)
    date_font = ImageFont.truetype(OTHER_FONT, 28)
    cert_id_font = ImageFont.truetype(OTHER_FONT, 32)

    d = ImageDraw.Draw(TEMPLATE)

    name = name.upper()
    w, h = d.textsize(name, font=name_font)
    d.text(((WIDTH - w) / 2, HEIGHT / 2 - 120), name, fill=NAME_COLOR, font=name_font)

    co2_amount += " KGS CO2"
    w, h = d.textsize(co2_amount, font=co2_amount_font)
    d.text(
        ((WIDTH - w) / 2, HEIGHT / 2 + 90),
        co2_amount,
        fill=CO2_AMOUNT_COLOR,
        font=co2_amount_font,
    )

    d.text(
        (WIDTH / 2 - 840, HEIGHT / 2 - 560),
        date,
        fill=DATE_COLOR,
        font=date_font,
    )

    d.text(
        (WIDTH / 2 - 640, HEIGHT / 2 + 440),
        cert_id,
        fill=CERT_ID_COLOR,
        font=cert_id_font,
    )

    buffer = BytesIO()
    TEMPLATE.save(buffer, format="PNG")
    buffer.seek(0)

    base64_encoded_image = base64.b64encode(buffer.getvalue()).decode()

    return base64_encoded_image
