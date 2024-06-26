from bot.client import Client
from pyrogram import filters
from pyrogram import types
from bot.core.db.add import add_user_to_database

@Client.on_message(filters.command("start") & filters.private)
async def ping_handler(c: Client, m: "types.Message"):
    if not m.from_user:
        return await m.reply_text("**I don't know about you, sir.**")
    await add_user_to_database(c, m)
    await c.send_message(
        chat_id=m.chat.id,
        text="**Hi, I am Star Bots Official Metadata Editor Bot!**\n\n"
             "**I can rename media without downloading it!**\n"
             "**Speed depends on your media DC. Change Your ⚙️ Settings in /settings Command.**\n\n"
             "**Just send me media and reply to it with /edit_metadata command.**",
        reply_markup=types.InlineKeyboardMarkup([[
            types.InlineKeyboardButton("Show Settings ⚙️",
                                       callback_data="showSettings")
        ]])
    )

@Client.on_message(filters.command("help") & filters.private)
async def help_handler(c: Client, m: "types.Message"):
    if not m.from_user:
        return await m.reply_text("**I don't know about you, sar.**")
    await add_user_to_database(c, m)
    await c.send_message(
        chat_id=m.chat.id,
        text="**I Can Rename Media Without Downloading It!**\n"
             "**Speed Depends on Your Media DC. Change Your ⚙️ Settings in /settings Command.**\n\n"
             "**Just send me media and reply to it with /edit_metadata command.**\n\n"
             "**To set custom thumbnail, reply to any image with /set_thumbnail**\n\n"
             "**To see custom thumbnail, press /show_thumbnail**",
        reply_markup=types.InlineKeyboardMarkup([[
            types.InlineKeyboardButton("Show Settings ⚙️",
                                       callback_data="showSettings")]])
    )

@Client.on_message(filters.command("settings") & filters.private)
async def settings_handler(c: Client, m: "types.Message"):
    if not m.from_user:
        return await m.reply_text("**I don't know about you, sir.**")
    await add_user_to_database(c, m)
    mention = m.from_user.mention
    await c.send_message(
        chat_id=m.chat.id,
        text=f"**Change ⚙️ Settings For {mention}**",
        reply_markup=types.InlineKeyboardMarkup([[
            types.InlineKeyboardButton("Show Settings ⚙️",
                                       callback_data="showSettings")
        ]])
    )
    
