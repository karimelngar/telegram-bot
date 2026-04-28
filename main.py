import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

TOKEN = "8748738608:AAEdOhMQR_GVvSQm4btNDO-I1YB1WEA3GSs"
ADMIN = "@x_Jude_xx"
ADMIN_CHAT_ID = int(os.environ.get("ADMIN_CHAT_ID", "0"))
VODAFONE_NUMBER = "01036369917"
USDT_ADDRESS = "0x6b956df953f5395e14144ca4c9286f7855750d54"

# user_id -> state info
user_states = {}

PACKAGES = {
    "pkg_5": {"name": "بكدج الخمس قناوات", "sar": "50 ريال", "usdt": "15 USDT"},
    "pkg_15": {"name": "بكدج الـ15 قناة", "sar": "100 ريال", "usdt": "25 USDT"},
    "pkg_35": {
        "name": "بكدج القناوات كامل 35 قناة",
        "sar": "200 ريال",
        "usdt": "50 USDT",
    },
}

WELCOME = (
    "🔥 متوفر بكج 35 قناة\n\n"
    "صغار قطاقيط و ورعان عربي سعودي ودياثة VIP سعودي "
    "ونيك امهات واخوات محارم عربي وتجسس كاميرات مراقبة "
    "ونودز سعودي — لو تدور قناوات قوية 🔥\n\n"
    "📦 الباقات:\n"
    "• بكدج الخمس قناوات ـ 50 ريال\n"
    "• بكدج الـ15 قناة ـ 100 ريال\n"
    "• البكدج كامل 35 قناة ـ 200 ريال\n\n"
    "👇 اضغط للاشتراك"
)

WAITING_MSG = (
    "✅ تم إرسال بياناتك بنجاح!\n\n⏳ انتظر الرد من المشرف أو تواصل معه مباشرةً 👇"
)

ADMIN_KEYBOARD = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                "💬 تواصل مع المشرف", url=f"https://t.me/{ADMIN.lstrip('@')}"
            )
        ]
    ]
)


# ─── إشعار المشرف ─────────────────────────────────────────────────────────────


def esc(text: str) -> str:
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def user_tag(user) -> str:
    name = esc(f"{user.first_name or ''} {user.last_name or ''}".strip())
    username = f"@{esc(user.username)}" if user.username else f"ID: {user.id}"
    return f"{name} ({username})"


async def notify_admin(context: ContextTypes.DEFAULT_TYPE, text: str):
    if ADMIN_CHAT_ID:
        try:
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID, text=text, parse_mode="HTML"
            )
        except Exception as e:
            print(f"[notify_admin error] {e}", flush=True)


async def notify_admin_photo(
    context: ContextTypes.DEFAULT_TYPE, file_id: str, caption: str
):
    if ADMIN_CHAT_ID:
        try:
            await context.bot.send_photo(
                chat_id=ADMIN_CHAT_ID, photo=file_id, caption=caption, parse_mode="HTML"
            )
        except Exception as e:
            print(f"[notify_admin_photo error] {e}", flush=True)


# ─── /start ──────────────────────────────────────────────────────────────────


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("📺 الاشتراك", callback_data="sub")]]
    await update.message.reply_text(
        WELCOME, reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ─── /myid ───────────────────────────────────────────────────────────────────


async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    await update.message.reply_text(
        f"🆔 الـ Chat ID بتاعك:\n`{uid}`\n\n"
        "احفظه في المتغير ADMIN_CHAT_ID عشان يوصلك إشعارات البوت.",
        parse_mode="Markdown",
    )


# ─── Callback buttons ─────────────────────────────────────────────────────────


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    # ── اختيار الباقة ────────────────────────────────────────────────────────
    if data == "sub":
        keyboard = [
            [
                InlineKeyboardButton(
                    "1• بكدج الخمس قناوات ـ 50 ريال", callback_data="pkg_5"
                )
            ],
            [
                InlineKeyboardButton(
                    "2• بكدج الـ15 قناة ـ 100 ريال", callback_data="pkg_15"
                )
            ],
            [
                InlineKeyboardButton(
                    "3• بكدج القناوات كامل 35 قناة ـ 200 ريال", callback_data="pkg_35"
                )
            ],
        ]
        await query.edit_message_text(
            "📦 اختار الباقة:\n\n"
            "ملحوظة: الاشتراك دائم مع الحفظ في جميع القناوات\n"
            "اختار الباقة وسيظهر لك طرق الدفع 👇",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    # ── اختيار طريقة الدفع ────────────────────────────────────────────────────
    elif data in PACKAGES:
        pkg = PACKAGES[data]
        user_states[user_id] = {"pkg_key": data, "pkg": pkg}
        keyboard = [
            [
                InlineKeyboardButton(
                    "💳 لايك كارد سعودي", callback_data=f"pay_likecard_{data}"
                )
            ],
            [
                InlineKeyboardButton(
                    "📱 بطاقة سوا شحن STC", callback_data=f"pay_stc_{data}"
                )
            ],
            [
                InlineKeyboardButton(
                    "💚 محفظة فودافون كاش", callback_data=f"pay_vodafone_{data}"
                )
            ],
            [InlineKeyboardButton("🪙 USDT", callback_data=f"pay_usdt_{data}")],
        ]
        await query.edit_message_text(
            f"✅ اخترت: {pkg['name']} ـ {pkg['sar']}\n\n💳 اختار طريقة الدفع:",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    # ── لايك كارد ────────────────────────────────────────────────────────────
    elif data.startswith("pay_likecard_"):
        pkg_key = data.replace("pay_likecard_", "")
        pkg = PACKAGES[pkg_key]
        user_states[user_id] = {
            "pkg_key": pkg_key,
            "pkg": pkg,
            "state": "waiting_likecard_code",
        }
        await query.edit_message_text(
            f"✅ اخترت: {pkg['name']} ـ {pkg['sar']}\n"
            "💳 طريقة الدفع: لايك كارد سعودي\n\n"
            "📤 أرسل كود البطاقة الآن:"
        )

    # ── STC ──────────────────────────────────────────────────────────────────
    elif data.startswith("pay_stc_"):
        pkg_key = data.replace("pay_stc_", "")
        pkg = PACKAGES[pkg_key]
        user_states[user_id] = {
            "pkg_key": pkg_key,
            "pkg": pkg,
            "state": "waiting_stc_code",
        }
        await query.edit_message_text(
            f"✅ اخترت: {pkg['name']} ـ {pkg['sar']}\n"
            "📱 طريقة الدفع: بطاقة سوا شحن STC\n\n"
            "📤 أرسل كود البطاقة الآن:"
        )

    # ── فودافون كاش — اختيار الباقة بالجنيه ─────────────────────────────────
    elif data.startswith("pay_vodafone_"):
        keyboard = [
            [
                InlineKeyboardButton(
                    "بكدج الخمس قناوات ـ 500 جنيه", callback_data="vf_pkg_5"
                )
            ],
            [
                InlineKeyboardButton(
                    "بكدج الـ15 قناة ـ 1000 جنيه", callback_data="vf_pkg_15"
                )
            ],
            [
                InlineKeyboardButton(
                    "بكدج القناوات كامل 35 قناة ـ 1500 جنيه", callback_data="vf_pkg_35"
                )
            ],
        ]
        await query.edit_message_text(
            "💚 طريقة الدفع: محفظة فودافون كاش\n\n📦 اختار الباقة بالجنيه المصري:",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    # ── فودافون كاش — بعد اختيار الباقة ─────────────────────────────────────
    elif data.startswith("vf_pkg_"):
        pkg_key = data.replace("vf_pkg_", "pkg_")
        pkg = PACKAGES[pkg_key]
        egp_prices = {"pkg_5": "500", "pkg_15": "1000", "pkg_35": "1500"}
        egp = egp_prices[pkg_key]
        user_states[user_id] = {
            "pkg_key": pkg_key,
            "pkg": pkg,
            "state": "waiting_vodafone_screenshot",
            "egp": egp,
        }
        keyboard = [
            [
                InlineKeyboardButton(
                    "✅ تم التحويل", callback_data=f"vodafone_done_{pkg_key}"
                )
            ]
        ]
        await query.edit_message_text(
            f"✅ اخترت: {pkg['name']} ـ {egp} جنيه\n"
            "💚 طريقة الدفع: محفظة فودافون كاش\n\n"
            f"📲 رقم المحفظة للتحويل:\n`{VODAFONE_NUMBER}`\n\n"
            "بعد إتمام التحويل اضغط الزر 👇",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )

    elif data.startswith("vodafone_done_"):
        user_states[user_id]["state"] = "waiting_vodafone_screenshot"
        await query.edit_message_text("📸 أرسل سكرين شوت التحويل الآن:")

    # ── USDT ─────────────────────────────────────────────────────────────────
    elif data.startswith("pay_usdt_"):
        pkg_key = data.replace("pay_usdt_", "")
        pkg = PACKAGES[pkg_key]
        user_states[user_id] = {"pkg_key": pkg_key, "pkg": pkg, "state": "waiting_usdt"}
        keyboard = [
            [InlineKeyboardButton("✅ تم الدفع", callback_data=f"usdt_done_{pkg_key}")]
        ]
        await query.edit_message_text(
            "🪙 أسعار الباقات بالـ USDT:\n\n"
            "• بكدج الخمس قناوات ـ 15 USDT\n"
            "• بكدج الـ15 قناة ـ 25 USDT\n"
            "• بكدج القناوات كامل 35 قناة ـ 50 USDT\n\n"
            f"💰 باقتك: {pkg['name']} ـ {pkg['usdt']}\n\n"
            f"📋 عنوان الدفع (شبكة BEP-20):\n`{USDT_ADDRESS}`\n\n"
            "بعد إتمام الدفع اضغط الزر 👇",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )

    elif data.startswith("usdt_done_"):
        pkg_key = data.replace("usdt_done_", "")
        pkg = PACKAGES.get(pkg_key, {})
        user = query.from_user
        await notify_admin(
            context,
            f"🪙 دفع USDT جديد!\n\n"
            f"👤 العميل: {user_tag(user)}\n"
            f"📦 الباقة: {esc(pkg.get('name', '؟'))} ـ {esc(pkg.get('usdt', '؟'))}\n"
            f"🔗 عنوان الدفع: <code>{esc(USDT_ADDRESS)}</code>\n\n"
            f"⚠️ يرجى التحقق من الدفع ثم تفعيل الاشتراك.",
        )
        await query.edit_message_text(WAITING_MSG, reply_markup=ADMIN_KEYBOARD)
        user_states.pop(user_id, None)


# ─── رسائل نصية وصور ─────────────────────────────────────────────────────────


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state_data = user_states.get(user_id, {})
    state = state_data.get("state")
    user = update.effective_user

    # كود لايك كارد — 16 خانة أرقام وحروف
    if state == "waiting_likecard_code":
        code = update.message.text.strip()
        if len(code) != 16 or not code.isalnum():
            await update.message.reply_text(
                "❌ الكود غلط!\n\n"
                "كود اللايك كارد لازم يكون مكوّن من 16 خانة (أرقام وحروف).\n"
                "📤 أرسل الكود الصحيح:"
            )
            return
        pkg = state_data["pkg"]
        await notify_admin(
            context,
            f"💳 كود لايك كارد جديد!\n\n"
            f"👤 العميل: {user_tag(user)}\n"
            f"📦 الباقة: {esc(pkg['name'])} ـ {esc(pkg['sar'])}\n"
            f"🔑 الكود: <code>{esc(code)}</code>",
        )
        await update.message.reply_text(WAITING_MSG, reply_markup=ADMIN_KEYBOARD)
        user_states.pop(user_id, None)

    # كود STC — 14 رقم فقط
    elif state == "waiting_stc_code":
        code = update.message.text.strip()
        if len(code) != 14 or not code.isdigit():
            await update.message.reply_text(
                "❌ الكود غلط!\n\n"
                "كود سوا لازم يكون مكوّن من 14 رقم فقط.\n"
                "📤 أرسل الكود الصحيح:"
            )
            return
        pkg = state_data["pkg"]
        await notify_admin(
            context,
            f"📱 كود STC جديد!\n\n"
            f"👤 العميل: {user_tag(user)}\n"
            f"📦 الباقة: {esc(pkg['name'])} ـ {esc(pkg['sar'])}\n"
            f"🔑 الكود: <code>{esc(code)}</code>",
        )
        await update.message.reply_text(WAITING_MSG, reply_markup=ADMIN_KEYBOARD)
        user_states.pop(user_id, None)

    # بيانات فودافون بعد الاسكرين شوت
    elif state == "waiting_vodafone_code":
        info = update.message.text.strip()
        pkg = state_data.get("pkg", {})
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
