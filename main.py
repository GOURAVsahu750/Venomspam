import asyncio
import random
import hashlib
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram.request import HTTPXRequest

# ================= CONFIG =================
BOT_TOKEN = "8097666609:AAEALj-SDPflW59oqAcgZf4ST0kBoQXEhOw"
OWNER_ID = 7957743011  # sirf ek owner

MASTER_EMOJIS = [
    "🔥","⚡","💀","👑","😈","🚀","💥","🌀","🧨","🎯",
    "🐉","🦁","☠️","🌪️","🌋","🩸","🧠","👁️","🦂","🦅"
]

# ============== EMOJI GENERATOR (TOKEN BASED) ==============
def generate_emojis(token: str):
    h = hashlib.sha256(token.encode()).hexdigest()
    random.seed(h)
    emojis = MASTER_EMOJIS.copy()
    random.shuffle(emojis)
    return emojis[:10]

EMOJIS = generate_emojis(BOT_TOKEN)

# ============== STORAGE ==============
gcnc_tasks = {}

# ============== HELPERS ==============
def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID

# ============== COMMANDS ==============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot is ONLINE & READY")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return
    await update.message.reply_text(
        "/spam <count> <text>\n"
        "/gcnc <group name>\n"
        "/stopgcnc"
    )

async def spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return

    if len(context.args) < 2:
        return await update.message.reply_text("Usage: /spam <count> <text>")

    try:
        count = int(context.args[0])
        text = " ".join(context.args[1:])
    except:
        return await update.message.reply_text("Invalid args")

    for _ in range(count):
        await update.message.reply_text(text)
        await asyncio.sleep(0.1)

async def gcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return

    chat = update.effective_chat
    if chat.type not in ["group", "supergroup"]:
        return await update.message.reply_text("Group only")

    if not context.args:
        return await update.message.reply_text("Usage: /gcnc <group name>")

    base_name = " ".join(context.args)

    async def loop():
        index = 0
        while True:
            try:
                emoji = EMOJIS[index % len(EMOJIS)]
                await chat.set_title(f"{emoji} {base_name}")
                index += 1
                await asyncio.sleep(0.7)  # 🔥 FAST & NON-STOP
            except Exception:
                await asyncio.sleep(1)

    if chat.id in gcnc_tasks:
        gcnc_tasks[chat.id].cancel()

    gcnc_tasks[chat.id] = asyncio.create_task(loop())
    await update.message.reply_text("✅ GCNC STARTED (NON-STOP)")

async def stopgcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return

    chat = update.effective_chat
    task = gcnc_tasks.pop(chat.id, None)

    if task:
        task.cancel()
        await update.message.reply_text("🛑 GCNC STOPPED")
    else:
        await update.message.reply_text("No GCNC running")

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type not in ["group", "supergroup"]:
        return
    for m in update.message.new_chat_members:
        await update.message.reply_text(f"👋 Welcome {m.mention_html()}!", parse_mode="HTML")

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_owner(update.effective_user.id):
        await update.message.reply_text("❓ Unknown command")

# ================= MAIN =================
def main():
    request = HTTPXRequest(
        connection_pool_size=1,
        connect_timeout=60,
        read_timeout=60,
        write_timeout=60,
    )

    app = Application.builder() \
        .token(BOT_TOKEN) \
        .request(request) \
        .build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("spam", spam))
    app.add_handler(CommandHandler("gcnc", gcnc))
    app.add_handler(CommandHandler("stopgcnc", stopgcnc))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    app.add_handler(MessageHandler(filters.COMMAND, unknown))

    print("✅ BOT STARTED SUCCESSFULLY")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
