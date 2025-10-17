import subprocess
import logging
from datetime import datetime
from colab_leecher.utility.helper import status_bar
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
        downloaded_size = "N/A"
        total_size = "N/A"
        speed = "N/A"

        if len(subparts) > 10:
            file_name = parts[0]
            Messages.download_name = file_name
            progress = subparts[0][:-1]
            if progress != "N/A":
                progress = round(float(progress))
            downloaded_size = f"{subparts[2]} {subparts[3]}"
            total_size = f"{subparts[7]} {subparts[8]}"
            speed = f"{subparts[9][1:]} {subparts[10][:-1]}"

        Messages.status_head = f"<b>📥 DOWNLOADING FROM MEGA » </b>\n\n<b>🏷️ Name » </b><code>{file_name}</code>\n"
        
        await status_bar(
            Messages.status_head,
            speed,
            progress,
            "🤷‍♂️ !!", # Calculate ETA
            downloaded_size,
            total_size,
            "Meg 😡",
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
