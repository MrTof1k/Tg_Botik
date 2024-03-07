# Импортируем необходимые классы.
import logging
import keyboard
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import Application,ConversationHandler, MessageHandler, filters, CommandHandler
from config import BOT_TOKEN

# Запускаем логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)


# Определяем функцию-обработчик сообщений.
# У неё два параметра, updater, принявший сообщение и контекст - дополнительная информация о сообщении.
async def echo(update, context):
    # У объекта класса Updater есть поле message,
    # являющееся объектом сообщения.
    # У message есть поле text, содержащее текст полученного сообщения,
    # а также метод reply_text(str),
    # отсылающий ответ пользователю, от которого получено сообщение.
    await update.message.reply_text(update.message.text)


async def mute(update, context):
    await update.message.reply_text(
        "mute")
    keyboard.send("volume mute")

async def next(update, context):
    await update.message.reply_text(
        "next track")
    keyboard.send("next track")


async def previous(update, context):
    await update.message.reply_text(
        "previous track")
    keyboard.send("previous track")


async def volume_up(update, context):
    await update.message.reply_text(
        "volume up")
    keyboard.send("volume up")


async def volume_down(update, context):
    await update.message.reply_text(
        "volume down")
    keyboard.send("volume down")


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("next", next))
    application.add_handler(CommandHandler("previous", previous))
    application.add_handler(CommandHandler("volume_up", volume_up))
    application.add_handler(CommandHandler("volume_down", volume_down))
    application.add_handler(CommandHandler("mute", mute))
    application.run_polling()
    application.add_handler(CommandHandler("close", close_keyboard))


reply_keyboard = [['/next', '/previous'],
                  ['/volume_up', '/volume_down']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)


async def start(update, context):
    await update.message.reply_text(
        "Я бот-справочник. Какая информация вам нужна?",
        reply_markup=markup
    )


async def close_keyboard(update, context):
    await update.message.reply_text(
        "Ok",
        reply_markup=ReplyKeyboardRemove()
    )


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()
