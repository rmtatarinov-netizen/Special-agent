import os
import logging
from dotenv import load_dotenv
import telebot
from agent.agent import AIAgent

load_dotenv()

# Настройка логирования для бота
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("TelegramBot")

def main():
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN не найден в .env")
        print("Ошибка: Добавьте TELEGRAM_BOT_TOKEN в файл .env")
        return

    bot = telebot.TeleBot(TOKEN)
    agent = AIAgent()

    logger.info("Бот запущен и ожидает сообщений...")

    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        welcome_text = (
            "🤖 Привет! Я твой AI-Агент.\n\n"
            "Я умею:\n"
            "🌤 Погоду $\rightarrow$ 'Погода в Москве'\n"
            "💰 Крипту $\rightarrow$ 'Курс Bitcoin в USD'\n"
            "🌐 Поиск $\rightarrow$ 'Найди новости о SpaceX'\n"
            "📅 Напоминания $\rightarrow$ 'Напомни мне купить хлеб'\n"
            "🖼 QR-коды $\rightarrow$ 'Создай QR для google.com'\n"
            "💻 Терминал $\rightarrow$ 'Создай файл test.txt'\n\n"
            "Просто напиши мне, что нужно сделать!"
        )
        bot.reply_to(message, welcome_text)

    @bot.message_handler(func=lambda message: True)
    def handle_message(message):
        try:
            logger.info(f"Сообщение от {message.chat.id}: {message.text}")
            
            # Отправляем статус "печатает", чтобы пользователь видел активность
            bot.send_chat_action(message.chat.id, 'typing')
            
            # Обработка через агента
            response = agent.run(message.text)
            
            # Если агент создал QR-код, отправляем его файлом
            if "qr_code.png" in response and os.path.exists("qr_code.png"):
                with open("qr_code.png", "rb") as photo:
                    bot.send_photo(message.chat.id, photo, caption=response)
            else:
                bot.reply_to(message, response)
                
        except Exception as e:
            logger.error(f"Ошибка обработки сообщения: {e}", exc_info=True)
            bot.reply_to(message, "Произошла ошибка при обработке вашего запроса. Попробуйте позже.")

    bot.infinity_polling()

if __name__ == "__main__":
    main()
