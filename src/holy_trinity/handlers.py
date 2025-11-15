from telegram import Update
from telegram.ext import ContextTypes
from storage import load_data, save_data
from helpers import get_today_key

# -----------------------------
# /add command
# -----------------------------
async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    user_id = str(update.effective_user.id)
    if not context.args:
        await update.message.reply_text("مثال:\n/add پروژه - باشگاه - کتابخونه")
        return

    today_key = get_today_key()
    tasks_raw = " ".join(context.args)
    raw_list = [t.strip() for t in tasks_raw.split("-") if t.strip()]
    tasks = [{"task": t, "done": False} for t in raw_list]

    if user_id not in data:
        data[user_id] = {}
    if today_key not in data[user_id]:
        data[user_id][today_key] = []

    data[user_id][today_key].extend(tasks)
    save_data(data)
    await update.message.reply_text("تسک‌ها اضافه شد ✔️")


# -----------------------------
# /done command
# -----------------------------
async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    user_id = str(update.effective_user.id)
    today_key = get_today_key()
    if not context.args:
        await update.message.reply_text("مثال:\n/done باشگاه")
        return
    task_done = " ".join(context.args).strip()
    if user_id not in data or today_key not in data[user_id]:
        await update.message.reply_text("امروز هیچ تسکی ثبت نکردی.")
        return
    for item in data[user_id][today_key]:
        if item["task"] == task_done:
            item["done"] = True
            save_data(data)
            await update.message.reply_text("تسک تیک خورد ✔️")
            return
    await update.message.reply_text("این تسک در لیست امروز نیست.")


# -----------------------------
# /tasks command
# -----------------------------
async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    user_id = str(update.effective_user.id)
    today_key = get_today_key()
    if user_id not in data or today_key not in data[user_id]:
        await update.message.reply_text("برای امروز هیچ تسکی ثبت نکردی.")
        return

    tasks_list = data[user_id][today_key]
    if not tasks_list:
        await update.message.reply_text("برای امروز هیچ تسکی ثبت نشده.")
        return

    user_name = update.effective_user.first_name
    msg = f"🗓 *تسک‌های امروز برای {user_name}:*\n\n"
    for item in tasks_list:
        check = "✅" if item["done"] else "⬜"
        msg += f"{check} {item['task']}\n"
    await update.message.reply_text(msg, parse_mode="Markdown")


# -----------------------------
# /clear command
# -----------------------------
async def clear_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    user_id = str(update.effective_user.id)
    today_key = get_today_key()
    if user_id not in data or today_key not in data[user_id] or not data[user_id][today_key]:
        await update.message.reply_text("برای امروز هیچ تسکی ثبت نکرده‌ای.")
        return
    data[user_id][today_key] = []
    save_data(data)
    await update.message.reply_text("تمام تسک‌های امروز پاک شد 🗑️")
