# Импортируем необходимые классы.
import logging
import keyboard
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, ConversationHandler, MessageHandler, filters, CommandHandler, Updater
from config import BOT_TOKEN, ID_GROUP

# Запускаем логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)
# Сохранение информации для заявки
# txt файл в который планировалось записывать заявку, но потом начал хранить её в bot_data(гораздо удобней)
# думаю сюда зааписать сообщение или html для сообщения от бота
customer_information = open("customer_information.txt", "w")
# кнопки для некоторых вопросов
# requirement
reply_keyboard = [['Моделирование и печать'],
                  ['Печать']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

# start
reply_keyboard_strt = [['Да', "/stop"]]
markup_start = ReplyKeyboardMarkup(reply_keyboard_strt, one_time_keyboard=True)

# application
reply_keyboard_application = [['Да', "Заново"]]
markup_application = ReplyKeyboardMarkup(reply_keyboard_application, one_time_keyboard=True)

# pchoice_of_plastic
reply_keyboard_plastic = [['PLA', 'ABS', 'HIPS', "PVA"],
                          ['SBS', 'NYLON', "FLEX", 'PETG']]
markup_plastic = ReplyKeyboardMarkup(reply_keyboard_plastic, one_time_keyboard=True)

# кнопки в сообщения бота choice_of_plastic
keyboard = [
    [InlineKeyboardButton("Option 1", url="https://cvetmir3d.ru/blog/poleznoe/vidy-plastika-dlya-3d-printera/")]]

reply_markup = InlineKeyboardMarkup(keyboard)


# Определяем функцию-обработчик сообщений.
# У неё два параметра, updater, принявший сообщение и контекст - дополнительная информация о сообщении.

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
            5: [MessageHandler(filters.TEXT & ~filters.COMMAND, second_response)],
            6: [MessageHandler(filters.TEXT & ~filters.COMMAND, proverka)]

        },

        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop', stop)]
    )

    application.add_handler(conv_handler)

    application.run_polling()


# точка входа в диалог
async def start(update, context):
    await update.message.reply_text(
        "Привет. Это бот для формирования заявок для 3D печати. \n"
        "Вы можете прервать заполнение заявки, послав команду /stop.\n"
        "Хотите начать заполнение заявки?", reply_markup=markup_start)
    return 0


# Дальнейшие вопросы для коректного заббора сообщений-ответов нужно вопрос задавать в предыдущей функции
async def sity(update, context):
    await update.message.reply_text("В каком городе вы живёте?:")
    # if filters.TEXT:
    #   customer_information.write(f"Город: {update.message.text} \n")
    return 1


async def name(update, context):
    await update.message.reply_text("Ваше ФИО:")
    d = {"Город": update.message.text}
    # customer_information.write(f"ФИО: {update.message.text} \n")

    context.bot_data.update(d)
    return 2


async def requirement(update, context):
    await update.message.reply_text("Что вам нужно ?", reply_markup=markup)
    # customer_information.write(f"Требования: {update.message.text} \n")
    d = {"ФИО": update.message.text}

    context.bot_data.update(d)
    return 3


async def description(update, context):
    await update.message.reply_text("Дайте краткое описание.")
    # customer_information.write(f"Описание: {update.message.text} \n")

    d = {"Требования": update.message.text}
    context.bot_data.update(d)
    return 4


async def choice_of_plastic(update, context):
    await update.message.reply_text("Выберите вид пластика", reply_markup=markup_plastic)
    await update.message.reply_text("Информация о пластиках", reply_markup=InlineKeyboardMarkup(keyboard))
    # (красивый кнопка)
    # customer_information.write(f"Пластик: {update.message.text} \n")

    d = {"Описание": update.message.text}
    context.bot_data.update(d)
    return 5


async def second_response(update, context):
    d = {"Пластик": update.message.text}
    context.bot_data.update(d)

    weather = update.message.text
    logger.info(weather)
    await update.message.reply_text("Ваша заявка сформирована")

    # формируем одно большое сообщение сюдаже надо приписать пересылку картинки желательно её хранить с id пользователя
    # иначе когда 2 чела одновременно будут делать заявку бот попутает картинки
    s = (f"Город: {context.bot_data["Город"]} \n"
         f"ФИО: {context.bot_data["ФИО"]} \n"
         f"Требования: {context.bot_data["Требования"]} \n"
         f"Описание: {context.bot_data["Описание"]} \n"
         f"Пластик: {context.bot_data["Пластик"]}")
    await update.message.reply_text(s)

    # опять раньше спрашиваем тк будет включена след функция
    await update.message.reply_text("Всё верно ?", reply_markup=markup_application)

    return 6


# функция костыль (кудаж без них) спрашиваем у пользователя всёли верно если да то присылаем в общий чат если нет,
# то всё заново
async def proverka(update, context):
    if update.message.text == "Да":
        await application(update, context)
    if update.message.text == "Заново":
        await update.message.reply_text("Давайте начнём заново /start")

    return ConversationHandler.END


# функция отправки заявки в общ группу
async def application(update, context):
    s = (f"Город: {context.bot_data["Город"]} \n"
         f"ФИО: {context.bot_data["ФИО"]} \n"
         f"Требования: {context.bot_data["Требования"]} \n"
         f"Описание: {context.bot_data["Описание"]} \n"
         f"Пластик: {context.bot_data["Пластик"]}")
    await context.bot.send_message(
        chat_id=ID_GROUP,
        text=s
    )
    await update.message.reply_text("Заявка успешно отправлена")
    await stop(update, context)


async def stop(update, context):
    await update.message.reply_text("Всего доброго!")
    return ConversationHandler.END


async def close_keyboard(update, context):
    await update.message.reply_text(
        "Ok",
        reply_markup=ReplyKeyboardRemove()
    )

#Это Серёжка он держит весь этот код
#       (•_• )
# 　　＿ノ ヽ ノ＼ __
# 　 /　`/ ⌒Ｙ⌒ Ｙ　ヽ
# 　(　 (三ヽ人　 /　　 |
# 　|　ﾉ⌒＼ ￣￣ヽ　 ノ
# 　ヽ＿＿＿＞､＿＿_／
# 　　　 ｜( 王 ﾉ〈　
# 　　　 /ﾐ`ー―彡\


if __name__ == '__main__':
    main()
