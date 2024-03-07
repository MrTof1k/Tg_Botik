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
# TIMER = 5  # таймер на 5 секунд
def main():
    application = Application.builder().token(BOT_TOKEN).build()
    conv_handler = ConversationHandler(
        # Точка входа в диалог.
        # В данном случае — команда /start. Она задаёт первый вопрос.
        entry_points=[CommandHandler('start', start)],

        # Состояние внутри диалога.
        # Вариант с двумя обработчиками, фильтрующими текстовые сообщения.
        states={
            # Функция читает ответ на первый вопрос и задаёт второй.
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, first_response)],
            # Функция читает ответ на второй вопрос и завершает диалог.
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, second_response)]
        },

        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop', stop)]
    )

    application.add_handler(conv_handler)

    # application.add_handler(CommandHandler("set", set_timer))
    # application.add_handler(CommandHandler("unset", unset))
    application.run_polling()
async def start(update, context):
    await update.message.reply_text(
        "Привет. Пройдите небольшой опрос, пожалуйста!\n"
        "Вы можете прервать опрос, послав команду /stop.\n"
        "В каком городе вы живёте?")

    # Число-ключ в словаре states —
    # втором параметре ConversationHandler'а.
    return 1
async def first_response(update, context):
    # Это ответ на первый вопрос.
    # Мы можем использовать его во втором вопросе.
    locality = update.message.text
    await update.message.reply_text(
        f"Какая погода в городе {locality}?")
    # Следующее текстовое сообщение будет обработано
    # обработчиком states[2]
    return 2


async def second_response(update, context):
    # Ответ на второй вопрос.
    # Мы можем его сохранить в базе данных или переслать куда-либо.
    weather = update.message.text
    logger.info(weather)
    await update.message.reply_text("Спасибо за участие в опросе! Всего доброго!")
    return ConversationHandler.END  # Константа, означающая конец диалога.
    # Все обработчики из states и fallbacks становятся неактивными.


async def stop(update, context):
    await update.message.reply_text("Всего доброго!")
    return ConversationHandler.END

def remove_job_if_exists(name, context):
    """Удаляем задачу по имени.
    Возвращаем True если задача была успешно удалена."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True



# Обычный обработчик, как и те, которыми мы пользовались раньше.
# async def set_timer(update, context):
#     """Добавляем задачу в очередь"""
#     chat_id = update.effective_message.chat_id
#     # Добавляем задачу в очередь
#     # и останавливаем предыдущую (если она была)
#     job_removed = remove_job_if_exists(str(chat_id), context)
#     context.job_queue.run_once(task, TIMER, chat_id=chat_id, name=str(chat_id), data=TIMER)
#
#     text = f'Вернусь через 5 с.!'
#     if job_removed:
#         text += ' Старая задача удалена.'
#     await update.effective_message.reply_text(text)

# async def task(context):
#     """Выводит сообщение"""
#     await context.bot.send_message(context.job.chat_id, text=f'КУКУ! 5c. прошли!')






if __name__ == '__main__':
    main()
