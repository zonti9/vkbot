import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
CHAT_ID = os.getenv("CHAT_ID")
DEFAULT = f"mysql://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
TORTOISE_ORM = {
    "connections": {"default": DEFAULT},
    "apps": {
        "models": {
            "models": ["models"],
            "default_connection": "default",
        },
    },
}
