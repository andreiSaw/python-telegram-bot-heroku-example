import logging
import os
import sys
from datetime import time

from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, PicklePersistence, run_async
import telegram

import back

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

if back._MODE == "dev":
    def run(updater):
        updater.start_polling()
elif back._MODE == "prod":
    def run(updater):
        PORT = int(os.environ.get("PORT", "8443"))
        HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
        updater.start_webhook(listen="0.0.0.0",
                              port=PORT,
                              url_path=back._TOKEN)
        updater.bot.set_webhook("https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, back._TOKEN))
        updater.idle()

else:
    logger.error("No MODE specified!")
    sys.exit(1)

persistence = PicklePersistence('./db')


def start_handler(update: Update, context: CallbackContext):
    update.message.reply_text("Hi there!")


def random_handler(update: Update, context: CallbackContext):
    the_link = "https://www.horoscope.com/us/horoscopes/general/horoscope-general-daily-today.aspx?sign=8"
    logger.info("User {} got horoscope {}".format(update.effective_user["id"], the_link))
    msg = back.get_data(the_link)
    logger.debug(msg)
    update.message.reply_text("Your horoscope for today: {}".format(msg))


def callback_alarm(bot, job):
    the_link = "https://www.horoscope.com/us/horoscopes/general/horoscope-general-daily-today.aspx?sign=8"
    logger.info("Send to chat {}".format(job.context))
    msg = back.get_data(the_link)
    logger.debug(msg)
    bot.send_message(chat_id=job.context, text="Your horoscope for today: {}".format(msg))


@run_async
def callback_timer(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.message.chat_id,
                             text='Daily reminder has been set! You\'ll get notified at 8 AM daily GMT+3')
    datetime_obj_naive = time(hour=11, minute=8, second=10)
    context.job_queue.run_daily(callback_alarm,
                                days=(0, 1, 2, 3, 4, 5, 6),
                                context=update.message.chat_id,
                                time=datetime_obj_naive
                                )


def pong(update, context):
    update.message.reply_text('Pong')


def get_list(context: CallbackContext) -> list:
    return context.user_data.setdefault('list', [])


def parse_command(update: Update) -> (str, str):
    key, value = update.message.text.split(' ', 1)
    return key, value


def list_add(update: Update, context: CallbackContext):
    key, value = parse_command(update)
    get_list(context).append(value)
    update.message.reply_text('Saved 💾')


def list_delete(update: Update, context: CallbackContext):
    key, value = parse_command(update)
    get_list(context).remove(value)
    update.message.reply_text('Deleted 🗑')


def list_all(update: Update, context: CallbackContext):
    items = get_list(context)
    update.message.reply_text('\n'.join(items) if len(items) > 0 else 'List empty 😢')


def list_clear(update: Update, context: CallbackContext):
    get_list(context).clear()
    update.message.reply_text('Cleared 🧼')


if __name__ == '__main__':
    logger.info("Starting bot")
    updater = Updater(back._TOKEN, request_kwargs=back._REQUEST_KWARGS, persistence=persistence, use_context=True)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler('ping', pong))
    dp.add_handler(CommandHandler("start", start_handler))
    dp.add_handler(CommandHandler("get", random_handler))
    timer_handler = CommandHandler('schedule', callback_timer, pass_job_queue=True)
    dp.add_handler(timer_handler)

    dp.add_handler(CommandHandler('add', list_add))
    dp.add_handler(CommandHandler('delete', list_delete))
    dp.add_handler(CommandHandler('all', list_all))
    dp.add_handler(CommandHandler('clear', list_clear))

    run(updater)
