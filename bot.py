import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# کلاس ها و توابع مربوط به مسابقات
class Match:
    def __init__(self, home_team, away_team, home_score, away_score):
        self.home_team = home_team
        self.away_team = away_team
        self.home_score = home_score
        self.away_score = away_score

    def is_draw(self):
        return self.home_score == self.away_score

    def winner(self):
        if self.home_score > self.away_score:
            return "home"
        elif self.away_score > self.home_score:
            return "away"
        else:
            return "draw"

class Prediction(Match):
    def __init__(self, home_team, away_team, home_score, away_score, multiplier=1):
        super().__init__(home_team, away_team, home_score, away_score)
        self.multiplier = multiplier

def parse_matches(text, prediction_mode=False):
    matches = []
    for line in text.strip().split("\n"):
        multiplier = 2 if "x2" in line else 1
        line = line.replace(" x2", "")
        match_data = re.match(r"(.+?) (\d+) - (\d+) (.+)", line)
        if match_data:
            home_team = match_data.group(1).strip()
            home_score = int(match_data.group(2))
            away_score = int(match_data.group(3))
            away_team = match_data.group(4).strip()
            if prediction_mode:
                matches.append(Prediction(home_team, away_team, home_score, away_score, multiplier))
            else:
                matches.append(Match(home_team, away_team, home_score, away_score))
    return matches

def calculate_score(matches, predictions):
    total_score = 0
    for match, prediction in zip(matches, predictions):
        score = 0
        if (match.home_score == prediction.home_score and match.away_score == prediction.away_score):
            score = 10
        elif (match.winner() == prediction.winner() and abs(match.home_score - match.away_score) == abs(prediction.home_score - prediction.away_score)):
            score = 5
        elif match.winner() == prediction.winner():
            score = 2
        elif match.is_draw() and prediction.is_draw():
            score = 5
        score *= prediction.multiplier
        total_score += score
    return total_score

# متغیرهای سراسری برای ذخیره‌ی مسابقات و پیش‌بینی‌ها
real_matches = []
predictions = []

# شروع ربات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("ارسال نتایج واقعی", callback_data="real_results")],
        [InlineKeyboardButton("ارسال پیش‌بینی‌ها", callback_data="predictions")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("یک گزینه را انتخاب کنید:", reply_markup=reply_markup)

# هندلر کلیدها
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "real_results":
        await query.message.reply_text("نتایج واقعی مسابقات را ارسال کنید:")
        context.user_data["mode"] = "real_results"
    elif query.data == "predictions":
        await query.message.reply_text("پیش‌بینی خود را ارسال کنید:")
        context.user_data["mode"] = "predictions"

# دریافت پیام‌های کاربر و تشخیص نتایج و پیش‌بینی‌ها
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global real_matches, predictions
    text = update.message.text
    mode = context.user_data.get("mode")
    if mode == "real_results":
        real_matches = parse_matches(text)
        predictions = []  # پاک‌سازی پیش‌بینی‌ها
        await update.message.reply_text("نتایج واقعی ثبت شد.")
    elif mode == "predictions":
        if real_matches:
            user_predictions = parse_matches(text, prediction_mode=True)
            score = calculate_score(real_matches, user_predictions)
            predictions = user_predictions  # ثبت پیش‌بینی جدید
            await update.message.reply_text(f"پیش‌بینی ثبت شد. امتیاز: {score}")
        else:
            await update.message.reply_text("لطفا اول نتایج واقعی را وارد کنید.")

# تنظیم ربات و ثبت هندلرها
def main():
    TOKEN = "8044636479:AAHxFg13xM8uRb24Ds7wKvi9C3A82LUGNC4"  # اینجا توکن ربات خود را وارد کنید
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == "__main__":
    main()
