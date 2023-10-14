import logging
from pathlib import Path

from rich.logging import RichHandler

try:
    from dotenv import find_dotenv, load_dotenv

    load_dotenv(find_dotenv())
except ModuleNotFoundError:
    pass

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
rich_handler = RichHandler(rich_tracebacks=True)
logging.getLogger().handlers = [rich_handler]


def get_filepath(filename: str, folder_name: str = "examples") -> str:
    """Function created to take the full path of the base files to
    execute in the scripts.
    Args:
        filename (str): The file name
        folder_name (str, optional): Folder where files are stored..
        Defaults to "examples".
    Returns:
        str: Returns the name of the file, assuming that it has been
        placed in the root folder or in the folder where it should be placed.
    """
    result = filename
    source = Path(folder_name).resolve()
    list_files = [file for file in source.iterdir()]
    for file in list_files:
        if file.name.strip() == filename.strip():
            result = file.as_posix()
    return result
