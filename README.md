# 📝 Telegram Daily Tasks Bot

A simple yet powerful **Telegram bot** for managing **daily tasks** with support for **Jalali (Persian) dates**.
Users can add tasks, mark them as done, list today's tasks, and clear them — all stored locally in a JSON database.

---

## 🚀 Features

### ✅ Add tasks

Use `/add` followed by tasks separated with a dash `-`
Example:

```
/add پروژه - باشگاه - کتابخونه
```

### ✔️ Mark a task as done

Example:

```
/done باشگاه
```

### 📋 List today’s tasks

Show all tasks for the current Jalali date:

```
/tasks
```

### 🗑 Clear all tasks for today

```
/clear
```

---

## 🗂 Data Storage

* Tasks are stored in a **tasks.json** file.
* Each user has their own data section based on Telegram user ID.
* Tasks are saved by **Jalali date** (`DD-MM` format).
* Format example:

```json
{
  "123456789": {
    "12-08": [
      { "task": "باشگاه", "done": false },
      { "task": "کتابخوانی", "done": true }
    ]
  }
}
```

---

## 🔄 Auto Migration System (Old → New Format)

If old data is detected (tasks as plain strings), it automatically converts them into the new structured format:

From:

```json
["باشگاه", "کتابخونه"]
```

To:

```json
[
  { "task": "باشگاه", "done": false },
  { "task": "کتابخونه", "done": false }
]
```

---

## 🧠 How It Works (Overview)

* Uses **persiantools** for Jalali date handling.
* Uses **python-telegram-bot v20+** (`ApplicationBuilder`).
* Handles 4 commands: `/add`, `/done`, `/tasks`, `/clear`.
* Data is loaded and saved via JSON with auto-migration.
* Each task has:

  ```json
  { "task": "some task", "done": false }
  ```

---

## 📦 Installation

### 1. Clone the project

```bash
git clone https://github.com/yourusername/daily-tasks-bot
cd daily-tasks-bot
```

### 2. Install dependencies

```bash
pip install python-telegram-bot persiantools
```

### 3. Set your bot token

Replace the token in `main()`:

```python
ApplicationBuilder().token("YOUR_BOT_TOKEN_HERE")
```

### 4. Run the bot

```bash
python bot.py
```

---

## 🧪 Example Usage

User:

```
/add خرید - دانشگاه - تمرین
```

Bot:

```
تسک‌ها اضافه شد ✔️
```

User:

```
/done خرید
```

Bot:

```
تسک تیک خورد ✔️
```

User:

```
/tasks
```

Bot example output:

```
🗓 تسک‌های امروز برای Ali:

⬜ دانشگاه
⬜ تمرین
✅ خرید
```

---

## 📌 Notes

* This bot uses **long polling**.
* Data is stored **locally** — no database setup required.
---

## 🛠 Technologies Used

* Python 3
* python-telegram-bot
* persiantools
* JSON storage

---
