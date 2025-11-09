import telebot
from telebot import types
import sqlite3
import datetime
import re
import json

# ====== تنظیم توکن اینجا ======
TOKEN = "8585854031:AAGytcSRlo_BP_mRigVMvLGLu20jwvbLNhU"
bot = telebot.Telebot = telebot.TeleBot(TOKEN)

# ====== راه‌اندازی دیتابیس ======
DB = "tasks.db"

def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER,
        user_id INTEGER,
        username TEXT,
        date TEXT,         -- YYYY-MM-DD
        task TEXT,
        done INTEGER DEFAULT 0,
        created_at TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

# ====== کمکی: تبدیل "18 آبان" یا "18/8" به YYYY-MM-DD ======
persian_months = {
    "فروردین":1, "اردیبهشت":2, "خرداد":3, "تیر":4, "مرداد":5, "شهریور":6,
    "مهر":7, "آبان":8, "آذر":9, "دی":10, "بهمن":11, "اسفند":12
}
# تابعی که ورودی کاربر رو به تاریخ تبدیل می‌کنه (سال جاری)
def parse_date_text(text):
    text = text.strip()
    # تلاش برای فرمت عدد/عدد مثل 18/8 یا 18-8
    m = re.match(r"^(\d{1,2})[\/\-\s](\d{1,2})$", text)
    if m:
        day = int(m.group(1)); month = int(m.group(2))
    else:
        # تلاش برای "18 آبان" یا "18آبان"
        m2 = re.match(r"^(\d{1,2})\s*(\S+)$", text)
        if m2:
            day = int(m2.group(1))
            month_text = m2.group(2)
            # احتمالا ماه فارسی است
            month = persian_months.get(month_text, None)
            if month is None:
                # اگر نتونستیم، سعی کن عدد بگیریم
                try:
                    month = int(month_text)
                except:
                    return None
        else:
            return None
    # ساخت تاریخ با سال جاری
    year = datetime.date.today().year
    try:
        dt = datetime.date(year, month, day)
    except Exception:
        return None
    return dt.isoformat()  # YYYY-MM-DD

# ====== ذخیره تسک‌ها ======
def add_tasks(chat_id, user_id, username, date_iso, tasks_list):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    now = datetime.datetime.now().isoformat()
    for t in tasks_list:
        cur.execute("INSERT INTO tasks (chat_id, user_id, username, date, task, created_at) VALUES (?,?,?,?,?,?)",
                    (chat_id, user_id, username, date_iso, t.strip(), now))
    conn.commit()
    conn.close()

def get_tasks_for_chat_date(chat_id, date_iso):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT id,task,done FROM tasks WHERE chat_id=? AND date=? ORDER BY id", (chat_id, date_iso))
    rows = cur.fetchall()
    conn.close()
    return rows

def toggle_task_done(task_id):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT done FROM tasks WHERE id=?", (task_id,))
    r = cur.fetchone()
    if not r:
        conn.close()
        return None
    new = 0 if r[0] else 1
    cur.execute("UPDATE tasks SET done=? WHERE id=?", (new, task_id))
    conn.commit()
    conn.close()
    return new

# ====== نمایش لیست و ساخت کیبورد ======
def build_tasks_message_and_keyboard(chat_id, date_iso):
    rows = get_tasks_for_chat_date(chat_id, date_iso)
    if not rows:
        text = f"هیچ تسکی برای {date_iso} ثبت نشده."
        return text, None
    lines = []
    keyboard = types.InlineKeyboardMarkup()
    for r in rows:
        tid, task_text, done = r
        # نشان دادن تیک و متن (HTML)
        mark = "✅" if done else "▫️"
        # خطای احتمالی: برای HTML باید از escaping ساده استفاده کنیم
        safe_task = task_text.replace("<","&lt;").replace(">","&gt;")
        lines.append(f"{mark} {safe_task}")
        # هر دکمه برای هر تسک => دیتا toggle:ID
        btn = types.InlineKeyboardButton(
            text=("✅ پاک/برگرد" if done else "تکمیل شد ✓"),
            callback_data=f"toggle:{tid}"
        )
        keyboard.add(btn)
    msg_text = f"تسک‌های ثبت‌شده برای <b>{date_iso}</b>:\n\n" + "\n".join(lines)
    return msg_text, keyboard

# ====== Conversation ساده با دستورات ======
# کاربر در گروه یا خصوصی می‌تواند /add را بفرستد تا ثبت تاریخ و تسک‌ها شروع شود.
user_state = {}  # نگه‌داری موقت وضعیت برای هر user_id : {"step":..., "chat_id":..., "date":...}

@bot.message_handler(commands=['start','help'])
def send_welcome(message):
    bot.reply_to(message,
                 "سلام! من ربات TODO هستم.\n\nدستورها:\n/add - اضافه کردن تسک برای یک تاریخ\n/show YYYY-MM-DD - نمایش تسک‌های آن تاریخ\n\nمثال برای اضافه کردن: بزن /add و بعد راهنمایی‌ها رو دنبال کن.")

@bot.message_handler(commands=['add'])
def cmd_add(message):
    uid = message.from_user.id
    chat_id = message.chat.id
    user_state[uid] = {"step":"await_date", "chat_id":chat_id}
    bot.reply_to(message, "تاریخ رو وارد کن (مثال: `18/8` یا `18 آبان`). سال جاری در نظر گرفته میشه.", parse_mode='Markdown')

@bot.message_handler(func=lambda m: user_state.get(m.from_user.id,{}).get("step") == "await_date")
def handle_date(message):
    uid = message.from_user.id
    st = user_state.get(uid)
    if not st: return
    dt_iso = parse_date_text(message.text)
    if not dt_iso:
        bot.reply_to(message, "فرمت تاریخ رو درست وارد کن. مثلا: `18/8` یا `18 آبان`", parse_mode='Markdown')
        return
    st["date"] = dt_iso
    st["step"] = "await_tasks"
    bot.reply_to(message, "حالا لیست تسک‌ها رو با `-` یا `;` یا هر خط جدید جدا وارد کن.\nمثال: `php - باشگاه - دانشگاه - خوندن کتاب`")

@bot.message_handler(func=lambda m: user_state.get(m.from_user.id,{}).get("step") == "await_tasks")
def handle_tasks(message):
    uid = message.from_user.id
    st = user_state.get(uid)
    if not st: return
    chat_id = st["chat_id"]
    date_iso = st["date"]
    # جداسازی تسک‌ها
    parts = re.split(r"\s*[-;]\s*|\n+", message.text)
    tasks = [p.strip() for p in parts if p.strip()]
    if not tasks:
        bot.reply_to(message, "تسکی پیدا نشد. لطفا دوباره وارد کن.")
        return
    add_tasks(chat_id=chat_id, user_id=uid, username=message.from_user.username or message.from_user.first_name,
              date_iso=date_iso, tasks_list=tasks)
    # پاک کردن وضعیت
    user_state.pop(uid, None)
    # ارسال پیام در همان چت (گروه یا خصوصی) با کیبورد
    text, keyboard = build_tasks_message_and_keyboard(chat_id, date_iso)
    if keyboard:
        bot.send_message(chat_id, text, reply_markup=keyboard, parse_mode='HTML')
    else:
        bot.send_message(chat_id, text)

@bot.message_handler(commands=['show'])
def cmd_show(message):
    # فرمت: /show 2025-11-10 یا /show 18/8
    args = message.text.split(maxsplit=1)
    chat_id = message.chat.id
    if len(args) == 1:
        bot.reply_to(message, "فرمت: /show YYYY-MM-DD یا /show 18/8 یا /show 18 آبان")
        return
    date_text = args[1].strip()
    dt_iso = parse_date_text(date_text) or date_text  # اگر کاربر YYYY-MM-DD فرستاد قبول کن
    # اگر parse نشد ولی فرمت YYYY-MM-DD باشه اجازه بده
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", dt_iso):
        bot.reply_to(message, "فرمت تاریخ معتبر نیست. مثال: /show 2025-11-09 یا /show 18/8")
        return
    text, keyboard = build_tasks_message_and_keyboard(chat_id, dt_iso)
    if keyboard:
        bot.send_message(chat_id, text, reply_markup=keyboard, parse_mode='HTML')
    else:
        bot.send_message(chat_id, text)

# ====== واکنش به دکمه‌ها (تغییر وضعیت تسک) ======
@bot.callback_query_handler(func=lambda call: call.data and call.data.startswith("toggle:"))
def callback_toggle(call):
    data = call.data.split(":",1)[1]
    try:
        task_id = int(data)
    except:
        bot.answer_callback_query(call.id, "خطا در شناسه تسک.")
        return
    new = toggle_task_done(task_id)
    if new is None:
        bot.answer_callback_query(call.id, "تسک یافت نشد.")
        return
    # بعد از تغییر، مجدد پیام را برای همان تاریخ بازسازی کنیم.
    # اول باید تاریخ و chat رو از دیتابیس بدست بیاریم
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT chat_id,date FROM tasks WHERE id=?", (task_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        bot.answer_callback_query(call.id, "خطا.")
        return
    chat_id, date_iso = row
    new_text, keyboard = build_tasks_message_and_keyboard(chat_id, date_iso)
    # ویرایش پیامی که دکمه فشار داده شد (اگر ممکن بود)
    try:
        bot.edit_message_text(new_text, chat_id=call.message.chat.id, message_id=call.message.message_id,
                              reply_markup=keyboard, parse_mode='HTML')
    except Exception as e:
        # ممکنه پیام پاک شده باشه یا مجوز نباشه
        pass
    bot.answer_callback_query(call.id, "وضعیت به‌روز شد ✔️")

if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling()
