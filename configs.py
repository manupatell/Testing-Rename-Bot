import os, environ
import logging

logging.basicConfig(
    format='%(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('log.txt'),
              logging.StreamHandler()],
    level=logging.INFO
)


class Config(object):
    API_ID = int(os.environ.get("API_ID", "11973721"))
    API_HASH = os.environ.get("API_HASH", "5264bf4663e9159565603522f58d3c18")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "6809904281:AAGdbV-NFrCtnNhwhXoBuXdDJf-evqRUkec")
    DOWNLOAD_DIR = os.environ.get("DOWNLOAD_DIR", "./downloads")
    LOGGER = logging
    OWNER_ID = int(os.environ.get("OWNER_ID", 1391556668))
    ADMINS = int(os.environ.get("ADMINS", 1391556668))
    PRO_USERS = list(set(int(x) for x in os.environ.get("PRO_USERS", "1391556668 5162208212").split()))
    PRO_USERS.append(OWNER_ID)
    MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb+srv://KarthikMovies:KarthikUK007@cluster0.4l5byki.mongodb.net/?retryWrites=true&w=majority")
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1001821439025"))
    FORCESUB_CHANNEL = os.environ.get("FORCESUB_CHANNEL", "Star_Bots_Tamil")
    BROADCAST_AS_COPY = bool(os.environ.get("BROADCAST_AS_COPY", "False"))
    WEBHOOK = bool(os.environ.get("WEBHOOK", True))
    BANNED_USERS = set(int(x) for x in environ.get("BANNED_USERS", "").split())
    DOWNLOAD_LOCATION = "./Downloads"
    MAX_FILE_SIZE = 4194304000
    TG_MAX_FILE_SIZE = 4194304000
    FREE_USER_MAX_FILE_SIZE = 4194304000
    CHUNK_SIZE = int(environ.get("CHUNK_SIZE", 128))
    HTTP_PROXY = environ.get("HTTP_PROXY", "")
    OUO_IO_API_KEY = ""
    MAX_MESSAGE_LENGTH = 4096
    PROCESS_MAX_TIMEOUT = 0
    DEF_WATER_MARK_FILE = ""
    LOGGER = logging
    lazydownloaders = [int(lazydownloaders) if id_pattern.search(lazydownloaders) else lazydownloaders for lazydownloaders in environ.get('PRIME_DOWNLOADERS', '1391556668').split()]
    PRIME_DOWNLOADERS = (lazydownloaders) if lazydownloaders else []
    
