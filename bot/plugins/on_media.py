import asyncio
from bot.client import Client
from bot.core.db.add import (
    add_user_to_database
)
from pyrogram import (
    filters,
    types
)


@Client.on_message((filters.video | filters.audio | filters.document) & ~filters.channel & ~filters.edited)
async def on_media_handler(c: Client, m: "types.Message"):
    if not m.from_user:
        return await m.reply_text("I Don't Know About you Bro/Sis..")
    await add_user_to_database(c, m)
    await asyncio.sleep(3)
    await c.send_flooded_message(
        chat_id=m.chat.id,
        text="**Select the Your wish to Execute the Process**",
        reply_markup=types.InlineKeyboardMarkup(
            [[types.InlineKeyboardButton("Edit Metadata", callback_data="EditMetadata"),
              types.InlineKeyboardButton("Rename File", callback_data="RenameFile"),
              types.InlineKeyboardButton("Media Information", callback_data="showFileInfo")
              types.InlineKeyboardButton("Not Now", callback_data="closeMessage")]]
        ),
        disable_web_page_preview=True,
        reply_to_message_id=m.message_id
    )
