# copyright 2023 © Xron Trix | https://github.com/Xrontrix10

import asyncio
import logging
import json
from pyrogram import Client
from uvloop import install

# Setup logging
logging.basicConfig(level=logging.INFO)

# Load credentials
with open("/content/tgdl/credentials.json", "r") as file:
    credentials = json.load(file)

API_ID = credentials["API_ID"]
API_HASH = credentials["API_HASH"]
BOT_TOKEN = credentials["BOT_TOKEN"]
OWNER = credentials["USER_ID"]
DUMP_ID = credentials["DUMP_ID"]

# Ensure event loop exists before uvloop install
try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

# Now safely install uvloop
try:
    install()
except Exception as e:
    logging.warning(f"uvloop could not be installed: {e}")

# Create Pyrogram client
colab_bot = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
