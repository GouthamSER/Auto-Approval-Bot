from os import getenv
import logging

# Set up basic logging
logging.basicConfig(level=logging.INFO)

class Config:
    def __init__(self):
        # API credentials
        self.API_ID = int(getenv("API_ID", "0"))
        if self.API_ID == 0:
            logging.error("API_ID is not set or invalid. Please set it in environment variables.")
            raise ValueError("API_ID required")
        
        self.API_HASH = getenv("API_HASH", "")
        if not self.API_HASH:
            logging.error("API_HASH is not set. Please set it in environment variables.")
            raise ValueError("API_HASH required")
        
        self.BOT_TOKEN = getenv("BOT_TOKEN", "")
        if not self.BOT_TOKEN:
            logging.error("BOT_TOKEN is not set. Please set it in environment variables.")
            raise ValueError("BOT_TOKEN required")
        
        # Channel ID
        self.CHID = int(getenv("CHID", "0"))
        if self.CHID == 0:
            logging.warning("CHID is not set. Force-subscribe checks will fail.")
        
        # Sudo users
        sudo_str = getenv("SUDO", "")
        if sudo_str:
            try:
                self.SUDO = list(map(int, sudo_str.split(",")))
            except ValueError:
                logging.error("SUDO contains invalid user IDs. Please provide comma-separated integers.")
                self.SUDO = []
        else:
            logging.warning("SUDO is not set. No admin commands will be available.")
            self.SUDO = []
        
        # MongoDB URI
        self.MONGO_URI = getenv("MONGO_URI", "")
        if not self.MONGO_URI:
            logging.warning("MONGO_URI is not set. Database operations may fail.")

cfg = Config()
