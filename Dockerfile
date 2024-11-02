# مرحله اول: انتخاب ایمیج پایه
FROM python:3.9-slim

# مرحله دوم: تنظیم دایرکتوری کاری در کانتینر
WORKDIR /app

# مرحله سوم: کپی کردن فایل‌های مورد نیاز به کانتینر
COPY . /app

# مرحله چهارم: نصب وابستگی‌ها
RUN pip install --no-cache-dir -r requirements.txt

# مرحله پنجم: تعریف متغیر محیطی برای توکن تلگرام
# این متغیر را می‌توانید در Railway تنظیم کنید.
ENV TELEGRAM_TOKEN=${TELEGRAM_TOKEN}

# مرحله ششم: تعیین دستور پیش‌فرض برای اجرا
CMD ["python", "bot.py"]
