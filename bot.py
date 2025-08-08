import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# توکن را از متغیر محیطی می‌گیریم (از Render یا هر سرویس دیگری تنظیم خواهی کرد)
TOKEN = os.getenv("BOT_TOKEN")

# فایل محلی برای نگهداری لیست ادمین‌ها
ADMIN_FILE = "admins.txt"

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

def load_admins():
    if not os.path.exists(ADMIN_FILE):
        # اگر فایل نیست، بساز و ادمین اولیه رو هم بذار (اسم بدون @)
        with open(ADMIN_FILE, "w", encoding="utf-8") as f:
            f.write("M_Rez_AZ\n")
    with open(ADMIN_FILE, "r", encoding="utf-8") as f:
        admins = [line.strip() for line in f if line.strip()]
    return admins

def save_admins(admins):
    with open(ADMIN_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(admins) + ("\n" if admins else ""))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username or ""
    admins = load_admins()
    if username in admins:
        await update.message.reply_text(f"👋 سلام {update.effective_user.first_name}!\nشما ادمین هستید — خوش آمدی به دستیار Beton Baz.")
    else:
        await update.message.reply_text(
            "سلام! برای دسترسی ادمینی باید توسط یکی از ادمین‌های فعلی تایید بشی.\n"
            "لطفاً از یکی از ادمین‌ها بخواهید در این ربات دستور زیر را بزند:\n"
            "`/approve YOUR_USERNAME` (مثال: /approve M_Rez_AZ)\n\n"
            "بعد از تایید، دسترسی بهت داده میشه."
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username or ""
    admins = load_admins()
    if username in admins:
        await update.message.reply_text(
            "دستورات:\n"
            "/start - شروع\n"
            "/help - این راهنما\n"
            "/approve <username> - (برای ادمین‌ها) اضافه کردن یوزرنیم به لیست ادمین‌ها\n"
            "/idea - پیشنهاد ایده ویدیویی (نمونه)\n"
            "/tags <موضوع> - تولید هشتگ‌های پیشنهادی\n"
        )
    else:
        await update.message.reply_text("🚫 شما دسترسی ادمین ندارید. از ادمین‌ها درخواست تایید بده.")

async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    actor = update.effective_user.username or ""
    admins = load_admins()
    if actor not in admins:
        await update.message.reply_text("🚫 فقط ادمین‌ها می‌توانند کاربر جدید را تایید کنند.")
        return
    if not context.args:
        await update.message.reply_text("❌ لطفاً یوزرنیم را وارد کن. مثال: /approve M_Rez_AZ")
        return
    new_user = context.args[0].lstrip("@")
    if new_user in admins:
        await update.message.reply_text(f"⚠️ @{new_user} قبلاً ادمین هست.")
        return
    admins.append(new_user)
    save_admins(admins)
    await update.message.reply_text(f"✅ @{new_user} به لیست ادمین‌ها اضافه شد.")

async def idea(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username or ""
    admins = load_admins()
    if username not in admins:
        await update.message.reply_text("🚫 فقط ادمین‌ها می‌توانند این دستور را اجرا کنند.")
        return
    await update.message.reply_text("💡 ایده ویدیو: «۵ اشتباه رایج در بتن‌ریزی که باعث کاهش مقاومت می‌شود»")

async def tags(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username or ""
    admins = load_admins()
    if username not in admins:
        await update.message.reply_text("🚫 فقط ادمین‌ها می‌توانند این دستور را اجرا کنند.")
        return
    if not context.args:
        await update.message.reply_text("❌ لطفاً موضوع را وارد کنید. مثال: /tags بتن ضدآب")
        return
    topic = " ".join(context.args)
    tags_list = f"#{topic.replace(' ', '')} #بتن #Concrete #CivilEngineering"
    await update.message.reply_text(f"🏷️ هشتگ‌های پیشنهادی:\n{tags_list}")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username or ""
    admins = load_admins()
    if username not in admins:
        await update.message.reply_text("🚫 دسترسی ندارید.")
        return
    # پیام‌های متنی ادمین‌ها رو برمی‌گردونه (می‌تونی اینجا تحلیل بذاری)
    await update.message.reply_text(f"پیامت دریافت شد:\n{update.message.text}")

def main():
    if not TOKEN:
        print("ERROR: BOT_TOKEN environment variable not set.")
        return
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("approve", approve))
    app.add_handler(CommandHandler("idea", idea))
    app.add_handler(CommandHandler("tags", tags))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
