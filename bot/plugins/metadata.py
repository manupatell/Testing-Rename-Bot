import os
import time
import json
import shlex
import shutil
import aiohttp
from bot.client import (
    Client
)
from configs import Config
from pyrogram import filters, enums
from pyrogram.types import Message
from bot.core.file_info import (
    get_media_file_size,
    get_media_file_name
)
from bot.core.handlers.time_gap import check_time_gap
from bot.core.db.database import db
from bot.core.utils.rm import rm_dir
from bot.core.utils.executor import execute
from bot.core.db.add import add_user_to_database
from bot.core.display import display_progress_for_pyrogram, convert
from bot.core.file_info import get_file_attr
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser

@Client.on_message(filters.command("edit_metadata") & filters.private)
async def video_info_handler(c: Client, m: Message):
    await add_user_to_database(c, m)
    if (not m.reply_to_message) or (len(m.command) == 1):
        await m.reply_text(f"Reply to video with,\n/{m.command[0]} file_name", True)
        return
    file_name = " ".join(m.command[1:])
    title = (await db.get_title(m.from_user.id)) or "StarMovies.hop.sh"
    default_f_name = get_media_file_name(m.reply_to_message)
    new_file_name = default_f_name[:60] + default_f_name[-4:]
    newfile_name = default_f_name[:60] + default_f_name[-4:]
    if not m.reply_to_message.video:
        await m.reply_text("This is not a Video!", True)
        return
    editable = await m.reply_text("Downloading Video ...", quote=True)
    dl_loc = Config.DOWNLOAD_DIR + "/" + str(m.from_user.id) + "/"
    root_dl_loc = dl_loc
    if not os.path.isdir(dl_loc):
        os.makedirs(dl_loc)
    c_time = time.time()
    the_media = await c.download_media(
        message=m.reply_to_message,
        file_name=dl_loc,
        progress=display_progress_for_pyrogram,
        progress_args=(
            "Downloading ...",
            editable,
            c_time
        )
    )
    await editable.edit("Trying to Fetch Media Metadata ...")
    output = await execute(f"ffprobe -hide_banner -show_streams -print_format json {shlex.quote(the_media)}")
    if not output:
        await rm_dir(root_dl_loc)
        return await editable.edit("Can't fetch media info!")

    try:
        details = json.loads(output[0])
        middle_cmd = f"ffmpeg -i {shlex.quote(the_media)} -c copy -map 0"
        if title:
            middle_cmd += f' -metadata title="{title}"'
        for stream in details["streams"]:
            if (stream["codec_type"] == "video") and video_title:
                middle_cmd += f' -metadata:s:{stream["index"]} title="{video_title}"'
            elif (stream["codec_type"] == "audio") and audio_title:
                middle_cmd += f' -metadata:s:{stream["index"]} title="{audio_title}"'
            elif (stream["codec_type"] == "subtitle") and subtitle_title:
                middle_cmd += f' -metadata:s:{stream["index"]} title="{subtitle_title}"'
        dl_loc = dl_loc + str(time.time()).replace(".", "") + "/"
        if not os.path.isdir(dl_loc):
            os.makedirs(dl_loc)
        middle_cmd += f" {shlex.quote(dl_loc + new_file_name)}"
        await editable.edit("Please Wait ...\n\nProcessing Video ...")
        await execute(middle_cmd)
        await editable.edit("Renamed Successfully!")
    except Exception as e:
        # Clean Up
        await editable.edit("Failed to process video!")
        await rm_dir(root_dl_loc)
        return
    try: os.remove(the_media)
    except: pass
    upload_as_doc = await db.get_upload_as_doc(m.from_user.id)
    _default_thumb_ = await db.get_thumbnail(m.from_user.id)
    if not _default_thumb_:
        _m_attr = get_file_attr(m.reply_to_message)
        _default_thumb_ = _m_attr.thumbs[0].file_id \
            if (_m_attr and _m_attr.thumbs) \
            else None
    if _default_thumb_:
        _default_thumb_ = await c.download_media(_default_thumb_, root_dl_loc)
    if (not upload_as_doc) and m.reply_to_message.video:
        await c.send_video(
            chat_id=m.chat.id,
            video=f"{dl_loc}{new_file_name}",
            thumb=_default_thumb_ or None,
        )
    else:
        await c.send_document(
            chat_id=m.chat.id,
            document=f"{dl_loc}{new_file_name}",
            thumb=_default_thumb_ or None
        )
    await rm_dir(root_dl_loc)
    await editable.edit("Upload Successfully..!")
    
