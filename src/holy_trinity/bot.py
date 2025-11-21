from telegram.ext import ApplicationBuilder, CommandHandler
from handlers import add_task, done, list_tasks, clear_tasks


def main():
    app = ApplicationBuilder().token("8585854031:AAGytcSRlo_BP_mRigVMvLGLu20jwvbLNhU").build()
    app.add_handler(CommandHandler("add", add_task))
    app.add_handler(CommandHandler("done", done))
    app.add_handler(CommandHandler("tasks", list_tasks))
    app.add_handler(CommandHandler("clear", clear_tasks))
    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
