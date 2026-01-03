import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    PreCheckoutQueryHandler,
    MessageHandler,
    Filters,
)

# Включаем логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

def start(update: Update, context):
    """Приветствие и краткая инструкция."""
    update.message.reply_text(
        "👋 Привет! Этот бот позволяет покупать Telegram Stars. "
        "Нажмите /buy, чтобы выбрать пакет звёзд."
    )

def buy(update: Update, context):
    """Показываем доступные пакеты звёзд."""
    keyboard = [
        [InlineKeyboardButton("⭐ 10 Stars", callback_data="buy_10")],
        [InlineKeyboardButton("⭐ 50 Stars", callback_data="buy_50")],
        [InlineKeyboardButton("⭐ 100 Stars", callback_data="buy_100")],
    ]
    update.message.reply_text(
        "Выберите количество звёзд:", reply_markup=InlineKeyboardMarkup(keyboard)
    )

def send_invoice(update: Update, context):
    """Формируем и отправляем счёт на выбранный пакет."""
    query = update.callback_query
    query.answer()
    stars = query.data.split("_")[1]
    price = int(stars)
    prices = [LabeledPrice(label=f"{stars} Telegram Stars", amount=price)]
    query.message.reply_invoice(
        title=f"Покупка {stars} ⭐",
        description="Покупка внутренней валюты Telegram Stars",
        payload=f"stars_{stars}",
        provider_token="",       # для Stars оставляем пустым
        currency="XTR",          # Stars-валюта
        prices=prices,
        start_parameter=f"buy-stars-{stars}",
    )

def precheckout_callback(update: Update, context):
    """Отвечаем на pre-checkout запрос."""
    query = update.pre_checkout_query
    query.answer(ok=True)

def successful_payment_callback(update: Update, context):
    """Уведомляем пользователя об успешной оплате."""
    total_amount = update.message.successful_payment.total_amount
    update.message.reply_text(
        f"✅ Спасибо за покупку! Вы купили {total_amount} звёзд."
    )

def error_handler(update, context):
    """Логируем ошибки."""
    logger.warning("Update \"%s\" caused error \"%s\"", update, context.error)

def main():
    """Запуск бота."""
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError(
            "BOT_TOKEN environment variable is not set. "
            "Please set BOT_TOKEN to your bot's API token."
        )

    updater = Updater(token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("buy", buy))
    dispatcher.add_handler(CallbackQueryHandler(send_invoice))
    dispatcher.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    dispatcher.add_handler(
        MessageHandler(Filters.successful_payment, successful_payment_callback)
    )
    dispatcher.add_error_handler(error_handler)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
