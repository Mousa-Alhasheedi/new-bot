from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, filters
import yt_dlp
import logging
import os

# إعداد السجل لعرض الأخطاء
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# معرف القناة (ضع هنا معرف القناة الخاصة بك)
CHANNEL_USERNAME = "@MediaDownloader22"

# التحقق من اشتراك المستخدم في القناة
async def check_subscription(update: Update, context: CallbackContext) -> bool:
    user_id = update.message.from_user.id
    try:
        user_status = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if user_status.status in ['member', 'administrator', 'creator']:
            return True
        else:
            return False
    except Exception as e:
        logger.error(f"Error checking subscription: {e}")
        return False

# إرسال رسالة تطلب الاشتراك
async def request_subscription(update: Update) -> None:
    await update.message.reply_text(
        f"❌ يجب الاشتراك في قناتنا أولاً لاستخدام البوت: {CHANNEL_USERNAME}\n\n"
        "🔔 بعد الاشتراك، حاول مرة أخرى."
    )

# دالة بدء البوت
async def start(update: Update, context: CallbackContext) -> None:
    logger.info("تم استقبال أمر /start")
    if not await check_subscription(update, context):
        await request_subscription(update)
        return

    await update.message.reply_text(
        "👋 مرحبًا بك في بوت تحميل الوسائط!\n\n"
        "🎥 يدعم التحميل من:\n"
        "- يوتيوب\n"
        "- إنستجرام\n"
        "- تيك توك\n"
        "- فيسبوك\n\n"
        "📩 أرسل رابط الفيديو أو الصوت لتحميله.\n"
        "📖 أرسل /help للمزيد من المعلومات."
    )

# دالة مساعدة المستخدم
async def help_command(update: Update, context: CallbackContext) -> None:
    logger.info("تم استقبال أمر /help")
    if not await check_subscription(update, context):
        await request_subscription(update)
        return

    await update.message.reply_text(
        "📚 **كيفية استخدام البوت**:\n\n"
        "1️⃣ أرسل رابطًا من المواقع التالية:\n"
        "- يوتيوب\n"
        "- إنستجرام\n"
        "- تيك توك\n"
        "- فيسبوك\n\n"
        "2️⃣ سأقوم بتحميل الوسائط وإرسالها لك مباشرةً!\n\n"
        "💡 **الأوامر المتاحة**:\n"
        "/start - بدء المحادثة\n"
        "/help - عرض المساعدة"
    )

# دالة معالجة الروابط
async def handle_link(update: Update, context: CallbackContext) -> None:
    if not await check_subscription(update, context):
        await request_subscription(update)
        return

    url = update.message.text.strip()
    logger.info(f"تم استقبال الرابط: {url}")
    await update.message.reply_text("🔄 جاري التحقق من الرابط والتحميل...")

    # التحقق من صحة الرابط
    if any(site in url for site in ['youtube.com', 'youtu.be', 'instagram.com', 'tiktok.com', 'facebook.com']):
        try:
            download_path = "downloads"
            os.makedirs(download_path, exist_ok=True)

            ydl_opts = {
                'format': 'best',
                'outtmpl': f'{download_path}/%(title)s.%(ext)s',
                'noplaylist': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)

            with open(file_path, 'rb') as file:
                await update.message.reply_document(file)
                await update.message.reply_text("✅ تم التحميل بنجاح!")

            # حذف الملف بعد الإرسال لتوفير المساحة
            os.remove(file_path)

        except Exception as e:
            logger.error(f"خطأ أثناء تحميل الوسائط: {e}")
            await update.message.reply_text("❌ حدث خطأ أثناء التحميل. تأكد من صحة الرابط أو من أن الوسائط متاحة.")
    else:
        await update.message.reply_text("⚠️ الرابط غير صالح. يرجى إرسال رابط من يوتيوب، إنستجرام، تيك توك أو فيسبوك.")

# إعداد البوت
def main():
    TOKEN = "7822645922:AAEcpF0JoN0UGSzZ-5VX8h8AI9c2HPloWQw"  # ضع توكن البوت الخاص بك هنا
    application = Application.builder().token(TOKEN).build()

    # إضافة الأوامر ومعالجات الرسائل
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

    logger.info("🤖 البوت بدأ في العمل!")
    application.run_polling()

if __name__ == '__main__':
    main()
