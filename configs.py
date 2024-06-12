import os
import logging

logging.basicConfig(
    format='%(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('log.txt'),
              logging.StreamHandler()],
    level=logging.INFO
)

class Config(object):
    API_ID = int(os.environ.get("API_ID", "23032012"))
    API_HASH = os.environ.get("API_HASH", "5e47a644cc456147dbc79a24511c4dbb")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "7264263787:AAFRNuk6CqcCimZ45eya6ZWKJs60tMJQkoQ")
    DOWNLOAD_DIR = os.environ.get("DOWNLOAD_DIR", "./Downloads")
    LOGGER = logging
    OWNER_ID = int(os.environ.get("OWNER_ID", 6704116482))
    PRO_USERS = list(set(int(x) for x in os.environ.get("PRO_USERS", "1391556668 5162208212").split()))
    PRO_USERS.append(OWNER_ID)
    MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb+srv://rename:rename@cluster0.uzqu6ce.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1002174622934"))
    BROADCAST_AS_COPY = bool(os.environ.get("BROADCAST_AS_COPY", "False"))
    ALLOW_UPLOAD_TO_STREAMTAPE = bool(os.environ.get("ALLOW_UPLOAD_TO_STREAMTAPE", True))
    STREAMTAPE_API_PASS = os.environ.get("STREAMTAPE_API_PASS", "zM4WB3RxQeIogb")
    STREAMTAPE_API_USERNAME = os.environ.get("STREAMTAPE_API_USERNAME", "d1cf7f6a67162eacdd77")
    WEBHOOK = bool(os.environ.get("WEBHOOK", True))
