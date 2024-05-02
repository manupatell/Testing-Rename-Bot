import asyncio
from pyrogram import types, errors, enums
from configs import Config
from bot.core.db.database import db

async def show_settings(m: "types.Message"):
    usr_id = m.chat.id
    user_data = await db.get_user_data(usr_id)
    if not user_data:
        await m.edit("Failed to fetch your data from database!")
        return
    upload_as_doc = user_data.get("upload_as_doc", False)
    caption = user_data.get("caption", None)
    apply_caption = user_data.get("apply_caption", True)
    thumbnail = user_data.get("thumbnail", None)
    title = user_data.get("title", None)
    buttons_markup = [
        [types.InlineKeyboardButton(f"Upload as Doc {'✅' if upload_as_doc else '❌'}",
                                    callback_data="triggerUploadMode")],
        [types.InlineKeyboardButton(f"Apply Caption {'✅' if apply_caption else '❌'}",
                                    callback_data="triggerApplyCaption")],
        [types.InlineKeyboardButton(f"Apply Default Caption {'❌' if caption else '✅'}",
                                    callback_data="triggerApplyDefaultCaption")],
        [types.InlineKeyboardButton(f"{'Change' if caption else 'Set'} Custom Caption",
                                    callback_data="setCustomCaption")],
        [types.InlineKeyboardButton(f"{'Change' if title else 'Set'} Title",
                                    callback_data="setTitle")],
        [types.InlineKeyboardButton(f"{'Change' if thumbnail else 'Set'} Thumbnail",
                                    callback_data="setThumbnail")]
    ]
    if thumbnail:
        buttons_markup.append([types.InlineKeyboardButton("Show Thumbnail",
                                                          callback_data="showThumbnail")])
    if title:
        buttons_markup.append([types.InlineKeyboardButton("Show Title",
                                                          callback_data="showTitle")])
    if caption:
        buttons_markup.append([types.InlineKeyboardButton("Show Caption",
                                                          callback_data="showCaption")])
    buttons_markup.append([types.InlineKeyboardButton("Close Message",
                                                      callback_data="closeMessage")])

    try:
        await m.edit(
            text="**Here You Can setup Your ⚙️ Settings:**",
            reply_markup=types.InlineKeyboardMarkup(buttons_markup),
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.MARKDOWN
        )
    except errors.MessageNotModified: pass
    except errors.FloodWait as e:
        await asyncio.sleep(e.x)
        await show_settings(m)
    except Exception as err:
        Config.LOGGER.getLogger(__name__).error(err)
