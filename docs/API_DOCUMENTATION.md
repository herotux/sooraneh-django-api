# 📚 مستندات API Sooraneh

## 🔐 احراز هویت
- `POST /api/auth/register/` — ثبت‌نام
- `POST /api/auth/login/` — ورود و دریافت توکن JWT

## 🧾 مالی
- `GET/POST /api/v1/persons/`
- `GET/POST /api/v1/incomes/` (اضافه شدن فیلد کیف پول)
- `GET/POST /api/v1/expenses/` (اضافه شدن فیلدهای کیف پول و تصویر رسید - برای جزئیات به Swagger مراجعه کنید)
- `GET/POST /api/v1/wallets/` (جدید)
- `GET/POST /api/v1/installments/`
- `GET/POST /api/v1/debts/`
- `GET/POST /api/v1/credits/`

## 👤 پروفایل و کاربران (جدید)
- `GET/PATCH /api/v1/users/me/` — مشاهده و ویرایش پروفایل کاربری (شامل تصویر پروفایل)
- توجه: مدل `Person` نیز اکنون دارای فیلد تصویر پروفایل است.

## 📝 لیست‌ها (جدید)
- `GET /api/v1/todolists/` — مدیریت لیست‌های کارها (برای دیدن آرشیو شده‌ها: `?archived=true`)
- `POST /api/v1/todolists/` — ایجاد لیست کار جدید
- `POST /api/v1/todolists/{id}/share/` — اشتراک‌گذاری لیست با یک کاربر (body: `{"user_id": id}`)
- `POST /api/v1/todolists/{id}/archive/` — آرشیو/لغو آرشیو لیست
- `GET/POST /api/v1/todolists/{id}/items/` — مدیریت آیتم‌های یک لیست کار
- `GET /api/v1/shoppinglists/` — مدیریت لیست‌های خرید (برای دیدن آرشیو شده‌ها: `?archived=true`)
- `POST /api/v1/shoppinglists/` — ایجاد لیست خرید جدید
- `POST /api/v1/shoppinglists/{id}/share/` — اشتراک‌گذاری لیست با یک کاربر (body: `{"user_id": id}`)
- `POST /api/v1/shoppinglists/{id}/archive/` — آرشیو/لغو آرشیو لیست
- `GET/POST /api/v1/shoppinglists/{id}/items/` — مدیریت آیتم‌های یک لیست خرید

## 💬 اجتماعی (جدید)
- `GET /api/v1/friends/` — لیست دوستان
- `GET /api/v1/friends/pending/` — لیست درخواست‌های دوستی در انتظار
- `POST /api/v1/friends/send-request/` — ارسال درخواست دوستی (body: `{"user_id": id}`)
- `POST /api/v1/friends/{id}/accept/` — پذیرش درخواست دوستی
- `POST /api/v1/friends/{id}/reject/` — رد درخواست دوستی
- `POST /api/v1/friends/{user_id}/unfriend/` — حذف دوست
- `GET /api/v1/messages/inbox/` — لیست گفتگوها
- `GET /api/v1/messages/{user_id}/history/` — مشاهده تاریخچه پیام با یک کاربر
- `POST /api/v1/messages/` — ارسال پیام (body: `{"recipient_id": id, "content": "..."}`)

## 👥 گروه‌ها (دونگی) (جدید)
- `GET/POST /api/v1/groups/` — مشاهده و ایجاد گروه‌ها
- `POST /api/v1/groups/{id}/add-member/` — افزودن عضو به گروه (body: `{"user_id": id}`)
- `POST /api/v1/groups/{id}/remove-member/` — حذف عضو از گروه (body: `{"user_id": id}`)
- `GET/POST /api/v1/groups/{id}/expenses/` — مشاهده و ثبت هزینه در گروه
- `GET /api/v1/groups/{id}/summary/` — مشاهده خلاصه وضعیت مالی و تسویه حساب‌های پیشنهادی

## 🏢 مدیریت ساختمان (جدید)
- `GET/POST /api/v1/buildings/` — مشاهده و ایجاد ساختمان‌ها
- `GET/POST /api/v1/buildings/{id}/units/` — مدیریت واحدهای یک ساختمان
- `POST /api/v1/buildings/{id}/units/{id}/fees/` — ثبت شارژ برای یک واحد
- `POST /api/v1/buildings/{id}/units/{id}/fees/{id}/pay/` — پرداخت شارژ یک واحد
- `GET/POST /api/v1/buildings/{id}/expenses/` — مشاهده و ثبت هزینه‌های ساختمان
- `GET /api/v1/buildings/{id}/summary/` — مشاهده خلاصه وضعیت مالی ساختمان

## 🎯 چالش‌ها (جدید)
- `GET/POST /api/v1/challenges/` — مشاهده و ایجاد چالش‌ها
- `GET /api/v1/challenges/{id}/` — مشاهده جزئیات و پیشرفت چالش
- `POST /api/v1/challenges/{id}/invite/` — دعوت یک دوست به چالش (body: `{"user_id": id}`)

## 💰 صندوق خانوادگی (جدید)
- `GET/POST /api/v1/funds/` — مشاهده و ایجاد صندوق‌ها
- `POST /api/v1/funds/{id}/invite/` — دعوت عضو جدید به صندوق
- `POST /api/v1/funds/{id}/contribute/` — ثبت پرداخت سهم ماهانه
- `POST /api/v1/funds/{id}/log-payout/` — ثبت دریافت‌کننده قرعه ماه (توسط مدیر)

## 💳 اشتراک و پرداخت (جدید)
- `POST /api/v1/subscriptions/request-payment/` — شروع فرآیند پرداخت برای یک پلن از طریق زرین‌پال (body: `{"plan_id": id}`)
- `GET /api/v1/subscriptions/verify-payment/` — نقطه بازگشت از درگاه پرداخت برای تأیید نهایی
- **توجه**: برای پرداخت آفلاین (کارت به کارت)، مدیر سیستم می‌تواند از طریق پنل ادمین جنگو، اشتراک کاربر را به صورت دستی ایجاد یا تمدید کند.

## 📊 Swagger
- `http://localhost:8000/swagger/`
- `http://localhost:8000/redoc/`

## 🔑 دسترسی
همه APIها نیاز به `Authorization: Bearer <token>` دارند.
