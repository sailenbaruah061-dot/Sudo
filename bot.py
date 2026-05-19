import json
import time
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)

BOT_TOKEN = "8712150869:AAFJ5LxIQ4MkCZQUXyvoFI0UNf2b2coHNh8"
OWNER_ID = 8722144519
OWNER_USERNAME = "@ll_DARK_GETO_ll"
HOME_GROUP = "https://t.me/+q1gqCcwSp8g4MjY1"
SUDO_GROUP = "https://t.me/+M-FVHREBRHUwODU1"
PHOTO = "https://ibb.co/pj863YbY"

DATA_FILE = "data.json"


def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        data = {
            "sudo": [],
            "filters": {},
            "welcome": True,
            "stickers": []
        }
        save_data(data)
        return data


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def is_owner(uid):
    return uid == OWNER_ID


def is_sudo(uid, data):
    return uid == OWNER_ID or uid in data["sudo"]


# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("➕ Add Me Baby", url="https://t.me/YOUR_BOT_USERNAME?startgroup=true")],
        [InlineKeyboardButton("🏠 My Home", url=HOME_GROUP)],
        [InlineKeyboardButton("👑 My Master", url=f"https://t.me/{OWNER_USERNAME}")],
        [InlineKeyboardButton("🆘 Help", callback_data="help")],
        [InlineKeyboardButton("⭐ Get Sudo", url=SUDO_GROUP)]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_photo(
        photo=PHOTO,
        caption="✨ Ready To Work ✨",
        reply_markup=reply_markup
    )


# BUTTONS
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "help":
        txt = """
AVAILABLE COMMANDS

/ping
/alive
/speed
/ban
/mute
/unmute
/promote
/filter
/mention
/info
/addsudo
/delsudo
/sudolist
/mutelist
/addsticker
"""
        await query.message.reply_text(txt)


# PING
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start = time.time()
    msg = await update.message.reply_text("Checking...")
    end = time.time()
    speed = round((end - start) * 1000)

    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=PHOTO,
        caption=f"🏓 Pong: {speed} ms"
    )

    await msg.delete()


# ALIVE
async def alive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=PHOTO,
        caption="✅ Bot Ready To Work"
    )


# SPEED
async def speed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ping(update, context)


# BAN
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return

    user = update.message.reply_to_message.from_user.id

    try:
        await context.bot.ban_chat_member(update.effective_chat.id, user)
        await update.message.reply_text("✅ User banned")
    except:
        await update.message.reply_text("❌ Ban failed")


# MUTE
async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return

    user = update.message.reply_to_message.from_user.id

    try:
        await context.bot.restrict_chat_member(
            chat_id=update.effective_chat.id,
            user_id=user,
            permissions={}
        )
        await update.message.reply_text("🔇 User muted")
    except:
        await update.message.reply_text("❌ Mute failed")


# UNMUTE
async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return

    user = update.message.reply_to_message.from_user.id

    try:
        from telegram import ChatPermissions

        await context.bot.restrict_chat_member(
            chat_id=update.effective_chat.id,
            user_id=user,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True
            )
        )
        await update.message.reply_text("✅ User unmuted")
    except:
        await update.message.reply_text("❌ Unmute failed")


# PROMOTE
async def promote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return

    user = update.message.reply_to_message.from_user.id

    try:
        await context.bot.promote_chat_member(
            update.effective_chat.id,
            user,
            can_delete_messages=True,
            can_manage_chat=True,
            can_restrict_members=True
        )

        await update.message.reply_text("👑 User promoted")
    except:
        await update.message.reply_text("❌ Promote failed")


# INFO
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return

    u = update.message.reply_to_message.from_user

    txt = f"""
USER INFO

ID: {u.id}
Name: {u.first_name}
Username: @{u.username}
Premium: {u.is_premium}
"""

    await update.message.reply_text(txt)


# ADD SUDO
async def addsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()

    if not is_owner(update.effective_user.id):
        return

    if not update.message.reply_to_message:
        return

    uid = update.message.reply_to_message.from_user.id

    if uid not in data["sudo"]:
        data["sudo"].append(uid)
        save_data(data)

    await update.message.reply_text("✅ Added to sudo")


# DEL SUDO
async def delsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()

    if not is_owner(update.effective_user.id):
        return

    if not update.message.reply_to_message:
        return

    uid = update.message.reply_to_message.from_user.id

    if uid in data["sudo"]:
        data["sudo"].remove(uid)
        save_data(data)

    await update.message.reply_text("❌ Removed from sudo")


# SUDO LIST
async def sudolist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()

    txt = "SUDO USERS\n\n"

    for x in data["sudo"]:
        txt += f"• {x}\n"

    await update.message.reply_text(txt)


# SAVE STICKER
async def addsticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()

    if not update.message.reply_to_message:
        return

    if not update.message.reply_to_message.sticker:
        return

    sid = update.message.reply_to_message.sticker.file_id

    if sid not in data["stickers"]:
        data["stickers"].append(sid)
        save_data(data)

    await update.message.reply_text("✅ Sticker saved")


# WELCOME
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for user in update.message.new_chat_members:
        await update.message.reply_text(
            f"Welcome {user.first_name} 🎉"
        )


# FILTER SAVE
async def save_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()

    text = update.message.text

    if text.startswith("/filter "):
        try:
            _, word, reply = text.split(" ", 2)
            data["filters"][word.lower()] = reply
            save_data(data)
            await update.message.reply_text("✅ Filter saved")
        except:
            await update.message.reply_text("Usage: /filter hello Hi")


# FILTER CHECK
async def check_filters(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()

    text = update.message.text.lower()

    for word, reply in data["filters"].items():
        if word in text:
            await update.message.reply_text(reply)


# MENTION
async def mention(update: Update, context: ContextTypes.DEFAULT_TYPE):
    members = []

    async for m in context.bot.get_chat_administrators(update.effective_chat.id):
        members.append(f"@{m.user.username}")

    await update.message.reply_text(" ".join(members))


# MAIN

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))

    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("alive", alive))
    app.add_handler(CommandHandler("speed", speed))

    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("mute", mute))
    app.add_handler(CommandHandler("unmute", unmute))
    app.add_handler(CommandHandler("promote", promote))

    app.add_handler(CommandHandler("info", info))

    app.add_handler(CommandHandler("addsudo", addsudo))
    app.add_handler(CommandHandler("delsudo", delsudo))
    app.add_handler(CommandHandler("sudolist", sudolist))

    app.add_handler(CommandHandler("addsticker", addsticker))

    app.add_handler(CommandHandler("mention", mention))

    app.add_handler(
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome)
    )

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, check_filters)
    )

    app.add_handler(
        MessageHandler(filters.TEXT & filters.Regex(r"^/filter"), save_filter)
    )

    print("BOT ONLINE ✅")

    app.run_polling()


if __name__ == "__main__":
    main()
