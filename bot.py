import logging
import os
import sys
from datetime import time
from telegram.ext import Updater, CommandHandler, CallbackContext
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
else:
    logger.error("No MODE specified!")
    sys.exit(1)


def start_handler(bot, update):
    logger.info("User {} started bot".format(update.effective_user["id"]))
    update.message.reply_text("Hello from Python!\nPress /random to get random number")


def random_handler(bot, update):
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


def callback_timer(bot, update, job_queue):
    bot.send_message(chat_id=update.message.chat_id,
                     text='Daily reminder has been set! You\'ll get notified at 8 AM daily')
    datetime_obj_naive = time(hour=11, minute=8, second=10)
    job_queue.run_daily(callback_alarm,
                        days=(0, 1, 2, 3, 4, 5, 6),
                        context=update.message.chat_id,
                        time=datetime_obj_naive
                        )


if __name__ == '__main__':
    logger.info("Starting bot")
    updater = Updater(back._TOKEN, request_kwargs=back._REQUEST_KWARGS)

    updater.dispatcher.add_handler(CommandHandler("start", start_handler))
    updater.dispatcher.add_handler(CommandHandler("get", random_handler))
    timer_handler = CommandHandler('schedule', callback_timer, pass_job_queue=True)
    updater.dispatcher.add_handler(timer_handler)
    run(updater)
