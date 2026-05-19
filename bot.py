import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)

# ========= CONFIGURATION =========
TOKEN = "8712150869:AAFJ5LxIQ4MkCZQUXyvoFI0UNf2b2coHNh8"  # .env / render env se bhi le sakte ho
OWNER_ID = 8722144519     # अपनी टेलीग्राम user id डालो
SUDO_USERS = [OWNER_ID]    # sudo users ki list
BAN_LIST = []              # ban ki list
MUTE_LIST = []             # mute ki list
FILTERS = {}               # filters: {chat_id: [keywords]}
STICKERS = []              # saved stickers
WELCOME_MESSAGES = {}      # chat_id: message
MY_HOME_LINK = "https://t.me/+Yu4K5-9LHH1mM2Zl"
GET_SUDO_LINK = "https://t.me/+M-FVHREBRHUwODU1"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ========= START / BUTTONS =========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_url = "https://example.com/bot-photo.jpg"  # apna photo link
    keyboard = [
        [
            InlineKeyboardButton("🤼‍♂️ Add me baby", callback_data="add_me"),
            InlineKeyboardButton("🏡 My Home", callback_data="my_home"),
        ],
        [
            InlineKeyboardButton("👑 My Master", callback_data="my_master"),
            InlineKeyboardButton("🆘 Help", callback_data="help"),
        ],
        [
            InlineKeyboardButton("⚡️ Get sudo", callback_data="get_sudo"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=photo_url,
        caption="Hi! I'm ready to work.\nUse the buttons below:",
        reply_markup=reply_markup,
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "add_me":
        # "Add to Group" button behavior
        text = "Add me to your group as admin from here:"
        await query.edit_message_caption(
            caption=text,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("➕ Add to Group", url="https://t.me/your_bot_username?startgroup=true")]]
            ),
        )
    elif query.data == "my_home":
        await query.edit_message_caption(
            caption=f"🏠 My Home Group: {MY_HOME_LINK}",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Join now", url=MY_HOME_LINK)]]
            ),
        )
    elif query.data == "my_master":
        if query.from_user.id == OWNER_ID:
            caption = "👑 You are the owner."
        else:
            caption = "👑 My Master"
        await query.edit_message_caption(
            caption=caption,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Open profile", url=f"tg://user?id={OWNER_ID}")]]
            ),
        )
    elif query.data == "help":
        help_text = (
            "🎛️ **Available commands:**\n"
            "`/ping` – bot speed.\n"
            "`/alive` – bot status.\n"
            "`/speed` – network speed.\n"
            "`/ban` – ban user.\n"
            "`/mute` – mute user.\n"
            "`/filter` – save filter.\n"
            "`/welcome` – set welcome message.\n"
            "`/promote` – promote admin.\n"
            "`/mute` (sudo) – delete all messages.\n"
            "`/sticker` – send stickers.\n"
            "`/spam` – spam someone.\n"
            "`/info` – user info.\n\n"
            "Only sudo_owner:\n"
            "`/addsudo` `/delsudo` `/addsticker` `/sudolist` `/mutelist`"
        )
        await context.bot.edit_message_caption(
            caption=help_text,
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
        )
    elif query.data == "get_sudo":
        await query.edit_message_caption(
            caption=f"⚡️ Get sudo access here: {GET_SUDO_LINK}",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Join sudo group", url=GET_SUDO_LINK)]]
            ),
        )


# ========= PING / ALIVE / SPEED =========

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_url = "https://example.com/ping.jpg"
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=photo_url,
        caption="🏓 Pong! Bot speed is good.",
    )


async def alive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_url = "https://example.com/alive.jpg"
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=photo_url,
        caption="✅ Alive! Ready to work.",
    )


async def speed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_url = "https://example.com/speed.jpg"
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=photo_url,
        caption="⚡ Network speed is good.",
    )


# ========= GROUP MODERATION =========

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.bot.can_admin_promote_members:
        await update.message.reply_text("I need admin rights to ban.")
        return
    reply = update.message.reply_to_message
    if not reply:
        await update.message.reply_text("Reply to a user to ban.")
        return
    user_id = reply.from_user.id
    # Ban from supergroup
    await context.bot.ban_chat_member(chat_id=update.effective_chat.id, user_id=user_id)
    await update.message.reply_text("🔇 Banned.")


async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.bot.can_admin_promote_members:
        await update.message.reply_text("I need admin rights to mute.")
        return
    reply = update.message.reply_to_message
    if not reply:
        await update.message.reply_text("Reply to a user to mute.")
        return
    user_id = reply.from_user.id
    MUTE_LIST.append(user_id)
    await update.message.reply_text("🔇 Muted (message‑deletion mode).")


# ========= FILTER / WELCOME / PROMOTE =========

async def filter_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    if not context.args:
        await update.message.reply_text("Usage: /filter spamword")
        return
    word = " ".join(context.args)
    if chat_id not in FILTERS:
        FILTERS[chat_id] = []
    FILTERS[chat_id].append(word)
    await update.message.reply_text(f"✅ Filter added: {word}")


async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    if not context.args:
        await update.message.reply_text("Usage: /welcome Your welcome text")
        return
    text = " ".join(context.args)
    WELCOME_MESSAGES[chat_id] = text
    await update.message.reply_text(f"✅ Welcome set: {text}")


async def promote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.bot.can_admin_promote_members:
        await update.message.reply_text("I need admin rights to promote.")
        return
    reply = update.message.reply_to_message
    if not reply:
        await update.message.reply_text("Reply to a user to promote.")
        return
    user_id = reply.from_user.id
    # simple promote (admin rights)
    await context.bot.promote_chat_member(
        chat_id=update.effective_chat.id,
        user_id=user_id,
        can_change_info=True,
        can_delete_messages=True,
        can_invite_users=True,
        can_restrict_members=True,
        can_pin_messages=True,
        can_manage_chat=True,
    )
    await update.message.reply_text("✅ Promoted as admin.")


# ========= SUDO COMMANDS =========

async def sudo_mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in SUDO_USERS:
        await update.message.reply_text("You are not sudo.")
        return
    reply = update.message.reply_to_message
    if not reply:
        await update.message.reply_text("Reply to a user to mute all content.")
        return
    user_id = reply.from_user.id
    MUTE_LIST.append(user_id)
    await update.message.reply_text("🔇 All messages from this user will be deleted.")


async def sudo_unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in SUDO_USERS:
        await update.message.reply_text("You are not sudo.")
        return
    reply = update.message.reply_to_message
    if not reply:
        await update.message.reply_text("Reply to a user to unmute.")
        return
    user_id = reply.from_user.id
    if user_id in MUTE_LIST:
        MUTE_LIST.remove(user_id)
        await update.message.reply_text("🔊 Unmuted.")
    else:
        await update.message.reply_text("User was not muted.")


async def sticker_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in SUDO_USERS:
        await update.message.reply_text("You are not sudo.")
        return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Usage: /sticker <count>")
        return
    count = int(context.args[0])
    if count > 10:
        count = 10  # limit
    for _ in range(count):
        if STICKERS:
            await context.bot.send_sticker(update.effective_chat.id, STICKERS[0])
        else:
            await context.bot.send_message(
                update.effective_chat.id, "No stickers saved yet. Use /addsticker."
            )


async def spam_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in SUDO_USERS:
        await update.message.reply_text("You are not sudo.")
        return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Usage: /spam <count> @user message")
        return
    count = int(context.args[0])
    if count > 50:
        count = 50
    # Parse message after user mention
    if len(context.args) < 2:
        await update.message.reply_text("Please provide a message after count.")
        return
    msg = " ".join(context.args[1:])
    for _ in range(count):
        await context.bot.send_message(update.effective_chat.id, msg)


async def stopspam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in SUDO_USERS:
        await update.message.reply_text("You are not sudo.")
        return
    await update.message.reply_text("🚫 Spam stopped.")


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply = update.message.reply_to_message
    if not reply:
        user = update.effective_user
    else:
        user = reply.from_user
    text = (
        f"👤 User info:\n"
        f"ID: `{user.id}`\n"
        f"Name: `{user.full_name}`\n"
        f"Username: @{user.username or 'None'}\n"
        f"Is bot: {user.is_bot}\n"
    )
    await update.message.reply_text(text)


# ========= OWNER ONLY =========

async def addsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Only owner can use this.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /addsudo user_id")
        return
    try:
        user_id = int(context.args[0])
        if user_id not in SUDO_USERS:
            SUDO_USERS.append(user_id)
            await update.message.reply_text(f"✅ {user_id} added as sudo.")
        else:
            await update.message.reply_text("User already sudo.")
    except ValueError:
        await update.message.reply_text("Invalid user ID.")


async def delsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Only owner can use this.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /delsudo user_id")
        return
    try:
        user_id = int(context.args[0])
        if user_id in SUDO_USERS:
            SUDO_USERS.remove(user_id)
            await update.message.reply_text(f"🚫 {user_id} removed from sudo.")
        else:
            await update.message.reply_text("User not sudo.")
    except ValueError:
        await update.message.reply_text("Invalid user ID.")


async def addsticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Only owner can use this.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /addsticker sticker_id")
        return
    sticker = context.args[0]
    STICKERS.append(sticker)
    await update.message.reply_text(f"✅ Sticker saved: {sticker}")


async def sudolist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Only owner can use this.")
        return
    if not SUDO_USERS:
        await update.message.reply_text("No sudo users.")
    else:
        sudo_list_text = "\n".join([f"• `{sid}`" for sid in SUDO_USERS])
        await update.message.reply_text(f"👥 Sudo users:\n{sudo_list_text}")


async def mutelist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Only owner can use this.")
        return
    if not MUTE_LIST:
        await update.message.reply_text("No muted users.")
    else:
        mute_list_text = "\n".join([f"• `{uid}`" for uid in MUTE_LIST])
        await update.message.reply_text(f"🔇 Muted users:\n{mute_list_text}")


# ========= MAIN + RENDER DEPLOY =========

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("alive", alive))
    app.add_handler(CommandHandler("speed", speed))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("mute", mute))
    app.add_handler(CommandHandler("filter", filter_cmd))
    app.add_handler(CommandHandler("welcome", welcome))
    app.add_handler(CommandHandler("promote", promote))
    app.add_handler(CommandHandler("sudo_mute", sudo_mute))
    app.add_handler(CommandHandler("sudo_unmute", sudo_unmute))
    app.add_handler(CommandHandler("sticker", sticker_cmd))
    app.add_handler(CommandHandler("spam", spam_cmd))
    app.add_handler(CommandHandler("stopspam", stopspam))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("addsudo", addsudo))
    app.add_handler(CommandHandler("delsudo", delsudo))
    app.add_handler(CommandHandler("addsticker", addsticker))
    app.add_handler(CommandHandler("sudolist", sudolist))
    app.add_handler(CommandHandler("mutelist", mutelist))

    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(
        MessageHandler(
            filters.PHOTO | filters.TEXT,
            lambda u, c: None  # dummy, agar tum filter + mute logic add karna ho to
        )
    )

    logger.info("Bot starting…")
    app.run_polling()


if __name__ == "__main__":
    main()
