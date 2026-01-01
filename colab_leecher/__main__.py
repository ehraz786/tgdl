import logging, os
from pyrogram import filters
from datetime import datetime
from asyncio import sleep, get_event_loop
from colab_leecher import colab_bot, OWNER
from colab_leecher.utility.handler import cancelTask
from .utility.variables import BOT, MSG, BotTimes, Paths
from .utility.task_manager import taskScheduler, task_starter
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from .utility.helper import isLink, setThumbnail, message_deleter, send_settings


src_request_msg = None


@colab_bot.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await message.delete()
    text = "**Hey There, 👋🏼 It's Colab Leecher**\n\n◲ I am a Powerful File Transloading Bot 🚀\n◲ I can Transfer Files To Telegram or Your Google Drive From Various Sources 🦐"
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Repository 🦄",
                    url="https://github.com/pasindu2580/tgdl",
                ),
                InlineKeyboardButton("Support 💝", url="https://t.me/Colab_Leecher"),
            ],
        ]
    )
    await message.reply_text(text, reply_markup=keyboard)


@colab_bot.on_message(filters.command("tupload") & filters.private)
async def telegram_upload(client, message):
    global BOT, src_request_msg
    BOT.Mode.mode = "leech"
    BOT.Mode.ytdl = False

    text = "<b>⚡ Send Me DOWNLOAD LINK(s) 🔗»</b>\n\n🦀 Follow the below pattern\n\n<code>https//linktofile1.mp4\nhttps//linktofile2.mp4\n[Custom name space.mp4]\n{Password for zipping}\n(Password for unzip)</code>"

    src_request_msg = await task_starter(message, text)


@colab_bot.on_message(filters.command("gdupload") & filters.private)
async def drive_upload(client, message):
    global BOT, src_request_msg
    BOT.Mode.mode = "mirror"
    BOT.Mode.ytdl = False

    text = "<b>⚡ Send Me DOWNLOAD LINK(s) 🔗»</b>\n\n🦀 Follow the below pattern\n\n<code>https//linktofile1.mp4\nhttps//linktofile2.mp4\n[Custom name space.mp4]\n{Password for zipping}\n(Password for unzip)</code>"

    src_request_msg = await task_starter(message, text)


@colab_bot.on_message(filters.command("drupload") & filters.private)
async def directory_upload(client, message):
    global BOT, src_request_msg
    BOT.Mode.mode = "dir-leech"
    BOT.Mode.ytdl = False

    text = "<b>⚡ Send Me FOLDER PATH 🔗»</b>\n\n🦀 Below is an example\n\n<code>/home/user/Downloads/bot</code>"

    src_request_msg = await task_starter(message, text)


@colab_bot.on_message(filters.command("ytupload") & filters.private)
async def yt_upload(client, message):
    global BOT, src_request_msg
    BOT.Mode.mode = "leech"
    BOT.Mode.ytdl = True

    text = "<b>⚡ Send YTDL DOWNLOAD LINK(s) 🔗»</b>\n\n🦀 Follow the below pattern\n\n<code>https//linktofile1.mp4\nhttps//linktofile2.mp4\n[Custom name space.mp4]\n{Password for zipping}</code>"

    src_request_msg = await task_starter(message, text)


@colab_bot.on_message(filters.command("settings") & filters.private)
async def settings(client, message):
    if message.chat.id == OWNER:
        await message.delete()
        await send_settings(client, message, message.id, True)


@colab_bot.on_message(filters.reply)
async def setPrefix(client, message):
    global BOT, SETTING
    if BOT.State.prefix:
        BOT.Setting.prefix = message.text
        BOT.State.prefix = False

        await send_settings(client, message, message.reply_to_message_id, False)
        await message.delete()
    elif BOT.State.suffix:
        BOT.Setting.suffix = message.text
        BOT.State.suffix = False

        await send_settings(client, message, message.reply_to_message_id, False)
        await message.delete()


@colab_bot.on_message(filters.create(isLink) & ~filters.photo)
async def handle_url(client, message):
    global BOT

    # Reset
    BOT.Options.custom_name = ""
    BOT.Options.zip_pswd = ""
    BOT.Options.unzip_pswd = ""

    if src_request_msg:
        await src_request_msg.delete()
    if BOT.State.task_going == False and BOT.State.started:
        temp_source = message.text.splitlines()

        # Check for arguments in message
        for _ in range(3):
            if temp_source[-1][0] == "[":
                BOT.Options.custom_name = temp_source[-1][1:-1]
                temp_source.pop()
            elif temp_source[-1][0] == "{":
                BOT.Options.zip_pswd = temp_source[-1][1:-1]
                temp_source.pop()
            elif temp_source[-1][0] == "(":
                BOT.Options.unzip_pswd = temp_source[-1][1:-1]
                temp_source.pop()
            else:
                break

        BOT.SOURCE = temp_source
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Regular", callback_data="normal")],
                [
                    InlineKeyboardButton("Compress", callback_data="zip"),
                    InlineKeyboardButton("Extract", callback_data="unzip"),
                ],
                [InlineKeyboardButton("UnDoubleZip", callback_data="undzip")],
            ]
        )
        await message.reply_text(
            text=f"<b>🐹 Select Type of {BOT.Mode.mode.capitalize()} You Want » </b>\n\nRegular:<i> Normal file upload</i>\nCompress:<i> Zip file upload</i>\nExtract:<i> extract before upload</i>\nUnDoubleZip:<i> Unzip then compress</i>",
            reply_markup=keyboard,
            quote=True,
        )
    elif BOT.State.started:
        await message.delete()
        await message.reply_text(
            "<i>I am Already Working ! Please Wait Until I finish 😣!!</i>"
        )


@colab_bot.on_callback_query()
async def handle_options(client, callback_query):
    global BOT, MSG

    if callback_query.data in ["normal", "zip", "unzip", "undzip"]:
        BOT.Mode.type = callback_query.data
        await callback_query.message.delete()
        await colab_bot.delete_messages(
            chat_id=callback_query.message.chat.id,
            message_ids=callback_query.message.reply_to_message_id,
        )
        MSG.status_msg = await colab_bot.send_message(
            chat_id=OWNER,
            text="#STARTING_TASK\n\n**Starting your task in a few Seconds...🦐**",
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("Cancel ❌", callback_data="cancel")],
                ]
            ),
        )
        BOT.State.task_going = True
        BOT.State.started = False
        BotTimes.start_time = datetime.now()
        event_loop = get_event_loop()
        BOT.TASK = event_loop.create_task(taskScheduler())  # type: ignore
        await BOT.TASK
        BOT.State.task_going = False

    elif callback_query.data == "video":
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Split Videos", callback_data="split-true"),
                    InlineKeyboardButton("Zip Videos", callback_data="split-false"),
                ],
                [
                    InlineKeyboardButton("Convert", callback_data="convert-true"),
                    InlineKeyboardButton(
                        "Don't Convert", callback_data="convert-false"
                    ),
                ],
                [
                    InlineKeyboardButton("To » Mp4", callback_data="mp4"),
                    InlineKeyboardButton("To » Mkv", callback_data="mkv"),
                ],
                [
                    InlineKeyboardButton("High Quality", callback_data="q-High"),
                    InlineKeyboardButton("Low Quality", callback_data="q-Low"),
                ],
                [InlineKeyboardButton("Back ⏎", callback_data="back")],
            ]
        )
        await callback_query.message.edit_text(
            f"CHOOSE YOUR DESIRED OPTION ⚙️ »\n\n╭⌬ CONVERT » <code>{BOT.Setting.convert_video}</code>\n├⌬ SPLIT » <code>{BOT.Setting.split_video}</code>\n├⌬ OUTPUT FORMAT » <code>{BOT.Options.video_out}</code>\n╰⌬ OUTPUT QUALITY » <code>{BOT.Setting.convert_quality}</code>",
            reply_markup=keyboard,
        )
    elif callback_query.data == "caption":
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Monospace", callback_data="code-Monospace"),
                    InlineKeyboardButton("Bold", callback_data="b-Bold"),
                ],
                [
                    InlineKeyboardButton("Italic", callback_data="i-Italic"),
                    InlineKeyboardButton("Underlined", callback_data="u-Underlined"),
                ],
                [InlineKeyboardButton("Regular", callback_data="p-Regular")],
            ]
        )
        await callback_query.message.edit_text(
            "CHOOSE YOUR CAPTION FONT STYLE »\n\n⌬ <code>Monospace</code>\n⌬ Regular\n⌬ <b>Bold</b>\n⌬ <i>Italic</i>\n⌬ <u>Underlined</u>",
            reply_markup=keyboard,
        )
    elif callback_query.data == "thumb":
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Delete Thumbnail", callback_data="del-thumb"),
                ],
                [
                    InlineKeyboardButton("Go Back ⏎", callback_data="back"),
                ],
            ]
        )
        thmb_ = "None" if not BOT.Setting.thumbnail else "Exists"
        await callback_query.message.edit_text(
            f"CHOOSE YOUR THUMBNAIL SETTINGS »\n\n⌬ Thumbnail » {thmb_}\n⌬ Send an Image to set as Your Thumbnail",
            reply_markup=keyboard,
        )
    elif callback_query.data == "del-thumb":
        if BOT.Setting.thumbnail:
            os.remove(Paths.THMB_PATH)
        BOT.Setting.thumbnail = False
        await send_settings(
            client, callback_query.message, callback_query.message.id, False
        )
    elif callback_query.data == "set-prefix":
        await callback_query.message.edit_text(
            "Send a Text to Set as PREFIX by REPLYING THIS MESSAGE »"
        )
        BOT.State.prefix = True
    elif callback_query.data == "set-suffix":
        await callback_query.message.edit_text(
            "Send a Text to Set as SUFFIX by REPLYING THIS MESSAGE »"
        )
        BOT.State.suffix = True
    elif callback_query.data in [
        "code-Monospace",
        "p-Regular",
        "b-Bold",
        "i-Italic",
        "u-Underlined",
    ]:
        res = callback_query.data.split("-")
        BOT.Options.caption = res[0]
        BOT.Setting.caption = res[1]
        await send_settings(
            client, callback_query.message, callback_query.message.id, False
        )
    elif callback_query.data in ["split-true", "split-false"]:
        BOT.Options.is_split = True if callback_query.data == "split-true" else False
        BOT.Setting.split_video = (
            "Split Videos" if callback_query.data == "split-true" else "Zip Videos"
        )
        await send_settings(
            client, callback_query.message, callback_query.message.id, False
        )
    elif callback_query.data in [
        "convert-true",
        "convert-false",
        "mp4",
        "mkv",
        "q-High",
        "q-Low",
    ]:
        if callback_query.data in ["convert-true", "convert-false"]:
            BOT.Options.convert_video = (
                True if callback_query.data == "convert-true" else False
            )
            BOT.Setting.convert_video = (
                "Yes" if callback_query.data == "convert-true" else "No"
            )
        elif callback_query.data in ["q-High", "q-Low"]:
            BOT.Setting.convert_quality = callback_query.data.split("-")[-1]
            BOT.Options.convert_quality = (
                True if BOT.Setting.convert_quality == "High" else False
            )
            await send_settings(
                client, callback_query.message, callback_query.message.id, False
            )
        else:
            BOT.Options.video_out = callback_query.data
        await send_settings(
            client, callback_query.message, callback_query.message.id, False
        )
    elif callback_query.data in ["media", "document"]:
        BOT.Options.stream_upload = True if callback_query.data == "media" else False
        BOT.Setting.stream_upload = (
            "Media" if callback_query.data == "media" else "Document"
        )
        await send_settings(
            client, callback_query.message, callback_query.message.id, False
        )

    elif callback_query.data == "close":
        await callback_query.message.delete()
    elif callback_query.data == "back":
        await send_settings(
            client, callback_query.message, callback_query.message.id, False
        )

    # @main Triggering Actual Leech Functions
    elif callback_query.data in ["ytdl-true", "ytdl-false"]:
        BOT.Mode.ytdl = True if callback_query.data == "ytdl-true" else False
        await callback_query.message.delete()
        await colab_bot.delete_messages(
            chat_id=callback_query.message.chat.id,
            message_ids=callback_query.message.reply_to_message_id,
        )
        MSG.status_msg = await colab_bot.send_message(
            chat_id=OWNER,
            text="#STARTING_TASK\n\n**Starting your task in a few Seconds...🦐**",
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("Cancel ❌", callback_data="cancel")],
                ]
            ),
        )
        BOT.State.task_going = True
        BOT.State.started = False
        BotTimes.start_time = datetime.now()
        event_loop = get_event_loop()
        BOT.TASK = event_loop.create_task(taskScheduler())  # type: ignore
        try:
            await BOT.TASK
        finally:
            BOT.State.task_going = False

    # If user Wants to Stop The Task
    elif callback_query.data == "cancel":
        await cancelTask("User Cancelled !")


@colab_bot.on_message(filters.photo & filters.private)
async def handle_image(client, message):
    msg = await message.reply_text("<i>Trying To Save Thumbnail...</i>")
    success = await setThumbnail(message)
    if success:
        await msg.edit_text("**Thumbnail Successfully Changed ✅**")
        await message.delete()
    else:
        await msg.edit_text(
            "🥲 **Couldn't Set Thumbnail, Please Try Again !**", quote=True
        )
    await sleep(15)
    await message_deleter(message, msg)


@colab_bot.on_message(filters.command("setname") & filters.private)
async def custom_name(client, message):
    global BOT
    if len(message.command) != 2:
        msg = await message.reply_text(
            "Send\n/setname <code>custom_fileame.extension</code>\nTo Set Custom File Name 📛",
            quote=True,
        )
    else:
        BOT.Options.custom_name = message.command[1]
        msg = await message.reply_text(
            "Custom Name Has Been Successfully Set !", quote=True
        )

    await sleep(15)
    await message_deleter(message, msg)


@colab_bot.on_message(filters.command("zipaswd") & filters.private)
async def zip_pswd(client, message):
    global BOT
    if len(message.command) != 2:
        msg = await message.reply_text(
            "Send\n/zipaswd <code>password</code>\nTo Set Password for Output Zip File. 🔐",
            quote=True,
        )
    else:
        BOT.Options.zip_pswd = message.command[1]
        msg = await message.reply_text(
            "Zip Password Has Been Successfully Set !", quote=True
        )

    await sleep(15)
    await message_deleter(message, msg)


@colab_bot.on_message(filters.command("unzipaswd") & filters.private)
async def unzip_pswd(client, message):
    global BOT
    if len(message.command) != 2:
        msg = await message.reply_text(
            "Send\n/unzipaswd <code>password</code>\nTo Set Password for Extracting Archives. 🔓",
            quote=True,
        )
    else:
        BOT.Options.unzip_pswd = message.command[1]
        msg = await message.reply_text(
            "Unzip Password Has Been Successfully Set !", quote=True
        )

    await sleep(15)
    await message_deleter(message, msg)


@colab_bot.on_message(filters.command("help") & filters.private)
async def help_command(client, message):
    msg = await message.reply_text(
        "**🚀 COLAB LEECHER - COMPLETE GUIDE**\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "**📥 UPLOAD COMMANDS:**\n\n"
        "🔹 /tupload - Download & Upload to Telegram\n"
        "🔹 /gdupload - Download & Mirror to Google Drive\n"
        "🔹 /drupload - Upload Folder from Colab to Telegram\n"
        "🔹 /ytupload - Download from YouTube/YTDL & Upload\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "**⚙️ SETTINGS & CONFIGURATION:**\n\n"
        "🔹 /settings - Open bot settings panel\n"
        "🔹 /setname <filename.ext> - Set custom output filename\n"
        "🔹 /zipaswd <password> - Set password for zip 🔐\n"
        "🔹 /unzipaswd <password> - Set password for extraction 🔓\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "**📋 SUPPORTED SOURCES:**\n\n"
        "✅ HTTP/HTTPS Links (Aria2c)\n"
        "✅ YouTube & YTDL Playlists\n"
        "✅ Torrents & Magnet Links\n"
        "✅ Google Drive Links\n"
        "✅ Mega.nz Cloud Storage\n"
        "✅ Terabox Cloud Storage\n"
        "✅ Telegram Files\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "**🎯 ADVANCED FEATURES:**\n\n"
        "✨ Video Conversion (MP4/MKV)\n"
        "✨ Auto File Splitting (2GB chunks)\n"
        "✨ Archive Compression (ZIP/RAR/7Z)\n"
        "✨ Password Protected Archives\n"
        "✨ Custom Thumbnails for uploads\n"
        "✨ Real-time Progress Updates\n"
        "✨ Task Cancellation\n"
        "✨ Colab Resource Monitoring\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "**💡 USAGE PATTERN:**\n\n"
        "<code>https://link1.mp4\n"
        "https://link2.zip\n"
        "[custom_name.mp4]        ← Optional\n"
        "{zippassword}            ← Optional\n"
        "(unzippassword)          ← Optional</code>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "**📸 THUMBNAIL FEATURE:**\n\n"
        "Simply send an image to set it as your default thumbnail for all uploads!\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "**👨‍💻 CREATORS & CONTRIBUTORS:**\n\n"
        "🦄 **Original Creator:** XronTrix10\n"
        "   Repository: github.com/XronTrix10/Telegram-Leecher\n\n"
        "🔄 **Current Maintainer:** Pasindu Dilsan\n"
        "   Repository: github.com/pasindu2580/tgdl\n\n"
        "🙏 **Special Thanks to:**\n"
        "   • kjeymax - Bug fixes & improvements\n"
        "   • ehraz786 - Bug fixes & improvements\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "**📞 SUPPORT & COMMUNITY:**\n\n"
        "Channel: @Colab_Leecher\n"
        "Discussion: @Colab_Leecher_Discuss\n\n"
        "⚠️ **IMPORTANT:** Only download content you have rights to. "
        "Google Colab has strict policies on copyrighted material.",
        quote=True,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "📖 Wiki Instructions",
                        url="https://github.com/XronTrix10/Telegram-Leecher/wiki/INSTRUCTIONS",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "🌐 GitHub Repository",
                        url="https://github.com/pasindu2580/tgdl",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "📣 Channel",
                        url="https://t.me/Colab_Leecher",
                    ),
                    InlineKeyboardButton(
                        "💬 Discussion",
                        url="https://t.me/Colab_Leecher_Discuss",
                    ),
                ],
            ]
        ),
    )
    await sleep(240)
    await message_deleter(message, msg)


logging.info("Colab Leecher Started !")
colab_bot.run()
