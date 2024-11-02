from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import re


# کلاس مسابقه و پیش‌بینی
class Match:
    def __init__(self, home_team, away_team, home_goals, away_goals):
        self.home_team = home_team
        self.away_team = away_team
        self.home_goals = home_goals
        self.away_goals = away_goals


class Prediction:
    def __init__(self, home_team, away_team, home_goals, away_goals, double=False):
        self.home_team = home_team
        self.away_team = away_team
        self.home_goals = home_goals
        self.away_goals = away_goals
        self.double = double


# متغیرهای سراسری برای ذخیره مسابقات و پیش‌بینی‌ها
actual_matches = []
predictions = []


# هندلر برای شروع ربات و نمایش دکمه‌ها
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("ارسال نتایج واقعی", callback_data='request_actual')],
        [InlineKeyboardButton("ارسال پیش‌بینی", callback_data='request_prediction')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("یکی از گزینه‌ها را انتخاب کنید:", reply_markup=reply_markup)


# هندلر برای کلیک روی دکمه‌ها
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'request_actual':
        await query.message.reply_text("لطفاً نتایج واقعی مسابقات را به فرمت 'تیم1 2 - 1 تیم2' ارسال کنید.")
    elif query.data == 'request_prediction':
        await query.message.reply_text("لطفاً پیش‌بینی خود را به فرمت 'تیم1 2 - 1 تیم2' ارسال کنید.")


# تابعی برای پردازش متن مسابقات
def parse_matches(text):
    matches = []
    lines = text.strip().split('\n')
    for line in lines:
        match = re.match(r'(.+?)\s+(\d+)\s*-\s*(\d+)\s+(.+)', line)
        if match:
            home_team, home_goals, away_goals, away_team = match.groups()
            matches.append(Match(home_team.strip(), away_team.strip(), int(home_goals), int(away_goals)))
    return matches


# هندلر برای دریافت نتایج واقعی
async def handle_actual_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global actual_matches
    actual_matches = parse_matches(update.message.text)
    await update.message.reply_text("نتایج واقعی ثبت شد. اکنون می‌توانید پیش‌بینی خود را ارسال کنید.")


# هندلر برای دریافت پیش‌بینی‌ها و محاسبه امتیاز
async def handle_prediction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global predictions, actual_matches

    # تبدیل متن به لیست پیش‌بینی‌ها
    predictions = parse_matches(update.message.text)

    # محاسبه امتیاز کل
    total_score = 0
    for prediction in predictions:
        for actual_match in actual_matches:
            if prediction.home_team == actual_match.home_team and prediction.away_team == actual_match.away_team:
                if (prediction.home_goals == actual_match.home_goals and
                        prediction.away_goals == actual_match.away_goals):
                    score = 10
                elif (actual_match.home_goals - actual_match.away_goals ==
                      prediction.home_goals - prediction.away_goals):
                    score = 5
                elif (actual_match.home_goals > actual_match.away_goals and
                      prediction.home_goals > prediction.away_goals) or \
                        (actual_match.home_goals < actual_match.away_goals and
                         prediction.home_goals < prediction.away_goals):
                    score = 2
                elif actual_match.home_goals == actual_match.away_goals and \
                        prediction.home_goals == prediction.away_goals:
                    score = 5
                else:
                    score = 0

                # چک کردن دو برابر شدن امتیاز
                if prediction.double:
                    score *= 2

                total_score += score
                break

    # ارسال امتیاز کل
    await update.message.reply_text(f"امتیاز شما: {total_score}")

    # بازگرداندن دکمه‌ی "ارسال پیش‌بینی"
    keyboard = [
        [InlineKeyboardButton("ارسال پیش‌بینی", callback_data='request_prediction')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("برای ارسال پیش‌بینی جدید دکمه زیر را فشار دهید:", reply_markup=reply_markup)


# تابع اصلی برای راه‌اندازی ربات
def main():
    application = Application.builder().token("YOUR_TELEGRAM_BOT_TOKEN").build()

    # افزودن هندلرها
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_actual_results))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_prediction))

    # شروع ربات
    application.run_polling()


if __name__ == "__main__":
    main()
