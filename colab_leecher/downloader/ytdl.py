import logging
import yt_dlp
from asyncio import sleep
from threading import Thread
from os import makedirs, path as ospath
from colab_leecher.utility.handler import cancelTask
from colab_leecher.utility.variables import YTDL, MSG, Messages, Paths, BOT
from colab_leecher.utility.helper import getTime, keyboard, sizeUnit, status_bar, sysINFO


async def YTDL_Status(link, num):
    global Messages, YTDL
    name = await get_YT_Name(link)
    Messages.status_head = f"<b>📥 DOWNLOADING FROM » </b><i>🔗Link {str(num).zfill(2)}</i>\n\n<code>{name}</code>\n"

    # pass BOT.Options.ytdl_format (may be empty)
    sel = BOT.Options.ytdl_format if hasattr(BOT.Options, "ytdl_format") else None
    YTDL_Thread = Thread(target=YouTubeDL, name="YouTubeDL", args=(link, sel))
    YTDL_Thread.start()

    while YTDL_Thread.is_alive():  # Until ytdl is downloading
        if YTDL.header:
            sys_text = sysINFO()
            message = YTDL.header
            try:
                await MSG.status_msg.edit_text(text=Messages.task_msg + Messages.status_head + message + sys_text, reply_markup=keyboard())
            except Exception:
                pass
        else:
            try:
                await status_bar(
                    down_msg=Messages.status_head,
                    speed=YTDL.speed,
                    percentage=float(YTDL.percentage),
                    eta=YTDL.eta,
                    done=YTDL.done,
                    left=YTDL.left,
                    engine="Xr-YtDL 🏮",
                )
            except Exception:
                pass

        await sleep(2.5)


class MyLogger:
    def __init__(self):
        pass

    def debug(self, msg):
        global YTDL
        if "item" in str(msg):
            msgs = msg.split(" ")
            YTDL.header = f"\n⏳ __Getting Video Information {msgs[-3]} of {msgs[-1]}__"

    @staticmethod
    def warning(msg):
        pass

    @staticmethod
    def error(msg):
        # if msg != "ERROR: Cancelling...":
        # print(msg)
        pass


# New helper: list available formats (heights + best audio)
def list_formats(link):
    try:
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            info = ydl.extract_info(link, download=False)
            title = info.get("title", "UNKNOWN")
            formats = info.get("formats", []) or []
            # find best audio candidate
            best_audio = None
            for f in sorted(formats, key=lambda x: (x.get("abr") or 0), reverse=True):
                if f.get("vcodec") == "none" and f.get("acodec") != "none":
                    best_audio = f
                    break
            heights = {}
            for f in formats:
                h = f.get("height")
                if h and f.get("vcodec") != "none":
                    size = f.get("filesize") or f.get("filesize_approx") or 0
                    existing = heights.get(h)
                    if not existing or (f.get("tbr") or 0) > (existing.get("tbr") or 0):
                        heights[h] = {
                            "format_id": f.get("format_id"),
                            "ext": f.get("ext"),
                            "v_size": size,
                            "tbr": f.get("tbr"),
                        }
            audio_info = None
            if best_audio:
                audio_info = {
                    "format_id": best_audio.get("format_id"),
                    "ext": best_audio.get("ext"),
                    "size": best_audio.get("filesize") or best_audio.get("filesize_approx") or 0,
                    "abr": best_audio.get("abr"),
                }
            return {"heights": heights, "audio": audio_info, "title": title}
    except Exception as e:
        logging.error(f"list_formats error: {e}")
        return {"heights": {}, "audio": None, "title": "UNKNOWN"}


# Modified YouTubeDL to accept optional format_selector
def YouTubeDL(url, format_selector=None):
    global YTDL

    def my_hook(d):
        global YTDL
        if d["status"] == "downloading":
            total_bytes = d.get("total_bytes", 0)
            dl_bytes = d.get("downloaded_bytes", 0)
            percent = d.get("downloaded_percent", 0)
            speed = d.get("speed", "N/A")
            eta = d.get("eta", 0)

            if total_bytes:
                percent = round((float(dl_bytes) * 100 / float(total_bytes)), 2)

            YTDL.header = ""
            YTDL.speed = sizeUnit(speed) if speed else "N/A"
            YTDL.percentage = percent
            YTDL.eta = getTime(eta) if eta else "N/A"
            YTDL.done = sizeUnit(dl_bytes) if dl_bytes else "N/A"
            YTDL.left = sizeUnit(total_bytes) if total_bytes else "N/A"

        elif d["status"] == "downloading fragment":
            pass
        else:
            logging.info(d)

    # Use provided selector when present, otherwise default
    ydl_opts = {
        "format": format_selector if format_selector else "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "writethumbnail": True,
        "concurrent_fragment_downloads": 4,
        "overwrites": True,
        "progress_hooks": [my_hook],
        "writesubtitles": "true",
        "subtitleslangs": ["all"],
        "extractor_args": {"subtitlesformat": "srt"},
        "logger": MyLogger(),
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        if not ospath.exists(Paths.thumbnail_ytdl):
            makedirs(Paths.thumbnail_ytdl)
        try:
            info_dict = ydl.extract_info(url, download=False)
            YTDL.header = "⌛ __Please WAIT a bit...__"
            if "_type" in info_dict and info_dict["_type"] == "playlist":
                playlist_name = info_dict["title"]
                if not ospath.exists(ospath.join(Paths.down_path, playlist_name)):
                    makedirs(ospath.join(Paths.down_path, playlist_name))
                ydl_opts["outtmpl"] = {
                    "default": f"{Paths.down_path}/{playlist_name}/%(title)s.%(ext)s",
                    "thumbnail": f"{Paths.thumbnail_ytdl}/%(id)s.%(ext)s",
                }
                for entry in info_dict["entries"]:
                    video_url = entry["webpage_url"]
                    try:
                        ydl.download([video_url])
                    except yt_dlp.utils.DownloadError as e:
                        if getattr(e, "exc_info", [None])[0] == 36:
                            ydl_opts["outtmpl"] = {
                                "default": f"{Paths.down_path}/%(id)s.%(ext)s",
                                "thumbnail": f"{Paths.thumbnail_ytdl}/%(id)s.%(ext)s",
                            }
                            ydl.download([video_url])
            else:
                YTDL.header = ""
                ydl_opts["outtmpl"] = {
                    "default": f"{Paths.down_path}/%(id)s.%(ext)s",
                    "thumbnail": f"{Paths.thumbnail_ytdl}/%(id)s.%(ext)s",
                }
                try:
                    # ensure chosen format is used
                    ydl.params["format"] = ydl_opts["format"]
                    ydl.download([url])
                except yt_dlp.utils.DownloadError as e:
                    if getattr(e, "exc_info", [None])[0] == 36:
                        ydl_opts["outtmpl"] = {
                            "default": f"{Paths.down_path}/%(id)s.%(ext)s",
                            "thumbnail": f"{Paths.thumbnail_ytdl}/%(id)s.%(ext)s",
                        }
                        ydl.download([url])
        except Exception as e:
            logging.error(f"YTDL ERROR: {e}")


async def get_YT_Name(link):
    with yt_dlp.YoutubeDL({"logger": MyLogger()}) as ydl:
        try:
            info = ydl.extract_info(link, download=False)
            if "title" in info and info["title"]: 
                return info["title"]
            else:
                return "UNKNOWN DOWNLOAD NAME"
        except Exception as e:
            await cancelTask(f"Can't Download from this link. Because: {str(e)}")
            return "UNKNOWN DOWNLOAD NAME"

