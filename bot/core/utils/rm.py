import shutil
import aiofiles.os
from configs import Config

async def rm_dir(root: str = f"{Config.DOWNLOAD_DIR}"):
    """
    Delete a Folder.

    :param root: Pass DIR Path
    """

    try:
        shutil.rmtree(root)
    except Exception as e:
        Config.LOGGER.getLogger(__name__).error(e)
