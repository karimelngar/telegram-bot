egp = state_data.get("egp", "؟")
        await notify_admin(
            context,
            f"💚 تحويل فودافون كاش جديد!\n\n"
            f"👤 العميل: {user_tag(user)}\n"
            f"📦 الباقة: {esc(pkg.get('name', '؟'))} ـ {esc(egp)} جنيه\n"
            f"📝 البيانات: {esc(info)}\n\n"
            f"⚠️ راجع السكرين شوت أعلاه ثم فعّل الاشتراك.",
        )
        await update.message.reply_text(WAITING_MSG, reply_markup=ADMIN_KEYBOARD)
        user_states.pop(user_id, None)

    else:
        keyboard = [[InlineKeyboardButton("📺 الاشتراك", callback_data="sub")]]
        await update.message.reply_text(
            WELCOME, reply_markup=InlineKeyboardMarkup(keyboard)
        )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state_data = user_states.get(user_id, {})
    state = state_data.get("state")
    user = update.effective_user

    # صورة فودافون كاش — أكبر جودة متاحة
    if state == "waiting_vodafone_screenshot":
        pkg = state_data.get("pkg", {})
        egp = state_data.get("egp", "؟")
        photo = update.message.photo[-1]
        # أرسل السكرين للمشرف
        await notify_admin_photo(
            context,
            photo.file_id,
            f"💚 سكرين شوت تحويل فودافون كاش\n"
            f"👤 العميل: {user_tag(user)}\n"
            f"📦 الباقة: {esc(pkg.get('name', '؟'))} ـ {esc(egp)} جنيه",
        )
        user_states[user_id]["state"] = "waiting_vodafone_code"
        await update.message.reply_text(
            "✅ تم استلام سكرين شوت التحويل\n\n"
            "📤 الآن أرسل اسمك ورقم تليفونك لإتمام الاشتراك:"
        )
    else:
        keyboard = [[InlineKeyboardButton("📺 الاشتراك", callback_data="sub")]]
        await update.message.reply_text(
            WELCOME, reply_markup=InlineKeyboardMarkup(keyboard)
        )


# ─── تشغيل البوت ─────────────────────────────────────────────────────────────

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("myid", myid))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()
