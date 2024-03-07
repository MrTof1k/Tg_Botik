# Импортируем необходимые классы.
import logging
import keyboard
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, ConversationHandler, MessageHandler, filters, CommandHandler
from config import BOT_TOKEN

# from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Запускаем логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)
# Сохранение информации для заявки
customer_information = open("customer_information.txt", "w")
# кнопки для некоторых вопросов
reply_keyboard = [['Моделирование и печать'],
                  ['Печать']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

reply_keyboard_strt = [['Да', "Нет"]]
markup_start = ReplyKeyboardMarkup(reply_keyboard_strt, one_time_keyboard=True)

reply_keyboard_plastic = [['PLA', 'ABS', 'HIPS', "PVA"],
                          ['SBS', 'NYLON', "FLEX", 'PETG']]
markup_plastic = ReplyKeyboardMarkup(reply_keyboard_plastic, one_time_keyboard=True)

# кнопки в сообщения бота
keyboard = [
    [InlineKeyboardButton("Option 1", url="https://cvetmir3d.ru/blog/poleznoe/vidy-plastika-dlya-3d-printera/")]]

reply_markup = InlineKeyboardMarkup(keyboard)


# Определяем функцию-обработчик сообщений.
# У неё два параметра, updater, принявший сообщение и контекст - дополнительная информация о сообщении.
# TIMER = 5
# таймер на 5 секунд
def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("close", close_keyboard))
    conv_handler = ConversationHandler(
        # Точка входа в диалог.
        # В данном случае — команда /start. Она задаёт первый вопрос.
        entry_points=[CommandHandler('start', start)],

        # Состояние внутри диалога.
        # Вариант с двумя обработчиками, фильтрующими текстовые сообщения.
        states={
            # Функция читает ответ на первый вопрос и задаёт второй.
            0: [MessageHandler(filters.TEXT & ~filters.COMMAND, sity)],
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
            # Функция читает ответ на второй вопрос и завершает диалог.
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, requirement)],
            3: [MessageHandler(filters.TEXT & ~filters.COMMAND, description)],
            4: [MessageHandler(filters.TEXT & ~filters.COMMAND, choice_of_plastic)],
            5: [MessageHandler(filters.TEXT & ~filters.COMMAND, second_response)]
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
        "Привет. Это бот для формирования заявок для 3D печати. \n"
        "Вы можете прервать заполнение заявки, послав команду /stop.", reply_markup=markup_start)
    return 0


async def sity(update, context):
    await update.message.reply_text("В каком городе вы живёте?:")

    customer_information.write(f"Город: {update.message.text} \n")
    d = {"Город" : update.message.text}
    context.bot_data.update(d)

    print(context.bot_data)
    return 1


async def name(update, context):
    await update.message.reply_text("Ваше ФИО:")

    customer_information.write(f"ФИО: {update.message.text} \n")
    d = {"ФИО": update.message.text}
    context.bot_data.update(d)
    return 2


async def requirement(update, context):
    await update.message.reply_text("Что вам нужно ?", reply_markup=markup)
    customer_information.write(f"Требования: {update.message.text} \n")
    d = {"Требования": update.message.text}
    context.bot_data.update(d)
    return 3


async def description(update, context):
    await update.message.reply_text("Дайте краткое описание.")
    customer_information.write(f"Описание: {update.message.text} \n")
    d = {"Описание": update.message.text}
    context.bot_data.update(d)
    return 4


async def choice_of_plastic(update, context):
    await update.message.reply_text("Выберите вид пластика", reply_markup=markup_plastic)
    await update.message.reply_text("Информация о пластиках", reply_markup=InlineKeyboardMarkup(keyboard))
    customer_information.write(f"Пластик: {update.message.text} \n")
    d = {"Пластик": update.message.text}
    context.bot_data.update(d)
    return 5


# async def application(update, context):
#     await update.message.reply_text("Приложите фото детали, чертежа или 3D модели.")
#     return 5


async def second_response(update, context):
    # Ответ на второй вопрос.
    # Мы можем его сохранить в базе данных или переслать куда-либо.
    weather = update.message.text
    logger.info(weather)
    await update.message.reply_text("Ваша заявка сформирована")
    customer_information.close()
    profile = open("customer_information.txt", "r")
    await update.message.reply_text(profile.read())
    s = [f"{i}: {context.bot_data[i]}" for i in context.bot_data]
    for i in s:
        await update.message.reply_text(i)

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


async def close_keyboard(update, context):
    await update.message.reply_text(
        "Ok",
        reply_markup=ReplyKeyboardRemove()
    )


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
