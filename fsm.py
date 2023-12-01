from telegram import Update
from telegram import ReplyKeyboardRemove
from telegram.ext import MessageHandler, CommandHandler, ConversationHandler
from telegram.ext import CallbackContext
from telegram.ext import Filters

import logging
from db import write_to_db

logger = logging.getLogger(__name__)

WAIT_OK, WAIT_NAME, WAIT_SURNAME, WAIT_BIRTHDAY = range(3)



def check_register(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    logger.info(f'{username=} {user_id=} вызвал функцию check_register')
    user = find_user_by_id(user_id)
    if not usesr:
        return ask_name(update,context)
    answer = [
        f'Привет!',
        f'Ты уже зарегистрирован со следующими данными:\n',
        f'Имя: {user[1]}',
        f'Фамилия: {user[2]}',
        

    ]
    answer = '\n'.join(answer)
    update.message.reply_text(answer, reply_markup=ReplyKeyboardRemove())
def ask_name(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    logger.info(f'{username=} {user_id=} вызвал функцию ask_name')
    answer = [
        f'Привет!',
        f'Назови свое имя'
    ]
    answer = '\n'.join(answer)
    update.message.reply_text(answer, reply_markup=ReplyKeyboardRemove())

    return WAIT_NAME


def get_name(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    text = update.message.text
    logger.info(f'{username=} {user_id=} вызвал функцию get_name')
    write_to_db('userid', 'name', 'surname', 'birthday')
    answer = [
        f'Твое имя - {text}'
    ]
    answer = '\n'.join(answer)
    update.message.reply_text(answer)

    return ask_surname(update, context)


def ask_surname(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    logger.info(f'{username=} {user_id=} вызвал функцию ask_surname')
    answer = [
        f'Назови свою фамилию'
    ]
    answer = '\n'.join(answer)
    update.message.reply_text(answer)

    return WAIT_SURNAME


def get_surname(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    text = update.message.text
    logger.info(f'{username=} {user_id=} вызвал функцию get_surname')
    answer = [
        f'Твоя фамилия - {text}'
    ]
    answer = '\n'.join(answer)
    update.message.reply_text(answer)

    return ask_birthday(update, context)


def ask_birthday(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    logger.info(f'{username=} {user_id=} вызвал функцию ask_birthday')
    answer = [
        f'Напиши свою дату рождения'
    ]
    answer = '\n'.join(answer)
    update.message.reply_text(answer)

    return WAIT_BIRTHDAY


def get_birthday(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    text = update.message.text
    logger.info(f'{username=} {user_id=} вызвал функцию get_birthday')
    answer = [
        f'Твоя дата рождения - {text}'
    ]
    answer = '\n'.join(answer)
    update.message.reply_text(answer)

    return register(update, context)


def register(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    logger.info(f'{username=} {user_id=} вызвал функцию register')
    answer = [
        f'Привет!',
        f'Зарегистрировал тебя!'
    ]
    answer = '\n'.join(answer)
    update.message.reply_text(answer)

    return ConversationHandler.END


register_handler = ConversationHandler(
    entry_points=[CommandHandler('register', ask_name)],
    states={
        WAIT_NAME: [MessageHandler(Filters.text, get_name)],
        WAIT_SURNAME: [MessageHandler(Filters.text, get_surname)],
        WAIT_BIRTHDAY: [MessageHandler(Filters.text, get_birthday)],
    },
    fallbacks=[]
)
