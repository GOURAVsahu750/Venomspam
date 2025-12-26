import asyncio
import random
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from telegram.error import RetryAfter, BadRequest

# -------- CONFIG --------
BOT_TOKEN = "8528820614:AAFwUeP0SAABfDq1yxCZL3jxCccr9KJB530"

# 🔐 ONLY ONE OWNER
OWNER_ID = 7957743011

# ⚡ FASTEST SAFE DELAY (NON-STOP)
DELAY = 0.6  # isse kam karoge to Telegram 30s wait dega

# 🔥 EMOJI LIST (ROTATE ONLY EMOJI, NO NUMBER)
EMOJIS = [
    "🔥","⚡","💥","🚀","🧨","🌋","🌪️","☄️",
    "👑","😈","☠️","🩸","⚔️","🗡️","🐉","🦅"
]

# -------- STORAGE --------
gcnc_tasks = {}

# -------- HELPERS --------
def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID

# -------- COMMANDS --------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return
    await update.message.reply_text(
        "🤖 Bot Online\n"
        "Commands:\n"
        "/gcnc <group_name>\n"
        "/stopgcnc"
    )

async def spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return
    if len(context.args) < 2:
        return
    count = int(context.args[0])
    text = " ".join(context.args[1:])
    for _ in range(count):
        await update.message.reply_text(text)
        await asyncio.sleep(0.12)

# -------- GCNC (FAST + UNLIMITED) --------
async def gcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return

    chat = update.effective_chat
    if chat.type not in ["group", "supergroup"]:
        return

    if not context.args:
        return await update.message.reply_text("Usage: /gcnc <group_name>")

    base = " ".join(context.args)

    async def loop():
        idx = 0
        while True:
            try:
                emoji = EMOJIS[idx % len(EMOJIS)]
                idx += 1

                await chat.set_title(f"{emoji} {base}")

                # 🔥 FAST + STABLE + NON-STOP
                await asyncio.sleep(DELAY)

            except RetryAfter as e:
                # Telegram ne jitna bola utna wait, phir auto resume
                await asyncio.sleep(e.retry_after + 0.5)

            except BadRequest:
                # same title / minor issue
                await asyncio.sleep(0.2)

            except asyncio.CancelledError:
                break

            except Exception:
                await asyncio.sleep(1)

    # agar pehle se running hai to cancel
    if chat.id in gcnc_tasks:
        gcnc_tasks[chat.id].cancel()

    gcnc_tasks[chat.id] = context.application.create_task(loop())
    await update.message.reply_text("✅ GCNC started (NON-STOP MODE)")

async def stopgcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return
    task = gcnc_tasks.pop(update.effective_chat.id, None)
    if task:
        task.cancel()
        await update.message.reply_text("🛑 GCNC stopped")

# -------- MAIN --------
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("spam", spam))
    app.add_handler(CommandHandler("gcnc", gcnc))
    app.add_handler(CommandHandler("stopgcnc", stopgcnc))
    app.add_handler(MessageHandler(filters.COMMAND, lambda u, c: None))

    app.run_polling()

if __name__ == "__main__":
    main()