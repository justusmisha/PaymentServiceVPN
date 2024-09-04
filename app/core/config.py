import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

load_dotenv()

SERVICE_TEST = True
TRAFFIC_TEST = True

API_HOST = str(os.getenv("API_HOST"))

YOOKASSA_API_URL = "https://api.yookassa.ru/v3/payments"

if SERVICE_TEST:
    YOOKASSA_SHOP_ID = str(os.getenv("TEST_YOOKASSA_SHOP_ID"))
    YOOKASSA_API_KEY = str(os.getenv("TEST_YOOKASSA_API_KEY"))
else:
    YOOKASSA_SHOP_ID = str(os.getenv("YOOKASSA_SHOP_ID"))
    YOOKASSA_API_KEY = str(os.getenv("YOOKASSA_API_KEY"))

CRYPTOMUS_API_URL = "https://api.cryptomus.com/v1/payment"
CRYPTOMUS_MERCHANT_ID = str(os.getenv("CRYPTOMUS_MERCHANT_ID"))
CRYPTOMUS_API_KEY = str(os.getenv("CRYPTOMUS_API_KEY"))
CRYPTOMUS_URL_CALLBACK = str(os.getenv("CRYPTOMUS_URL_CALLBACK"))

CREATING_LINK_KEY = str(os.getenv("CREATING_LINK_KEY"))

TEST_PRICE = 1
if SERVICE_TEST:
    TEST_DAYS = 0
else:
    TEST_DAYS = 7

VLESS_USERNAME = str(os.getenv("VLESS_USERNAME"))
VLESS_PASSWORD = str(os.getenv("VLESS_PASSWORD"))
VLESS_PORT = str(os.getenv("VLESS_PORT"))

if SERVICE_TEST:
    DEFAULT_TRAFFIC_LIMIT_MB = 1000
    FAMILY_TRAFFIC_LIMIT_MB = 7000
    TRAFFIC_TEST_LIMIT_MB = 7000
else:
    DEFAULT_TRAFFIC_LIMIT_MB = 150000
    FAMILY_TRAFFIC_LIMIT_MB = 750000
    TRAFFIC_TEST_LIMIT_MB = 20000000

YOOKASSA_CAPTURE = True
YOOKASSA_DESCRIPTION = "Продление подписки Liberty"

VPN_START_LINK = "?start="
VPN_SECOND_START_LINK = ""


X_WEEBHOK_SECRET = str(os.getenv("X_WEEBHOK_SECRET"))
REACHED_DAYS_LEFT = 3
REACHED_USAGE = 80

MARZBAN_URL = str(os.getenv("MARZBAN_URL"))
MARZBAN_USERNAME = str(os.getenv("MARZBAN_USERNAME"))
MARZBAN_PASSWORD = str(os.getenv("MARZBAN_PASSWORD"))


RABBITMQ_USER = str(os.getenv("RABBITMQ_USER"))
RABBITMQ_PASS = str(os.getenv("RABBITMQ_PASS"))
RABBITMQ_HOST = str(os.getenv("RABBITMQ_HOST"))
RABBITMQ_URL = f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}/"


DB_USER = str(os.getenv("DB_USER"))
DB_PASSWORD = str(os.getenv("DB_PASSWORD"))
DB_NAME = str(os.getenv("DB_NAME"))
DB_HOST = str(os.getenv("DB_HOST"))
DB_PORT = str(os.getenv("DB_PORT"))
DATABASE_URL_ASYNC = f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
DATABASE_URL_SYNC = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'

async_engine = create_async_engine(DATABASE_URL_ASYNC, echo=True)
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)
