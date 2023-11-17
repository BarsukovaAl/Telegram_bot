from telegram import Update, ParseMode
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, Dispatcher
from telegram.ext import MessageHandler, CommandHandler, CallbackQueryHandler
from telegram.ext import CallbackContext
from telegram.ext import Filters

import logging
import datetime

from key import TOKEN
from fsm import register_handler

logging.basicConfig(
    format='%(asctime)s | %(levelname)s | %(name)s: %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    updater = Updater(token=TOKEN)
    dispatcher: Dispatcher = updater.dispatcher

    start_handler = CommandHandler(['start', 'help'], do_start)
    echo_handler = MessageHandler(Filters.text, do_echo)
    keyboard_handler = CommandHandler('keyboard', do_keyboard)
    inline_keyboard_handler = CommandHandler('inline_keyboard', do_inline_keyboard)
    set_timer_handler = MessageHandler(Filters.text('СТАРТ'), set_timer)
    delete_timer_handler = MessageHandler(Filters.text('СТОП'), delete_timer)
    callback_handler = CallbackQueryHandler(keyboard_react)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(keyboard_handler)
    dispatcher.add_handler(inline_keyboard_handler)
    dispatcher.add_handler(set_timer_handler)
    dispatcher.add_handler(callback_handler)
    dispatcher.add_handler(delete_timer_handler)
    dispatcher.add_handler(register_handler)
    dispatcher.add_handler(echo_handler)
    updater.start_polling()
    logger.info(updater.bot.getMe())
    updater.idle()


def do_echo(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    text = update.message.text

    logger.info(f'{username}{user_id} вызвал функцию "do_echo"')
    logger.info(f'{username}{user_id} вызвал функцию "start"')
    answer = f'Твои данные: {username}, {user_id}\nТы написал(а): {text}\nЯ знаю команды:\n/start\n/help\n/keyboard\n' \
             f'/inline_keyboard'
    update.message.reply_text(answer, reply_markup=ReplyKeyboardRemove())


def do_start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    logger.info(f'{user_id=} вызвал функцию start')
    text = [
        'Приветствую, любимка',
        f'Твой <b>{user_id=}</b>',
        'Я знаю команды:',
        '/start',
        '/keyboard',
        '/inline_keyboard',
        '/register',
        '/set',

    ]
    text = '\n'.join(text)

    update.message.reply_text(text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)


def do_keyboard(update: Update, context: CallbackContext):
    buttons = [
        ['СТАРТ', 'СТОП']
    ]
    logger.info(f'Созданы кнопочки!{buttons}')
    keyboard = ReplyKeyboardMarkup(buttons)
    logger.info(f'Создана клавиатура {keyboard}')
    text = 'Выбери нужную тебе кнопку'

    update.message.reply_text(
        text,
        reply_markup=keyboard
    )


def do_inline_keyboard(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    logger.info(f'{user_id=} вызвал функцию do_inline_keyboard')
    buttons = [
        [('погода сегодня', 'https://yandex.ru/pogoda/moscow?utm_source=serp&utm_campaign=helper&utm_medium=desktop'
                            '&utm_content=helper_desktop_main&utm_term=title&lat=55.755863&lon=37.6177'),
         ('расписание электричек из мск',
          'https://rasp.yandex.ru/suburban/moskvoreche-platform--chekhov-train-station/today')],
         [('расписание электричек в мск',
           'https://rasp.yandex.ru/suburban/chekhov-train-station--moskvoreche-platform/today'),
          ('кухня', 'https://ctc.ru/projects/serials/kukhnya/?ysclid=lo8jf2yca1753403068')],
    ]
    keyboard_buttons = [[InlineKeyboardButton(text=text[0], callback_data=text[0], url=text[1]) for text in row] for row
                        in buttons]

    logger.info(f'Созданы кнопки {buttons}')
    keyboard = InlineKeyboardMarkup(keyboard_buttons)
    logger.info(f'Создана клавиатура {keyboard}')
    text = 'Выбери нужную тебе кнопку'
    update.message.reply_text(
        text,
        reply_markup=keyboard
    )


def keyboard_react(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = update.effective_user.id
    logger.info(f'{user_id=} вызвал функцию keyboard_react')
    buttons = [
        ['Раз', 'Два'],
        ['Три', 'Четыре'],
        ['Хи-Хи']
    ]
    for row in buttons:
        if query.data in row:
            row.pop(row.index(query.data))
    keyboard_buttons = [[InlineKeyboardButton(text=text, callback_data=text) for text in row] for row in buttons]
    logger.info(f'Созданы кнопки {buttons}')
    keyboard = InlineKeyboardMarkup(keyboard_buttons)
    text = 'попробуй, нажми'
    query.edit_message_text(
        text,
        reply_markup=keyboard
    )


def set_timer(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    context.bot_data['user_id'] = user_id
    context.bot_data['timer'] = datetime.datetime.now()
    context.bot_data['timer_job'] = context.job_queue.run_repeating(show_seconds, 1)


def show_seconds(context: CallbackContext):
    logger.info(f'{context.job_queue.jobs()}')
    message_id = context.bot_data.get('message_id', None)
    user_id = context.bot_data['user_id']
    timer = datetime.datetime.now() - context.bot_data['timer']
    timer = timer.seconds
    text = f'прошло {timer} секунд'
    text += '\nнажмите /stop чтобы остановить таймер'
    if not message_id:
        message = context.bot.send_message(user_id, text)
        context.bot_data['message_id'] = message.message_id
    else:
        context.bot.edit_message_text(text, chat_id=user_id, message_id=message_id)


def stop_timer(update: Update, context: CallbackContext):
    logger.info(f'Запущена функция delete_timer')
    timer = datetime.datetime.now() - context.bot_data['timer']
    context.bot_data['timer_job'].schedule_removal()
    update.message.reply_text(f'Таймер остановлен. Прошло {timer} секунд')

def delete_timer(update: Update, context: CallbackContext):
    logger.info(f'Запущена функция delete_timer')
    timer = datetime.datetime.now() - context.bot_data['timer']
    var = context.bot_data['timer_job']
    for job in context.job_queue.jobs():
        job.schedule_removal()
        update.message.reply_text(f'Таймер остановлен, прошло {timer.seconds} секунд')



if __name__ == '__main__':
    main()
