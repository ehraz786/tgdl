# copyright 2023 © Xron Trix | https://github.com/Xrontrix10

import asyncio
import logging
import json
from pyrogram import Client

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

# Create Pyrogram client
colab_bot = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
