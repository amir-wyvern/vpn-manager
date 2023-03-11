import coloredlogs
import logging
from telegram.ext import CallbackContext
from telegram.error import Unauthorized
from telegram.constants import PARSEMODE_MARKDOWN
import datetimeIR
import datetime
from models import Services, UserData
from v2rayVpn import *
import os
import time
import config as Config
import paramiko

import configparser
config = configparser.ConfigParser()
config.read('bot.ini')

logger = logging.getLogger(__name__)
coloredlogs.install(level=logging.DEBUG, logger=logger)


class BackupJobHandler:
    def __init__(self, context):
        self.context = context
        self.bot = context.bot
        self.job = context.job

        try:
            print("BackupJob started!")
            for day in Config.days_alarm:
                self.run(day)

        except Exception as e:
            logger.exception(context.error)
            self.bot.send_message(Config.Id_AdminDebug, repr(e))

    def run(self):
        os.system("zip -r postgres-data.zip postgres-data")

        text = """بک آپ دیتابیس
{}"""
        self.bot.send_document(chat_id=356308821, document=open(
            'postgres-data.zip', 'rb'), filename="BackUp", caption=text.format(datetime.datetime.utcnow()), timeout=10)


class AlarmDateJobHandler:
    def __init__(self, context: CallbackContext):
        self.context = context
        self.bot = context.bot
        self.job = context.job

        try:
            print("AlarmDateJob started!")
            for day in [0, 1, 3, 5]:
                self.run(day)

        except Exception as e:
            logger.exception(context.error)
            self.bot.send_message(Config.Id_AdminDebug, repr(e))

    def run(self, day):
        wanted = datetimeIR.timedelta_subs(days=day)
        for location in Config.list_locations:
            ip = Config.list_locations[location]['servers'][0]['ip']
            # if ip != "s3.weserver.space":
            #     continue

            configs = get_Allconfigs(ip)

            for config in configs:
                if not config['name'].startswith('U'):
                    continue
                elif config['expire-time'].date() != wanted.date():
                    continue
                user_id = config['name'].replace('U', '')

                service = Services.select().where((Services.ip == ip) &
                                                  (Services.port == str(config['port'])))
                user = UserData.select().where((UserData.user_id == user_id))
                if service:
                    service = service.get()
                    user_id = service.owner.user_id
                elif user:
                    user = user.get()
                    user_id = user.user_id
                else:
                    continue

                if day == 0:
                    text = """‼️ کاربر گرامی زمان اشتراک سرویس "{}" به پایان رسید ✅
    """.format(service.name)
                else:
                    text = """‼️ کاربر گرامی مدت زمان اشتراک سرویس "{}"، {} روز دیگر به پایان میرسد.
                    
جهت جلوگیری از قطعی اشتراک لطفاً در اسرع وقت اشتراک‌تان را تمدید کنید ♻️
""".format(service.name, day)

                try:
                    self.bot.send_message(
                        chat_id=user_id, text=text, parse_mode=PARSEMODE_MARKDOWN)
                except Unauthorized:
                    pass

                # try:
                #     SendAdminsText(self.bot, text=text.format(service.name))
                # except:
                #     pass

                time.sleep(0.2)


class AlarmVolumeJobHandler:
    def __init__(self, context: CallbackContext):
        self.context = context
        self.bot = context.bot
        self.job = context.job

        try:
            print("AlarmVolumeJob started!")
            self.run()

        except Exception as e:
            logger.exception(context.error)
            self.bot.send_message(Config.Id_AdminDebug, repr(e))

    def run(self):
        for location in Config.list_locations:
            ip = Config.list_locations[location]['servers'][0]['ip']
            # if ip != "s3.weserver.space":
            #     continue

            configs = get_Allconfigs(ip)

            for config in configs:
                if not config['name'].startswith('U'):
                    continue
                user_id = config['name'].replace('U', '')

                service = Services.select().where((Services.ip == ip) &
                                                  (Services.port == str(config['port'])))
                user = UserData.select().where((UserData.user_id == user_id))
                if service:
                    service = service.get()
                    user_id = service.owner.user_id
                elif user:
                    user = user.get()
                    user_id = user.user_id
                else:
                    continue

                if 0 < config['remain-volume'] < 1:
                    text = """‼️ کاربر گرامی از حجم اشتراک سرویس "{}" کمتر از 1 گیگابایت باقی مانده است ✅

    ⚠️ در صورت اتمام حجم و عدم تمدید، اشتراک‌تان به صورت کامل حذف می‌گردد. جهت تمدید می‌توانید از دکمه های ربات اقدام نمایید"""
                elif config['remain-volume'] == 0:
                    text = """‼️ کاربر گرامی حجم اشتراک سرویس "{}" به پایان رسیده است ✅
    """
                else:
                    continue

                try:
                    self.bot.send_message(
                        chat_id=user_id, text=text.format(service.name), parse_mode=PARSEMODE_MARKDOWN)
                except Unauthorized:
                    pass

                # try:
                #     SendAdminsText(self.bot, text=text.format(service.name))
                # except:
                #     pass

                time.sleep(0.2)


class BackUpPanelsJobHandler:
    def __init__(self, context: CallbackContext):
        self.context = context
        self.bot = context.bot
        self.job = context.job

        try:

            print("BackUpPanelsJob started!")
            self.run()

        except Exception as e:
            logger.exception(context.error)
            self.bot.send_message(Config.Id_AdminDebug, repr(e))

    def run(self):
        for server in Config.list_servers:
            ip = server['ip']
            password = server['password']
            port = server['port']

            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(ip, username='root', port=port,
                           password=password, timeout=10)

            ftp_client = client.open_sftp()
            ftp_client.get("/etc/x-ui/x-ui.db",
                           "./backups/x-ui.db")
            ftp_client.close()

            self.bot.send_document(Config.Id_Admins()[2], document=open(
                "./backups/x-ui.db", 'rb'), caption=f"Backup: {ip}")

            os.remove("./backups/x-ui.db")

        text = "📮 از همه سرور ها بک اپ گرفته شد"
        try:
            SendAdminsText(self.bot, text=text)
        except:
            pass


def SendAdminsText(bot, text, reply_markup=None, parse_mode=None):
    for user_id in Config.Id_Admins():

        try:
            bot.send_message(chat_id=user_id, text=text,
                             reply_markup=reply_markup, parse_mode=parse_mode)
        except:
            pass

        time.sleep(0.1)
