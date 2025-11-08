from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from configs import cfg
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Connect to MongoDB
try:
    client = MongoClient(cfg.MONGO_URI)
    # Ping to verify connection
    client.admin.command('ping')
    logging.info("Connected to MongoDB successfully.")
except ConnectionFailure:
    logging.error("Failed to connect to MongoDB. Check MONGO_URI.")
    raise

# Collections
users = client['main']['users']
groups = client['main']['groups']

def already_db(user_id):
    """Check if user exists."""
    try:
        user = users.find_one({"user_id": user_id})
        return user is not None
    except Exception as e:
        logging.error(f"Error checking user {user_id}: {e}")
        return False

def already_dbg(chat_id):
    """Check if group exists."""
    try:
        group = groups.find_one({"chat_id": chat_id})
        return group is not None
    except Exception as e:
        logging.error(f"Error checking group {chat_id}: {e}")
        return False

def add_user(user_id):
    """Add user if not exists."""
    if already_db(user_id):
        return
    try:
        users.insert_one({"user_id": user_id})
        logging.info(f"Added user {user_id}")
    except Exception as e:
        logging.error(f"Error adding user {user_id}: {e}")

def remove_user(user_id):
    """Remove user if exists."""
    if not already_db(user_id):
        return
    try:
        users.delete_one({"user_id": user_id})
        logging.info(f"Removed user {user_id}")
    except Exception as e:
        logging.error(f"Error removing user {user_id}: {e}")

def add_group(chat_id):
    """Add group if not exists."""
    if already_dbg(chat_id):
        return
    try:
        groups.insert_one({"chat_id": chat_id})
        logging.info(f"Added group {chat_id}")
    except Exception as e:
        logging.error(f"Error adding group {chat_id}: {e}")

def all_users():
    """Return total user count."""
    try:
        return users.count_documents({})
    except Exception as e:
        logging.error(f"Error counting users: {e}")
        return 0

def all_groups():
    """Return total group count."""
    try:
        return groups.count_documents({})
    except Exception as e:
        logging.error(f"Error counting groups: {e}")
        return 0
