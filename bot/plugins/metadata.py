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

@Client.on_message(filters.private & (filters.video | filters.document | filters.audio))
async def Edit_Metadata(c: Client, m: Message):
    default_f_name = get_media_file_name(m)
    title = (await db.get_title(m.from_user.id)) or "StarMovies.hop.sh"
    caption = await db.get_caption(m.from_user.id)
    if m.from_user.id not in Config.PRO_USERS:
        is_in_gap, sleep_time = await check_time_gap(m.from_user.id)
        if is_in_gap:
            await m.reply_text("**Sorry Sir,**\n"
                               "**No Flooding Allowed!**\n\n"
                               f"**Send After `{str(sleep_time)}s`..!!**",
                               quote=True)
            return
    await add_user_to_database(c, m)
    editable = await m.reply_text(f"**Current File Name :-** `{default_f_name}` \n**File Caption :-** {caption}\n**Current Title :-** `{title}` \n**You Can Change Your Settings from /settings Command.\nNow Send me New File Name..!**", quote=True)
    user_input_msg: Message = await c.listen(m.chat.id)
    if user_input_msg.text is None:
        await editable.edit("**Process Cancelled!**")
        return await user_input_msg.continue_propagation()
    if user_input_msg.text and user_input_msg.text.startswith("/"):
        await editable.edit("**Process Cancelled!**")
        return await user_input_msg.continue_propagation()
    if user_input_msg.text.rsplit(".", 1)[-1].lower() != default_f_name.rsplit(".", 1)[-1].lower():
        file_name = user_input_msg.text.rsplit(".", 1)[0][:255] + "." + default_f_name.rsplit(".", 1)[-1].lower()
    else:
        new_file_name = user_input_msg.text
    await editable.edit("Please Wait ...")
    newfile_name = f"{default_f_name.rsplit('.', 1)[0] if default_f_name else 'output'}.mkv"
    await editable.edit("**Downloading Video...**")
    dl_loc = Config.DOWNLOAD_DIR + "/" + str(m.from_user.id) + "/"
    root_dl_loc = dl_loc
    stream = shlex.quote(dl_loc + new_file_name) # Config.DOWNLOAD_DIR + "/" + str(m.from_user.id) + "/", f"{new_file_name}"
    if not os.path.isdir(dl_loc):
        os.makedirs(dl_loc)
    c_time = time.time()
    the_media = await c.download_media(
        message=m,
        file_name=dl_loc,
        progress=display_progress_for_pyrogram,
        progress_args=(
            "**Downloading...**",
            editable,
            c_time
        )
    )
    await editable.edit("**Trying to Fetch Media Metadata...**")
    output = await execute(f"ffprobe -hide_banner -show_streams -print_format json {shlex.quote(the_media)}")
    if not output:
        await rm_dir(root_dl_loc)
        return await editable.edit("**Can't Fetch Media Info!**")
    try:
        details = json.loads(output[0])
        middle_cmd = f"ffmpeg -i {shlex.quote(the_media)} -c copy -map 0"
        if title:
            middle_cmd += f' -metadata title="{title}"'
        for stream in details["streams"]:
            if (stream["codec_type"] == "video") and title:
                middle_cmd += f' -metadata:s:{stream["index"]} title="{title}"'
            elif (stream["codec_type"] == "audio") and title:
                middle_cmd += f' -metadata:s:{stream["index"]} title="{title}"'
            elif (stream["codec_type"] == "subtitle") and title:
                middle_cmd += f' -metadata:s:{stream["index"]} title="{title}"'
        dl_loc = dl_loc + str(time.time()).replace(".", "") + "/"
        if not os.path.isdir(dl_loc):
            os.makedirs(dl_loc)
        middle_cmd += f" {shlex.quote(dl_loc + new_file_name)}"
        await editable.edit("**Please Wait ...\n\nProcessing Video...**")
        await execute(middle_cmd)
        await editable.edit("**Renamed Successfully!**")
    except:
        # Clean Up
        await editable.edit("**Failed to Process Video!**")
        await rm_dir(root_dl_loc)
        return
    upload_as_doc = await db.get_upload_as_doc(m.from_user.id)
    _default_thumb_ = await db.get_thumbnail(m.from_user.id)
    if not _default_thumb_:
        _m_attr = get_file_attr(m)
        _default_thumb_ = _m_attr.thumbs[0].file_id \
            if (_m_attr and _m_attr.thumbs) \
            else None
    file_size = get_media_file_size(m)
    file_caption = await db.get_caption(m.from_user.id)
    if file_caption:
         try:
             caption = file_caption.format(file_name=new_file_name, file_size=file_size, duration=convert(duration))
         except Exception as e:
             await editable.edit(text=f"**Your caption Error Unexpected Keyword ●> {e}**")
             return 
    else:
        caption = f"**{new_file_name}**"
    if _default_thumb_:
        _default_thumb_ = await c.download_media(_default_thumb_, root_dl_loc)
    if (not upload_as_doc) and m.video:
        await c.send_video(
            chat_id=m.chat.id,
            video=f"{dl_loc}{new_file_name}",
            caption=caption,
            duration=duration,
            thumb=_default_thumb_ or None,
            editable_message=editable,
        )
    else:
        await c.send_document(
            chat_id=m.chat.id,
            document=f"{dl_loc}{new_file_name}",
            caption=caption,
            duration=duration,
            thumb=_default_thumb_ or None,
            editable_message=editable,
        )
    await rm_dir(root_dl_loc)
