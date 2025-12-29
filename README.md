# tgdl-main — Colab Leecher 🚀

<div align="center">
  <img src="https://user-images.githubusercontent.com/125879861/255391401-371f3a64-732d-4954-ac0f-4f093a6605e1.png" alt="Colab Leecher" width="200px"/>
  
  <p><strong>A Pyrogram-based Telegram Bot to Transfer Files / Folders to Telegram and Google Drive using Google Colab with Multi-Functionality</strong></p>
</div>

A powerful Telegram bot that runs on Google Colab to download files from various sources and upload them to Telegram or Google Drive with advanced features like video conversion, file compression, extraction, and progress tracking.

## 🎯 Overview

**Colab Leecher** uses Google Colab's resources to:
- Download from HTTP/S, Torrents, Magnets, YouTube, Google Drive, Mega, Terabox, and Telegram
- Upload files to Telegram (with automatic splitting for large files)
- Mirror downloads to Google Drive
- Convert videos (MP4/MKV) using FFmpeg
- Compress/extract archives with password protection
- Split large files automatically
- Track progress in real-time with speed, ETA, and bandwidth usage

## ⚙️ Features

### Core Download Support
- **HTTP/S Links** — Direct downloads via Aria2c
- **YouTube/YTDL** — Videos and playlists (with subtitles & thumbnails)
- **Torrents & Magnets** — Fast downloads via Libtorrent with tracker optimization
- **Google Drive** — Direct GDrive link downloads
- **Mega.nz** — Cloud storage downloads
- **Terabox** — Cloud storage support
- **Telegram** — Direct Telegram file downloads

### Upload & Storage
- **Telegram Upload** — Stream upload with automatic file splitting (2GB chunks)
- **Google Drive Mirror** — Copy downloads directly to Drive
- **Directory Leech** — Upload entire folders from Colab

### File Processing
- **Video Conversion** — Convert to MP4/MKV with quality selection (High/Low)
- **Video Splitting** — Automatically split large videos (>2GB) into chunks
- **Compression** — ZIP/RAR/7z with password protection (split archives)
- **Extraction** — Extract RAR/7Z/ZIP/TAR/GZ with password support
- **Dual Compression** — Unzip then rezip in one operation

### Advanced Features
- **Custom File Naming** — Rename downloads with prefix/suffix
- **Thumbnail Management** — Custom thumbnails for uploaded files
- **Progress Updates** — Real-time status with speed, ETA, CPU/RAM/Disk usage
- **Settings Panel** — Inline keyboard UI for configuration
- **Task Cancellation** — Stop ongoing downloads anytime
- **Colab Resource Monitoring** — Display system usage during operations

## 📋 Prerequisites

### System Requirements
- Google Colab account (free or pro)
- Python 3.7+
- FFmpeg (installed via apt in Colab)
- Aria2c (for HTTP downloads)
- Libtorrent (for torrent/magnet support)

### Credentials
- **Telegram Bot Token** — Create via [@BotFather](https://t.me/botfather)
- **API_ID & API_HASH** — Get from [my.telegram.org](https://my.telegram.org)
- **User ID** — Your Telegram user ID (find via [@userinfobot](https://t.me/userinfobot))
- **Dump Chat ID** — Channel/group ID for logs (format: -100xxxxxxxxx)
- **(Optional) Google Drive** — For mirror uploads (service account JSON)

## 🚀 Installation & Setup

### In Google Colab

1. **Open the Notebook Cell** (copy `main.py` into a Colab cell)
2. **Fill Credentials:**
   ```python
   API_ID = 12345678              # Your API_ID from my.telegram.org
   API_HASH = "abcdef123456..."   # Your API_HASH
   BOT_TOKEN = "123456:ABC..."    # Bot token from @BotFather
   USER_ID = 987654321            # Your Telegram user ID
   DUMP_ID = 1001234567890        # Dump channel ID (or just the numbers)
   ```

3. **Run the Cell** — Bot will:
   - Clone the tgdl repository
   - Install dependencies (ffmpeg, aria2, megatools, unrar, p7zip)
   - Install Python packages (pyrogram, yt-dlp, libtorrent, etc.)
   - Start listening for commands

## 📱 Commands

### Upload Modes

| Command | Description |
|---------|-------------|
| `/tupload` | Download and upload files **to Telegram** |
| `/gdupload` | Download and upload files **to Google Drive** (mirror) |
| `/drupload` | Upload **directory from Colab** to Telegram |
| `/ytupload` | Download from **YouTube/YTDL** and upload to Telegram |

### Settings & Configuration

| Command | Usage |
|---------|-------|
| `/settings` | Open bot settings panel ⚙️ |
| `/setname <filename.ext>` | Set custom output filename |
| `/zipaswd <password>` | Set password for zip compression 🔐 |
| `/unzipaswd <password>` | Set password for extraction 🔓 |
| `/help` | Show all commands and examples |
| `/start` | Bot introduction and links |

### Configuration Options

**Upload Type:**
- `Media` — Upload as media (optimized for playback)
- `Document` — Upload as document file

**Video Settings:**
- `Split Videos` — Split large videos into chunks
- `Zip Videos` — Compress instead of split
- `Convert` — Enable/disable video conversion
- `Quality` — High (slow, best) or Low (fast, compressed)
- `Format` — MP4 or MKV output

**Caption Style:**
- Monospace, Bold, Italic, Underlined, or Regular text

**Other:**
- Set custom prefix/suffix for filenames
- Upload custom thumbnail for videos

## 📥 Usage Examples

### Download & Upload to Telegram
```
/tupload
[Send multiple links, one per line]
https://example.com/file1.mp4
https://example.com/file2.zip
[custom_name.mp4]        ← Optional: set filename
{zippassword}            ← Optional: password for compression
(unzippassword)          ← Optional: password to extract
```

Then select: **Regular** (normal upload) or **Compress** (zip first) or **Extract** (unzip then upload) or **UnDoubleZip** (unzip + rezip)

### Download from YouTube
```
/ytupload
https://www.youtube.com/watch?v=xxxxxxx
```

### Upload Directory from Colab
```
/drupload
/home/user/Downloads/myfolder
```

### Mirror to Google Drive
```
/gdupload
https://example.com/largefile.zip
```
(Files appear in: Drive → Downloads → tgdl folder)

## ⚙️ Bot Settings (via /settings)

```
╭⌬ UPLOAD » Media/Document
├⌬ SPLIT » Split Videos / Zip Videos
├⌬ CONVERT » Yes / No
├⌬ CAPTION » Monospace / Bold / Italic / Underlined / Regular
├⌬ PREFIX » None / Exists
├⌬ SUFFIX » None / Exists
╰⌬ THUMBNAIL » None / Exists
```

## 📊 Real-Time Status Display

During downloads, bot shows:
```
📥 DOWNLOADING »
Link 01
Speed: 5.2 MB/s
Engine: Aria2c 🧨 (or YtDL 🏮 or Libtorrent 🚀)
ETA: 2m 30s
Time Spent: 5m 12s
Processed: 250 MB
Total Size: 1.5 GB

⌬─────「 Colab Usage 」─────⌬
CPU Usage » 45%
RAM Usage » 2.3 GB
DISK Free » 50 GB
```

## 🔧 Supported Sources

| Source | Download | Support |
|--------|----------|---------|
| **HTTP/HTTPS** | Aria2c | Direct links, streaming |
| **YouTube** | yt-dlp | Videos, playlists, subtitles |
| **Torrents/Magnets** | Libtorrent | Fast torrent downloads |
| **Google Drive** | Direct API | Public/shared files |
| **Mega.nz** | Direct | Cloud downloads |
| **Terabox** | Direct | Cloud downloads |
| **Telegram** | Direct API | Channel/chat files |

## 🛡️ Security & Limits

- **Bot Owner Only** — Only your User ID can control the bot
- **File Size Limit** — 2GB per upload to Telegram (auto-split)
- **Archive Passwords** — Protect compressed files
- **Colab Quotas** — Free tier has time/resource limits; use responsibly
- **No Credentials in Code** — All sensitive data in `credentials.json` (auto-created)

### ⚠️ Important Notes
- Google Colab has strict policies — avoid downloading copyrighted content
- Torrents work but are resource-intensive; may trigger Colab warnings
- Free Colab sessions reset every 12 hours; use Colab Pro for longer sessions
- Each file upload requires Colab session to stay active

## 📝 Configuration Files

### credentials.json (Auto-Created)
```json
{
  "API_ID": 12345678,
  "API_HASH": "abcdef...",
  "BOT_TOKEN": "123456:ABC...",
  "USER_ID": 987654321,
  "DUMP_ID": -1001234567890
}
```

### my_bot.session
- Pyrogram bot session file (auto-created, deleted before each run)

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| **Bot won't start** | Check credentials in cell; verify API_ID/HASH |
| **Downloads failing** | Check link validity; inspect Colab logs for rate-limits |
| **Video conversion slow** | Normal on free Colab; use Low quality or skip conversion |
| **Telegram upload fails** | Ensure DUMP_ID is correct; bot needs write permission |
| **Torrent won't work** | Install libtorrent: `pip install libtorrent` |
| **FFmpeg errors** | Colab installs it automatically; check cell output logs |
| **Out of space** | Colab free tier has ~80GB; delete old downloads or upgrade |

## 💡 Tips & Tricks

1. **Batch Downloads** — Send multiple links at once; bot queues them sequentially
2. **Custom Thumbnails** — Send an image in Telegram; bot uses it for all uploads
3. **Password Protection** — Use `/zipaswd` before upload to encrypt files
4. **Video Quality** — Set to Low for faster processing on free Colab
5. **Prefix/Suffix** — Automatically rename files (e.g., prefix: "MyChannel_", suffix: "_HD")
6. **Keep-Alive** — Bot auto-plays silent audio to prevent Colab session timeout

## 🔗 Links & Support

- **GitHub Repository** — [pasindu2580/tgdl](https://github.com/pasindu2580/tgdl)
- **Instructions Wiki** — [Telegram-Leecher Wiki](https://github.com/XronTrix10/Telegram-Leecher/wiki/INSTRUCTIONS)
- **Support Channel** — [@Colab_Leecher](https://t.me/Colab_Leecher)
- **Discussion Group** — [@Colab_Leecher_Discuss](https://t.me/Colab_Leecher_Discuss)

## 📜 License

MIT — See LICENSE file in repository

## 👨‍💻 Credits & Attribution

<h3 align="center">‎𐂐 Forked from <a href="https://github.com/XronTrix10/Telegram-Leecher">XronTrix10</a></h3>

### Special Thanks 🙏

- **XronTrix10** — Original creator and main developer
- **kjeymax** — Bug fixes and minor improvements
- **ehraz786** — Bug fixes and minor improvements

## Recent Fixes
- **YTDL Video Naming:** Videos downloaded using `ytdl` are now saved with their proper titles instead of their video IDs.
- **Thumbnail Format:** Thumbnails are now saved in `.jpg` format to avoid issues with some Telegram clients that don't handle `.webp` thumbnails correctly.
- **Magnet Link Cleanup**: Fixed an issue where partially downloaded files from a canceled magnet link were not properly cleaned up and were being included in subsequent tasks.
- **Improved Video Splitting**: Enhanced video splitting to correctly handle x265 encoded MP4s and MKVs, as well as x264 encoded MKVs, ensuring that video, audio, and subtitle tracks are all correctly processed.
- **Added WMV Conversion**: Added support for converting `.wmv` files. These files are now correctly identified as videos and sent for conversion.

---

**Happy Leeching! 🦐**
