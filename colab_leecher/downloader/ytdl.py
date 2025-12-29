import logging
import yt_dlp
from asyncio import sleep, run, get_running_loop, run_coroutine_threadsafe
from threading import Thread
from os import makedirs, path as ospath, remove, listdir
from colab_leecher.utility.handler import cancelTask
from colab_leecher.utility.variables import YTDL, MSG, Messages, Paths, BOT
from colab_leecher.utility.helper import getTime, keyboard, sizeUnit, status_bar, sysINFO
from PIL import Image
import time


async def YTDL_Status(link, num, ytdl_mode):
    global Messages, YTDL
    name = await get_YT_Name(link)
    loop = get_running_loop()
    Messages.status_head = f"<b>📥 DOWNLOADING FROM » </b><i>🔗Link {str(num).zfill(2)}</i>\n\n<code>{name}</code>\n"

    ytdl_thread = Thread(target=YouTubeDL(link, ytdl_mode, loop).download)
    ytdl_thread.start()

    while ytdl_thread.is_alive():  # Until ytdl is downloading
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
    def __init__(self, loop):
        self.loop = loop

    def debug(self, msg):
        global YTDL
        if "item" in str(msg):
            msgs = msg.split(" ")
            YTDL.header = f"\n⏳ __Getting Video Information {msgs[-3]} of {msgs[-1]}__"

    def warning(self, msg):
        pass

    def error(self, msg):
        logging.error(msg)


class YouTubeDL:
    def __init__(self, link, ytdl_mode, loop):
        self.link = link
        self.ytdl_mode = ytdl_mode
        self.loop = loop
        self.logger = MyLogger(self.loop)
        self.info_dict = None
        self.final_filename = None

    def my_hook(self, d):
        global YTDL

        if d["status"] == "finished":
            self.final_filename = d["filename"]
        elif d["status"] == "downloading":
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

    def download(self):
        if self.ytdl_mode == "video":
            self.download_video()
        elif self.ytdl_mode == "audio":
            self.download_audio()
        elif self.ytdl_mode == "thumbnail":
            self.download_thumbnail()

    def download_video(self):
        ydl_opts = {
            "format": "bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/bestvideo+bestaudio",
            "merge_output_format": "mkv",
            "writethumbnail": True,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "embedsubtitles": True,
            "embedthumbnail": True,
            "subtitleslangs": ["all"],
            "ignoreerrors": True,
            "concurrent_fragment_downloads": 4,
            "overwrites": True,
            "progress_hooks": [self.my_hook],
            "logger": self.logger,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        }
        self._download_with_opts(ydl_opts)

    def download_audio(self):
        ydl_opts = {
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
            "writethumbnail": False,
            "progress_hooks": [self.my_hook],
            "logger": self.logger,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        }
        self._download_with_opts(ydl_opts, audio_only=True)

    def download_thumbnail(self):
        ydl_opts = {
            "writethumbnail": True,
            "skip_download": True,
            "logger": self.logger,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        }
        self._download_with_opts(ydl_opts, thumbnail_only=True)
    
    def _download_with_opts(self, ydl_opts, audio_only=False, thumbnail_only=False):
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                if not ospath.exists(Paths.thumbnail_ytdl) and not thumbnail_only:
                    makedirs(Paths.thumbnail_ytdl)
                
                self.info_dict = ydl.extract_info(self.link, download=False)
                YTDL.header = "⌛ __Please WAIT a bit...__"
                if "_type" in self.info_dict and self.info_dict["_type"] == "playlist":
                    playlist_name = self.info_dict["title"]
                    playlist_path = ospath.join(Paths.down_path, playlist_name)
                    if not ospath.exists(playlist_path):
                        makedirs(playlist_path)
                    
                    for entry in self.info_dict["entries"]:
                        if not entry:
                            logging.warning("Skipping an empty entry in the playlist.")
                            continue
                        video_url = entry["webpage_url"]
                        try:
                            if thumbnail_only:
                                ydl_opts["outtmpl"] = f"{playlist_path}/%(title)s.%(ext)s"
                            elif audio_only:
                                ydl_opts["outtmpl"] = f"{playlist_path}/%(title)s.%(ext)s"
                            else:
                                ydl_opts["outtmpl"] = f"{playlist_path}/%(title)s.%(ext)s"
                            
                            with yt_dlp.YoutubeDL(ydl_opts) as ydl_single:
                                ydl_single.download([video_url])

                            if self.final_filename and self.ytdl_mode == "video":
                                base_name, _ = ospath.splitext(self.final_filename)
                                dir_name = ospath.dirname(self.final_filename)
                                for file in listdir(dir_name):
                                    file_path = ospath.join(dir_name, file)
                                    if ospath.isfile(file_path) and file_path.startswith(base_name) and not file_path.endswith('.mkv'):
                                        remove(file_path)

                            if thumbnail_only:
                                info = ydl.extract_info(video_url, download=False)
                                file_path = ydl.prepare_filename(info)
                                base, _ = ospath.splitext(file_path)
                                for ext in ['webp', 'png', 'jpg', 'jpeg']:
                                    thumb_path = f"{base}.{ext}"
                                    if ospath.exists(thumb_path):
                                        img = Image.open(thumb_path).convert("RGB")
                                        img.save(f"{base}.jpg", "jpeg")
                                        if ext != "jpg":
                                            remove(thumb_path)
                                        break
                            
                            time.sleep(2) # sleep between playlist downloads

                        except yt_dlp.utils.DownloadError as e:
                            logging.error(f"Failed to download {video_url}: {e}")
                            continue # Skip to the next video
                else:
                    YTDL.header = ""
                    if thumbnail_only:
                        ydl_opts["outtmpl"] = f"{Paths.down_path}/%(title)s.%(ext)s"
                    elif audio_only:
                        ydl_opts["outtmpl"] = f"{Paths.down_path}/%(title)s.%(ext)s"
                    else:
                        ydl_opts["outtmpl"] = f"{Paths.down_path}/%(title)s.%(ext)s"

                    with yt_dlp.YoutubeDL(ydl_opts) as ydl_single:
                        ydl_single.download([self.link])

                    if self.final_filename and self.ytdl_mode == "video":
                        base_name, _ = ospath.splitext(self.final_filename)
                        dir_name = ospath.dirname(self.final_filename)
                        for file in listdir(dir_name):
                            file_path = ospath.join(dir_name, file)
                            if ospath.isfile(file_path) and file_path.startswith(base_name) and not file_path.endswith('.mkv'):
                                remove(file_path)

                    if thumbnail_only:
                        info = ydl.extract_info(self.link, download=False)
                        file_path = ydl.prepare_filename(info)
                        base, _ = ospath.splitext(file_path)
                        for ext in ['webp', 'png', 'jpg', 'jpeg']:
                            thumb_path = f"{base}.{ext}"
                            if ospath.exists(thumb_path):
                                img = Image.open(thumb_path).convert("RGB")
                                img.save(f"{base}.jpg", "jpeg")
                                if ext != "jpg":
                                    remove(thumb_path)
                                break
        except Exception as e:
            logging.error(f"YTDL ERROR: {e}")
            run_coroutine_threadsafe(cancelTask(f"YTDL ERROR: {e}"), self.loop)


async def get_YT_Name(link):
    loop = get_running_loop()
    with yt_dlp.YoutubeDL({"logger": MyLogger(loop)}) as ydl:
        try:
            info = ydl.extract_info(link, download=False)
            if "title" in info and info["title"]:
                return info["title"]
            else:
                return "UNKNOWN DOWNLOAD NAME"
        except Exception as e:
            await cancelTask(f"Can't Download from this link. Because: {str(e)}")
            return "UNKNOWN DOWNLOAD NAME"
