import os
import logging
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)

from database import get_user, update_user, add_order

# ─── إعدادات ─────────────────────
TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.environ.get("ADMIN_CHAT_ID", "0"))
ADMIN = os.environ.get("ADMIN_USERNAME", "@admin")
VODAFONE_NUMBER = os.environ.get("VODAFONE_NUMBER")
USDT_ADDRESS = os.environ.get("USDT_ADDRESS")

# ─── Logging ─────────────────────
logging.basicConfig(level=logging.INFO)

# ─── Rate Limit ──────────────────
last_message_time = {}

def is_spam(user_id):
    now = time.time()
    last = last_message_time.get(user_id, 0)
    if now - last < 2:
        return True
    last_message_time[user_id] = now
    return False

# ─── Helpers ─────────────────────
def user_tag(user):
    return f"{user.first_name} (@{user.username})" if user.username else f"{user.first_name} ({user.id})"

async def notify_admin(context, text):
    if ADMIN_CHAT_ID:
        await context.bot.send_message(ADMIN_CHAT_ID, text)

# ─── Commands ────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("📺 اشتراك", callback_data="sub")]]
    await update.message.reply_text("أهلاً بيك 👋", reply_markup=InlineKeyboardMarkup(keyboard))

async def admin_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_CHAT_ID:
        return
    from database import load_data
    data = load_data()
    orders = data["orders"][-5:]
    text = "\n\n".join([str(o) for o in orders]) or "لا يوجد طلبات"
    await update.message.reply_text(text)

# ─── Buttons ─────────────────────
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if is_spam(user_id):
        return

    if query.data == "sub":
        keyboard = [
            [InlineKeyboardButton("5 قنوات", callback_data="pkg_5")],
            [InlineKeyboardButton("15 قناة", callback_data="pkg_15")],
        ]
        await query.edit_message_text("اختار:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data.startswith("pkg"):
        update_user(user_id, {"package": query.data})
        keyboard = [
            [InlineKeyboardButton("فودافون", callback_data="vodafone")],
            [InlineKeyboardButton("USDT", callback_data="usdt")],
        ]
        await query.edit_message_text("طريقة الدفع:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "vodafone":
        update_user(user_id, {"state": "vodafone"})
        await query.edit_message_text(f"حول على:\n{VODAFONE_NUMBER}")

    elif query.data == "usdt":
        update_user(user_id, {"state": "usdt"})
        await query.edit_message_text(f"ابعت على:\n{USDT_ADDRESS}")

# ─── Messages ────────────────────
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = get_user(user_id)

    if is_spam(user_id):
        return

    if user_data.get("state") == "usdt":
        add_order({
            "user": user_id,
            "method": "usdt",
            "time": time.ctime()
        })
        await notify_admin(context, f"طلب USDT من {user_id}")
        await update.message.reply_text("تم استلام طلبك ✅")

# ─── Run ─────────────────────────
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("orders", admin_orders))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT, handle_message))

print("Running...")
app.run_polling()
