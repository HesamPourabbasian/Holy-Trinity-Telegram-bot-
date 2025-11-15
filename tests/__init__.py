import json
from persiantools.jdatetime import JalaliDate
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os

DATA_FILE = "tasks.json"

# -----------------------------
# Load & Save Storage (JSON)
# -----------------------------
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    migrated_data, changed = migrate_old_format(data)
    if changed:
        save_data(migrated_data)

    return migrated_data


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# -----------------------------
# Migration Helper (old → new)
# -----------------------------
def migrate_old_format(data):
    changed = False
    for user_id in data:
        for date in data[user_id]:
            new_list = []
            for item in data[user_id][date]:
                if isinstance(item, str):
                    new_list.append({"task": item, "done": False})
                    changed = True
                else:
                    new_list.append(item)
            data[user_id][date] = new_list
    return data, changed


# -----------------------------
# Helpers
# -----------------------------
def get_today_key():
    today = JalaliDate.today()
    return f"{today.day:02d}-{today.month:02d}"


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
# /clear command → remove all tasks today
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


# -----------------------------
# Start the bot
# -----------------------------
def main():
    app = ApplicationBuilder().token("8585854031:AAGytcSRlo_BP_mRigVMvLGLu20jwvbLNhU").build()

    app.add_handler(CommandHandler("add", add_task))
    app.add_handler(CommandHandler("done", done))
    app.add_handler(CommandHandler("tasks", list_tasks))
    app.add_handler(CommandHandler("clear", clear_tasks))  # ✅

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
