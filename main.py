await notify_admin(
            context,
            f"🪙 USDT\n\n👤 {user_tag(user)}\n📦 {pkg['name']}"
        )

        await update.message.reply_text(WAITING_MSG)
        user_states.pop(user_id, None)

    else:
        await update.message.reply_text("اضغط /start")

# ─── PHOTO ───────────────────────────
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = update.effective_user
    state_data = user_states.get(user_id, {})
    state = state_data.get("state")

    if state == "waiting_vodafone_screenshot":
        pkg = state_data["pkg"]
        photo = update.message.photo[-1]

        await notify_admin_photo(
            context,
            photo.file_id,
            f"💚 فودافون\n\n👤 {user_tag(user)}\n📦 {pkg['name']}"
        )

        await update.message.reply_text(WAITING_MSG)
        user_states.pop(user_id, None)

# ─── RUN ─────────────────────────────
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT, handle_message))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

print("Bot is running...")
app.run_polling()
