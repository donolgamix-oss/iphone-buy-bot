from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# === ВСТАВЬ СЮДА СВОИ ДАННЫЕ ===
TOKEN = '8508973670:AAFiogJSUfywMs_azCbR9tOMinXFz4M3W8c'  # ← ТВОЙ ТОКЕН (уже вставлен)
ADMIN_ID = 1181860611  # ← ТВОЙ ID (уже вставлен — ты получишь все заявки)

# Состояния
MODEL, MEMORY, BATTERY, PRICE = range(4)

# Клавиатуры
def start_keyboard():
    return ReplyKeyboardMarkup([['iPhone']], resize_keyboard=True)

def model_keyboard():
    models = [
        ['iPhone 7', 'iPhone 8'],
        ['iPhone X', 'iPhone 11'],
        ['iPhone 12', 'iPhone 13'],
        ['iPhone 14', 'iPhone 15'],
        ['Назад']
    ]
    return ReplyKeyboardMarkup(models, resize_keyboard=True)

def memory_keyboard():
    memory = [
        ['64 GB', '128 GB'],
        ['256 GB', '512 GB'],
        ['1 TB'],
        ['Назад']
    ]
    return ReplyKeyboardMarkup(memory, resize_keyboard=True)

# === Обработчики ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Хочешь сдать свой iPhone?\nНажми кнопку ниже",
        reply_markup=start_keyboard()
    )
    return MODEL

async def choose_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == 'iPhone':
        await update.message.reply_text("Выбери модель:", reply_markup=model_keyboard())
        return MODEL

    if text == 'Назад':
        await update.message.reply_text("Начнём заново.", reply_markup=start_keyboard())
        return MODEL

    valid_models = ['iPhone 7', 'iPhone 8', 'iPhone X', 'iPhone 11', 'iPhone 12', 'iPhone 13', 'iPhone 14', 'iPhone 15']
    if text not in valid_models:
        await update.message.reply_text("Выбери из списка!")
        return MODEL

    context.user_data['model'] = text
    await update.message.reply_text(f"Модель: {text}\n\nВыбери память:", reply_markup=memory_keyboard())
    return MEMORY

async def choose_memory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == 'Назад':
        await update.message.reply_text("Выбери модель:", reply_markup=model_keyboard())
        return MODEL

    valid_memory = ['64 GB', '128 GB', '256 GB', '512 GB', '1 TB']
    if text not in valid_memory:
        await update.message.reply_text("Выбери из списка!")
        return MEMORY

    context.user_data['memory'] = text
    await update.message.reply_text(
        f"Память: {text}\n\n"
        "Напиши % заряда батареи (0–100):",
        reply_markup=ReplyKeyboardRemove()
    )
    return BATTERY

async def get_battery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if not text.isdigit() or not (0 <= int(text) <= 100):
        await update.message.reply_text("Введи число от 0 до 100!")
        return BATTERY

    context.user_data['battery'] = text + '%'
    await update.message.reply_text("Теперь напиши желаемую сумму в тенге (например: 85000):")
    return PRICE

async def get_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if not text.isdigit() or int(text) < 1000:
        await update.message.reply_text("Сумма должна быть больше 1000 тенге!")
        return PRICE

    context.user_data['price'] = text + ' ₸'

    # === Формируем заявку ===
    user = update.effective_user
    summary = (
        f"*НОВАЯ ЗАЯВКА НА iPhone*\n\n"
        f"Пользователь: [{user.first_name}](tg://user?id={user.id})\n"
        f"ID: `{user.id}`\n"
        f"Модель: {context.user_data['model']}\n"
        f"Память: {context.user_data['memory']}\n"
        f"Батарея: {context.user_data['battery']}\n"
        f"Сумма: {context.user_data['price']}\n\n"
        f"Свяжитесь с ним!"
    )

    # Отправляем ТЕБЕ
    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=summary,
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
    except Exception as e:
        await context.bot.send_message(ADMIN_ID, f"Ошибка: {e}")

    # Ответ пользователю
    await update.message.reply_text(
        "*Спасибо за заявку!*\n\n"
        "Мы свяжемся с вами в ближайшее время.",
        parse_mode='Markdown',
        reply_markup=start_keyboard()
    )

    context.user_data.clear()
    return MODEL

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отменено.", reply_markup=start_keyboard())
    context.user_data.clear()
    return MODEL

# === Запуск ===
def main():
    app = Application.builder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler('start', start),
                      MessageHandler(filters.TEXT & ~filters.COMMAND, start)],
        states={
            MODEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_model)],
            MEMORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_memory)],
            BATTERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_battery)],
            PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_price)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    app.add_handler(conv)
    print("Бот запущен... Ожидаю заявки.")
    app.run_polling()

if __name__ == '__main__':
    main()