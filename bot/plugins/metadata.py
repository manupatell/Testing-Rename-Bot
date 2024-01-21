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
from pyrogram import filters
from pyrogram.types import Message
from bot.core.file_info import (
    get_media_file_name
)
from bot.core.db.database import db
from bot.core.utils.rm import rm_dir
from bot.core.utils.executor import execute
from bot.core.db.add import add_user_to_database
from bot.core.display import progress_for_pyrogram
from bot.core.file_info import get_file_attr

@Client.on_message((filters.video | filters.document) & ~filters.private & ~filters.edited)
async def Edit_Metadata(c: Client, m: Message):
    default_f_name = get_media_file_name(m.reply_to_message)
    title = (await db.get_titles(m.from_user.id)) or "StarMovies.hop.sh"
    await add_user_to_database(c, m)
    editable = await m.reply_text(f"**Current File Name :-** `{default_f_name}` \n**Current Title :-** `{title}` \n**Now Send me New File Name..!**", quote=True)
    user_input_msg: Message = await c.listen(m.chat.id)
    if user_input_msg.text is None:
        await editable.edit("Process Cancelled!")
        return await user_input_msg.continue_propagation()
    if user_input_msg.text and user_input_msg.text.startswith("/"):
        await editable.edit("Process Cancelled!")
        return await user_input_msg.continue_propagation()
    if user_input_msg.text.rsplit(".", 1)[-1].lower() != default_f_name.rsplit(".", 1)[-1].lower():
        file_name = user_input_msg.text.rsplit(".", 1)[0][:60] + "." + default_f_name.rsplit(".", 1)[-1].lower()
    else:
        new_file_name = user_input_msg.text[:60]
    await editable.edit("Please Wait ...")
    newfile_name = f"{default_f_name.rsplit('.', 1)[0] if default_f_name else 'output'}.mkv"
    file_type = m.reply_to_message.video or m.reply_to_message.document
    if not file_type.mime_type.startswith("video/"):
        await m.reply_text("This is not a Video!", True)
        return
    await editable.edit("Downloading Video ...")
    dl_loc = Config.DOWNLOAD_DIR + "/" + str(m.from_user.id) + "/" + str(m.message_id) + "/"
    root_dl_loc = dl_loc
    stream = f"{dl_loc}{new_file_name}"
    if not os.path.isdir(dl_loc):
        os.makedirs(dl_loc)
    c_time = time.time()
    the_media = await c.download_media(
        message=m.reply_to_message,
        file_name=dl_loc,
        progress=progress_for_pyrogram,
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
        await editable.edit("Please Wait ...\n\nProcessing Video ...")
        await execute(middle_cmd)
        await editable.edit("Renamed Successfully!")
    except:
        # Clean Up
        await editable.edit("Failed to process video!")
        await rm_dir(root_dl_loc)
        return
    try: os.remove(the_media)
    except: pass
    file_size = os.path.getsize(stream)
    if (int(file_size) > 2097152000) and (Config.ALLOW_UPLOAD_TO_STREAMTAPE is True) and (Config.STREAMTAPE_API_USERNAME != "NoNeed") and (Config.STREAMTAPE_API_PASS != "NoNeed"):
        await editable.edit(f"Sorry Sir,\n\nFile Size Become {naturalsize(file_size)} !!\nI can't Upload to Telegram!\n\nSo Now Uploading to Streamtape ...")
        try:
            async with aiohttp.ClientSession() as session:
                Main_API = "https://api.streamtape.com/file/ul?login={}&key={}"
                hit_api = await session.get(Main_API.format(Config.STREAMTAPE_API_USERNAME, Config.STREAMTAPE_API_PASS))
                json_data = await hit_api.json()
                temp_api = json_data["result"]["url"]
                files = {'file1': open(stream, 'rb')}
                response = await session.post(temp_api, data=files)
                data_f = await response.json(content_type=None)
                download_link = data_f["result"]["url"]
                filename = stream.split("/")[-1].replace("_"," ")
                text_edit = f"File Uploaded to Streamtape!\n\n**File Name:** `{filename}`\n**Size:** `{naturalsize(file_size)}`\n**Link:** `{download_link}`"
                await editable.edit(text_edit, parse_mode="Markdown", disable_web_page_preview=True, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Open Link", url=download_link)]]))
        except Exception as e:
            print(f"Error: {e}")
            await editable.edit("Sorry, Something went wrong!\n\nCan't Upload to Streamtape. You can report at [Support Group](https://t.me/linux_repo).")
        await rm_dir(root_dl_loc)
        return
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
        await c.upload_video(
            chat_id=m.chat.id,
            video=f"{dl_loc}{new_file_name}",
            thumb=_default_thumb_ or None,
            editable_message=editable,
        )
    else:
        await c.upload_document(
            chat_id=m.chat.id,
            document=f"{dl_loc}{new_file_name}",
            editable_message=editable,
            thumb=_default_thumb_ or None
        )
    await rm_dir(root_dl_loc)
    
