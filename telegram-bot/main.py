from telegram.ext import Updater, Filters, CommandHandler, MessageHandler, CallbackQueryHandler, CallbackContext
from telegram import Bot
from models import *
from handlers import MyStartHandler, MyButtonHandler, MyCallbackHandler
from Jobqueue import *

import configparser
import time
import logging
import coloredlogs
logger = logging.getLogger(__name__)
coloredlogs.install(level=logging.DEBUG, logger=logger)
logging.getLogger("telegram").setLevel("ERROR")


def error(update, context):
    
    logger.info('Update "%s" caused error "%s"', update, context.error)
    logger.exception(context.error)


def main() -> None:

    config = configparser.ConfigParser()
    config.read('bot.ini')
    time.sleep(3)

    u = Updater(token=config['KEYS']['bot_api'],
                use_context=True, workers=20)
    dp = u.dispatcher
    jq = u.job_queue

    dp.add_handler(CommandHandler("start", MyStartHandler, Filters.chat_type.private,
                                  pass_args=True, run_async=True, pass_user_data=True))

    dp.add_handler(MessageHandler(Filters.chat_type.private,
                                  MyButtonHandler, pass_user_data=True, run_async=True))

    dp.add_handler(CallbackQueryHandler(
        MyCallbackHandler, pass_user_data=True, run_async=True))

    # jq.run_daily(callback=BackupJobHandler,
    #              time=datetime.time(00, 00), context=CallbackContext)

    jq.run_daily(callback=AlarmVolumeJobHandler, time=datetime.time(21, 00),
                 context=CallbackContext)
    jq.run_daily(callback=AlarmDateJobHandler, time=datetime.time(21, 30),
                 context=CallbackContext)

    jq.run_daily(callback=BackUpPanelsJobHandler, time=datetime.time(22, 30),
                 context=CallbackContext)
    # jq.run_once(BackUpPanelsJobHandler, when=2)

    dp.add_error_handler(error)

    u.start_polling()

    print(
        f"Bot {Bot(token=config['KEYS']['bot_api']).get_me().username} started!")

    u.idle()


if __name__ == '__main__':
    main()
