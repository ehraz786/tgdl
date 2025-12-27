import subprocess
import logging
from datetime import datetime
from colab_leecher.utility.helper import getTime, status_bar
from colab_leecher.utility.variables import BotTimes, Messages, Paths

async def megadl(link: str, num: int):
    """
    Downloads a file from Mega.nz asynchronously.

    Args:
        link (str): The Mega.nz link to the file.
        num (int): Identification number for the download.

    Returns:
        None
    """
    global BotTimes, Messages
    BotTimes.task_start = datetime.now()

    try:
        # Validate the Mega.nz link
        validate_mega_link(link)

        # Construct command to run megadl
        command = [
            "megadl",
            "--no-ask-password",
            "--path",
            Paths.down_path,
            link,
        ]

        # Run megadl asynchronously
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0)

        while True:
            output = process.stdout.readline()
            if output == b'' and process.poll() is not None:
                break

            # Extract information from output
            await extract_info(output.strip().decode("utf-8"))

    except Exception as e:
        logging.error(f"Error downloading from Mega.nz: {e}")

def get_bytes_from_string(size_str: str) -> int:
    """Converts a size string (e.g., '1.23 GiB') to bytes."""
    size_str = size_str.strip()
    try:
        size, unit = size_str.split()
        size = float(size)
        unit = unit.replace("/s", "")
        if unit == "B":
            return int(size)
        elif unit == "KiB":
            return int(size * 1024)
        elif unit == "MiB":
            return int(size * 1024**2)
        elif unit == "GiB":
            return int(size * 1024**3)
        elif unit == "TiB":
            return int(size * 1024**4)
    except (ValueError, IndexError):
        pass
    return 0

async def extract_info(line: str):
    """
    Extracts information about the download progress from a line of output.

    Args:
        line (str): A line of output from the megadl command.

    Returns:
        None
    """
    try:
        parts = line.split(": ")
        subparts = parts[1].split() if len(parts) > 1 else []

        file_name = "N/A"
        progress = "N/A"
        downloaded_size_str = "N/A"
        total_size_str = "N/A"
        speed_str = "N/A"
        eta = "N/A"

        if len(subparts) > 10:
            file_name = parts[0]
            Messages.download_name = file_name
            progress = subparts[0][:-1]
            if progress != "N/A":
                progress = round(float(progress))
            downloaded_size_str = f"{subparts[2]} {subparts[3]}"
            total_size_str = f"{subparts[7]} {subparts[8]}"
            speed_str = f"{subparts[9][1:]} {subparts[10][:-1]}"

            downloaded_size = get_bytes_from_string(downloaded_size_str)
            total_size = get_bytes_from_string(total_size_str)
            speed = get_bytes_from_string(speed_str)

            if speed > 0:
                time_left = (total_size - downloaded_size) / speed
                eta = getTime(time_left)

        Messages.status_head = f"<b>📥 DOWNLOADING FROM MEGA » </b>\n\n<b>🏷️ Name » </b><code>{file_name}</code>\n"
        
        await status_bar(
            Messages.status_head,
            speed_str,
            progress,
            eta,
            downloaded_size_str,
            total_size_str,
            "Mega 🥰",
        )

    except Exception as e:
        logging.error(f"Error extracting download info: {e}")

def validate_mega_link(link: str):
    """
    Validates a Mega.nz link to ensure it's in the correct format.

    Args:
        link (str): The Mega.nz link to validate.

    Raises:
        ValueError: If the link is invalid.
    """
    # Add your validation logic here
    pass
