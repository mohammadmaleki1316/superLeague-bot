from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext, \
    CallbackQueryHandler
import re


# کلاس های مسابقه و پیش بینی
class Match:
    def __init__(self, host_team, guest_team, host_score, guest_score):
        self.host_team = host_team
        self.guest_team = guest_team
        self.host_score = host_score
        self.guest_score = guest_score


class Prediction(Match):
    def __init__(self, host_team, guest_team, host_score, guest_score, multiplier):
        super().__init__(host_team, guest_team, host_score, guest_score)
        self.multiplier = multiplier


# توابع کمکی برای تجزیه و تحلیل متن
def parse_text_to_matches(text, is_prediction=False):
    lines = text.strip().splitlines()
    matches = []
    for line in lines:
        parts = re.match(r"(.+?)\s+(\d+)\s*-\s*(\d+)\s+(.+?)(\sx2)?$", line)
        if parts:
            host_team = parts.group(1).strip()
            guest_team = parts.group(4).strip()
            host_score = int(parts.group(2))
            guest_score = int(parts.group(3))
            multiplier = 2 if parts.group(5) and is_prediction else 1
            if is_prediction:
                matches.append(Prediction(host_team, guest_team, host_score, guest_score, multiplier))
            else:
                matches.append(Match(host_team, guest_team, host_score, guest_score))
    return matches


# تابع محاسبه امتیاز
def calculate_score(real_matches, predictions):
    score = 0
    for prediction in predictions:
        for match in real_matches:
            if prediction.host_team == match.host_team and prediction.guest_team == match.guest_team:
                if prediction.host_score == match.host_score and prediction.guest_score == match.guest_score:
                    score += 10 * prediction.multiplier
                elif (prediction.host_score - prediction.guest_score) == (match.host_score - match.guest_score):
                    score += 5 * prediction.multiplier
                elif ((prediction.host_score > prediction.guest_score) and (match.host_score > match.guest_score)) or \
                        ((prediction.host_score < prediction.guest_score) and (match.host_score < match.guest_score)):
                    score += 2 * prediction.multiplier
                elif prediction.host_score == prediction.guest_score and match.host_score == match.guest_score:
                    score += 5 * prediction.multiplier
    return score


# متغیرهای وضعیت
real_matches = []
predictions = []
is_receiving_results = False
is_receiving_predictions = False


# تابع برای نمایش دکمه‌های اصلی
def show_main_buttons():
    keyboard = [
        [InlineKeyboardButton("نتایج دقیق", callback_data="send_results")],
        [InlineKeyboardButton("پیش‌بینی", callback_data="send_predictions")],
        [InlineKeyboardButton("شروع", callback_data="start")]
    ]
    return InlineKeyboardMarkup(keyboard)


# هندلر شروع
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("لطفاً یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=show_main_buttons())


# هندلر برای دریافت نوع ورودی از طریق دکمه‌ها
async def button_handler(update: Update, context: CallbackContext) -> None:
    global is_receiving_results, is_receiving_predictions, real_matches, predictions

    query = update.callback_query
    await query.answer()

    if query.data == "send_results":
        is_receiving_results = True
        is_receiving_predictions = False
        real_matches = []  # پاک کردن نتایج قبلی
        await query.edit_message_text("نتایج واقعی مسابقات را ارسال کنید:", reply_markup=show_main_buttons())

    elif query.data == "send_predictions":
        is_receiving_results = False
        is_receiving_predictions = True
        predictions = []  # پاک کردن پیش‌بینی‌های قبلی
        await query.edit_message_text("پیش‌بینی‌های خود را ارسال کنید:", reply_markup=show_main_buttons())

    elif query.data == "start":
        is_receiving_results = False
        is_receiving_predictions = False
        await query.edit_message_text("ربات شروع به کار کرد.", reply_markup=show_main_buttons())


# هندلر برای پردازش پیام‌های متنی کاربر
async def text_handler(update: Update, context: CallbackContext) -> None:
    global is_receiving_results, is_receiving_predictions, real_matches, predictions

    text = update.message.text

    if is_receiving_results:
        real_matches = parse_text_to_matches(text)
        is_receiving_results = False  # پایان حالت دریافت نتایج
        await update.message.reply_text("نتایج واقعی ثبت شد.", reply_markup=show_main_buttons())

    elif is_receiving_predictions:
        predictions = parse_text_to_matches(text, is_prediction=True)
        is_receiving_predictions = False  # پایان حالت دریافت پیش‌بینی
        score = calculate_score(real_matches, predictions)
        await update.message.reply_text(f"پیش‌بینی شما ثبت شد و امتیاز شما: {score}", reply_markup=show_main_buttons())


# تنظیمات اصلی و راه‌اندازی ربات
def main():
    application = ApplicationBuilder().token("8044636479:AAHxFg13xM8uRb24Ds7wKvi9C3A82LUGNC4").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    application.run_polling()


if __name__ == "__main__":
    main()
