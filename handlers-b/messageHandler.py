from telegram import (
    InlineKeyboardButton, Message, ReplyKeyboardMarkup,
    KeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardRemove, Update
)
from telegram.ext import CallbackContext
from telegram.error import BadRequest, Unauthorized
from telegram.utils import helpers

from telegram.constants import PARSEMODE_MARKDOWN

import datetimeIR
from v2rayVpn import *

from utils import *
from models import *
import config as Config

import coloredlogs
import logging
import datetime
import re

import sys
import os
import datetime
import random
import time
import ast

import configparser
config = configparser.ConfigParser()
config.read('bot.ini')


sys.path.append('..')
logger = logging.getLogger(__name__)
coloredlogs.install(level=logging.DEBUG, logger=logger)

B_panel = "پنل مدیریت 🛠"
B_buy_vpn = "🌟 خرید سرویس جدید"
B_services = "🐉 سرویس ها"
B_connect_android = "🔌 اتصال در اندروید"
B_connect_ios = "🔌 اتصال در ios"
B_support = "💬 پشتیبانی"
B_see_configDetails = "مشاهده حجم و زمان باقی مانده"
B_wallet = "کیف پول"
PASSWORDS = []

lockSell = False


def RK_start(admin=False):

    strt_list = [[B_buy_vpn, B_services], [B_connect_android, B_connect_ios],
                 [B_support], [B_see_configDetails, B_wallet]]

    if admin:
        strt_list.append([B_panel])

    reply_markup = ReplyKeyboardMarkup(strt_list,
                                       resize_keyboard=True)

    return reply_markup


class MyStartHandler:
    def __init__(self, update: Update, context: CallbackContext):
        self.update = update
        self.context = context
        self.bot = self.context.bot
        self.message: Message = self.update.message
        self.user_id = self.message.from_user.id
        self.name = self.message.from_user.first_name
        self.payload = self.context.args
        self.user_data = context.user_data

        try:
            self.run()
            logger.info("bot started.")

        except Exception as e:
            logger.exception(f"User: {self.user_id}, {context.error}")
            self.bot.send_message(Config.Id_AdminDebug, repr(e))
            raise e

    def run(self):
        if self.checkSpam() == False:
            print("spaming...")
            return
        self.user_data['time'] = datetime.datetime.now()
        if not checkJoin(self.bot, self.user_id):
            return

        self.user = get_and_updateUser(self.user_id, self.name)

        text = f"""خوش اومدی!
چه کاری برات انجام بدم؟

برای خرید سرویس جدید پرسرعت و بدون قطعی روی دکمه '{B_buy_vpn}' کلیک کنید👇🏻"""

        if self.user_id in Config.Id_Admins():
            reply_markup = RK_start(admin=True)
        else:
            reply_markup = RK_start()

        self.message.reply_text(
            text=text, reply_markup=reply_markup)

#         text = """کانال اطلاع رسانی:
# @irFvpn"""
#         self.message.reply_text(
#             text=text)

    def checkSpam(self):
        now = datetime.datetime.now()
        try:
            before = self.user_data['time']
        except:
            return True

        timedelta = now-before
        # print(timedelta)

        if timedelta.total_seconds() < 0.6:
            return False
        else:
            return True


class MyMessageHandler:
    def __init__(self, update: Update, context: CallbackContext):
        self.update = update
        self.context = context
        self.bot = self.context.bot
        self.message: Message = self.update.message
        self.user_id = self.message.from_user.id
        self.name = self.message.from_user.first_name
        self.user_data = context.user_data
        self.user = get_and_updateUser(self.user_id, self.name)

        try:
            self.__set_text()
            if self.user_id in Config.Id_Admins():
                self.run_admin()
            self.run()

        except Exception as e:
            logger.exception(context.error)
            self.bot.send_message(Config.Id_AdminDebug, repr(e))
            raise e

    def run_admin(self):
        if B_sendMembers in self.user_data:
            self.user_data.clear()
            text = "درحال ارسال لطفا منتظر بمانید...⏰"
            self.bot.send_message(chat_id=self.user_id, text=text)

            users = UserData.select()
            text = f"""پیام همگانی :

{self.message.text}"""
            for user in users:
                try:
                    self.bot.send_message(chat_id=user.user_id, text=text)
                    time.sleep(0.2)
                except:
                    pass

            text = "پیام شما به کل اعضا ارسال شد.✅"
            self.bot.send_message(chat_id=self.user_id, text=text)

        elif (B_manage_members in self.user_data) and re.fullmatch("\d+", self.message.text):
            if UserData.select().where(UserData.user_id == self.message.text).exists():

                self.user_data.clear()
                user = UserData.get(UserData.user_id == self.message.text)

                reply_markup = RK_member(int(self.message.text))

                text = """کاربر با کد کاربری\a[[{}](tg://user?id={})]
                
موجودی : {}"""
                self.bot.send_message(chat_id=self.user_id, text=text.format(
                    self.message.text, self.message.text, user.wallet), reply_markup=reply_markup, parse_mode=PARSEMODE_MARKDOWN)

        elif B_sendto_user in self.user_data:
            user_id = self.user_data[B_sendto_user]
            self.user_data.clear()

            try:
                text = """پیام پشتیبانی :

{}"""
                self.bot.send_message(
                    chat_id=user_id, text=text.format(self.message.text))

                text = """پیام شما ارسال شد.✅"""
                self.bot.send_message(
                    chat_id=self.user_id, text=text)
            except:
                text = "⚠️متاسفانه کاربر ربات بلاک کرده."
                self.bot.send_message(chat_id=self.user_id, text=text)

        elif B_add_balance in self.user_data:
            user_id = self.user_data[B_add_balance]
            user = UserData.get(UserData.user_id == user_id)
            self.user_data.clear()

            user.set_wallet(user.wallet+int(self.message.text))

            text = """موجودی شما {} افزایش یافت."""
            self.bot.send_message(
                chat_id=user_id, text=text.format(self.message.text))

            text = """موجودی کاربر {} افزایش یافت."""
            self.bot.send_message(
                chat_id=self.user_id, text=text.format(self.message.text))

    def run(self):
        if not checkJoin(self.bot, self.user_id):
            return

        if B_see_configDetails in self.user_data:
            self.user_data.clear()
            if (not self.message.text.startswith('vless://')) or not re.search(':\d+', self.message.text):
                text = "فرمت کانفیگ ارسالی صحیح نیست ‼️"
                return self.message.reply_text(text)

            ip = re.search(
                "@[\w\.]+", self.message.text).group().replace("@", '')
            uuid = re.search(
                "//[\w-]+", self.message.text).group().replace("//", '')
            port = re.search(
                ":\d+", self.message.text).group().replace(":", '')

            info = get_info_config(ip=ip, port=port)
            if not info:
                text = """کانفیگ شما پیدا نشد!"""
                return self.message.reply_text(text)

            remain_volume = info['remain-volume']
            expire_time = info['expire-time']
            timedelta = convert_timedelta(
                expire_time-datetime.datetime.utcnow())

            text = """کانفیگ شما پیدا شد.
حجم باقی مانده : {}
زمان مانده : {} روز {} ساعت {} دقیقه"""

            self.message.reply_text(text.format(
                remain_volume, timedelta['days'], timedelta['hours'], timedelta['minutes']))

        elif B_service_editName in self.user_data:
            service_id = self.user_data[B_service_editName]
            service = Services.get(Services.id == service_id)

            try:
                self.bot.delete_message(
                    chat_id=self.user_id, message_id=self.message.message_id)
            except BadRequest:
                pass

            if not re.search('\w{3,20}', self.text):
                text = """❌ نام ارسالی باید بین 5 تا 16 کاراکتر باشد
"""
                return self.message.reply_text(text)

            service.set_name(self.text)

            text = """✅ تغییر نام سرویس با موفقیت انجام شد"""
            self.message.reply_text(text)
            self.user_data.clear()

    def __set_text(self):
        if self.message.text:
            self.text = self.message.text
        else:
            self.text = ""

    def warn_text(self):
        text = "⚠️ لطفا متن وارد کنید ."
        self.message.reply_text(text=text)


class MyButtonHandler:
    def __init__(self, update: Update, context: CallbackContext):
        self.update = update
        self.context = context
        self.message: Message = self.update.message
        self.text = self.message.text
        self.bot = self.context.bot
        self.user_id = self.message.from_user.id
        self.name = self.message.from_user.first_name
        self.user_data = context.user_data
        self.job_queue = context.job_queue
        self.user = get_and_updateUser(self.user_id, self.name)

        try:
            self.__set_text()
            logger.info("get message.")
            self.run()

        except Exception as e:
            logger.exception(context.error)
            self.bot.send_message(Config.Id_AdminDebug, repr(e))
            raise e

    def run(self):
        if self.checkSpam() == False:
            print("spaming...")
            return
        self.user_data['time'] = datetime.datetime.now()
        if not checkJoin(self.bot, self.user_id):
            return

        if self.text == B_panel and (self.user_id in Config.Id_Admins()):
            self.user_data.clear()

            reply_markup = RK_panel()
            text = "🔻🔻🔻 به کنترل پنل خوش آمدید. 🔻🔻🔻"
            self.message.reply_text(text=text, reply_markup=reply_markup)

        elif self.text == B_buy_vpn:
            if lockSell:
                text = """❌ بخش خرید موقتا غیرفعال می باشد لطفا بعدا تلاش کنید"""
                return self.message.reply_text(text=text)

            self.user_data.clear()
            now = datetime.datetime.utcnow()
            # if self.user.expire_vpn_datetime and self.user.expire_vpn_datetime > now:
            #     text = """شما سرویس فعال دارین!"""
            #     self.message.reply_text(text=text)
            #     return

            text = """
لطفا یکی از کشور های زیر را انتخاب کنید👇"""

            list_key = []
            for location in Config.list_locations.keys():
                list_key.append(
                    [InlineKeyboardButton(location, callback_data='buy'+location)])
            list_key.append([InlineKeyboardButton(
                B_ask_capacity, callback_data=B_ask_capacity)])
            reply_markup = InlineKeyboardMarkup(list_key)
            self.message.reply_text(text=text, reply_markup=reply_markup)

        elif self.text == B_services:

            text = """🐉 جهت مدیریت سرویس، سرویس مورد نظر را انتخاب کنید

⚠️ این بخش مخصوص مشتریان فعلی ما میباشد ، اگر قصد تهیه کانفیگ را دارین لطفا از طریق دکمه خرید اقدام کنید.
"""
            self.message.reply_text(
                text=text, reply_markup=RK_services(self.user))

        elif self.text == B_connect_android:
            text = """⚡️ جهت اتصال در اندروید از نرم افزار زیر استفاده کنید:

https://t.me/fdbot_Ch/2244
"""

            self.message.reply_text(text)

        elif self.text == B_connect_ios:
            text = """⚡️ جهت اتصال در ios از نرم افزار زیر استفاده کنید:

https://t.me/fdbot_Ch/2245
"""
            self.message.reply_text(text)

        elif self.text == B_support:
            text = """به پشتیبانی خوش اومدی☺️

مشکل یا سوال خودتو در قالب یک پیام ارسال کن و کمی به ما مهلت بده تا برسی کنیم، بعضی وقتا ممکنه یکم دیر جواب بدیم ولی نگران نباش تا نهایتا 72 ساعت ما مشکلتو حل میکنیم!

@nextvpnsupport"""
            self.message.reply_text(text)

        elif self.text == B_see_configDetails:
            self.user_data[B_see_configDetails] = ""
            text = """لطفا مانند نمونه کانفیگ که قبلا از ربات دریافت کرده اید را ارسال کنید.

vless://ec9c61d4-8843-4f6f-d026-b178c47ae3d4@188.678.64.2:103/?type=ws&security=none&path=%2F#Test

⚠️ این بخش مخصوص مشتریان فعلی ما میباشد ، اگر قصد تهیه کانفیگ را دارین لطفا از طریق دکمه خرید اقدام کنید."""
            self.message.reply_text(text)

        elif self.text == B_wallet:
            text = """موجودی شما : {}"""
            self.message.reply_text(text.format(self.user.wallet))
        else:
            MyMessageHandler(self.update, self.context)

    def checkSpam(self):
        now = datetime.datetime.now()
        try:
            before = self.user_data['time']
        except:
            return True

        timedelta = now-before

        if timedelta.total_seconds() < 0.6:
            return False
        else:
            return True

    def __set_text(self):
        if self.message.text:
            self.text = self.message.text
        else:
            self.text = ""


B_ask_capacity = "استعلام ظرفیت📊"
B_next_service = ">>"
B_before_service = "<<"
B_service_editName = "📝تغییر نام سرویس"
B_service_details = "📜مشخصات سرویس"
B_service_link = "🔗لینک مستقیم"
B_service_internalLink = "🇮🇷 لینک داخلی"
B_service_changelink = "🚫تغییر لینک اتصال"
B_service_continuation = "🔃تمدید"
B_delete_service = "حذف سرویس 🗑"

B_manage_members = "مدیریت اعضا👨‍👩‍👧‍👧"
B_lastMembers = "کاربران اخیر 🚻"
B_report_members = "گزارش کاربران 🗂"
B_sendMembers = "ارسال پیام به کاربران 📮"
B_backup = "بک آپ 📥"
B_lock_sell = "قفل فروش"

B_back = "برگشت 🔙"

B_next = "➡"
B_before = "⬅️"
B_add_balance = "افزودن موجودی"
B_set_subscription = "اضافه کردن اشتراک"
B_del_user = "حذف کلی اطلاعات کاربر 🗑"
B_delete = "بله حذف شود"
B_last_seen = "آخرین بازدید👁‍🗨 : {}\n{}"
B_sendto_user = "ارسال پیام به کاربر 📮"

B_use_balance = "استفاده از کیف پول"


class MyCallbackHandler:
    def __init__(self, update: Update, context: CallbackContext):
        self.update = update
        self.context = context
        self.bot = self.context.bot
        self.query = self.update.callback_query
        self.message: Message = self.query.message
        self.user_id = self.query.from_user.id
        self.name = self.query.from_user.first_name
        self.data = self.query.data
        self.user_data = context.user_data
        self.user = get_and_updateUser(self.user_id, self.name)

        try:
            logger.info("get callBack.")
            if self.user_id in Config.Id_Admins():
                self.admins()

            self.run()

            self.bot.answer_callback_query(self.query.id)

        # except BadRequest:
        #     text = "خطا!"
        #     self.bot.answer_callback_query(self.query.id, text)

        except Exception as e:
            logger.exception(context.error)
            self.bot.send_message(Config.Id_AdminDebug, repr(e))

    def admins(self):
        if self.data == B_lastMembers:

            users = UserData.select().order_by(UserData.id)
            list_users = ""
            for user in users[-30:]:
                list_users += f"\n[{user.name}](tg://user?id={user.user_id})"
                print(list_users)

            text = """30 کاربر اخیر عضو شده در ربات 📈
{}            """
            reply_markup = InlineKeyboardMarkup(
                [[InlineKeyboardButton(B_panel, callback_data=B_panel)]])
            self.edit_message(text=text.format(list_users),
                              reply_markup=reply_markup, parse_mode='markdown')

        elif (self.data == B_sendMembers):
            self.user_data.clear()
            self.user_data[self.data] = ""

            if (self.data == B_sendMembers):
                text = "پیام خود را بنویسید✍🏻."
            else:
                text = "پیام خود را ارسال کنید✍🏻."
            reply_markup = InlineKeyboardMarkup(
                [[InlineKeyboardButton(B_panel, callback_data=B_panel)]])
            self.edit_message(text=text, reply_markup=reply_markup)

        elif self.data == B_panel and (self.user_id in Config.Id_Admins()):
            self.user_data.clear()

            reply_markup = RK_panel()
            text = "🔻🔻🔻 به کنترل پنل خوش آمدید. 🔻🔻🔻"
            self.edit_message(text=text, reply_markup=reply_markup)

        elif self.data == B_manage_members:
            self.user_data.clear()
            self.user_data[B_manage_members] = ""

            reply_markup = RK_members()
            text = """🔻🔻🔻 مدیریت کاربران 🔻🔻🔻"""
            self.edit_message(text=text, reply_markup=reply_markup)

        elif B_before in self.data:
            less = int(self.data.replace(B_before, ""))
            high = less
            print(less, high)

            if less <= 0:
                return

            less = high-Config.limit_list

            text = "🔻🔻🔻 مدیریت کاربران 🔻🔻🔻"
            try:
                self.edit_message(
                    text=text, reply_markup=RK_members(less, high))
            except BadRequest:
                pass

        elif B_next in self.data:
            high = int(self.data.replace(B_next, ""))
            less = high
            print(less, high)

            if less >= len(UserData.select()):
                return

            high = high+Config.limit_list

            text = "🔻🔻🔻 مدیریت کاربران 🔻🔻🔻"
            try:
                self.edit_message(
                    text=text, reply_markup=RK_members(less, high))
            except BadRequest:
                pass

        elif re.fullmatch("\d+", self.data):
            if UserData.select().where(UserData.user_id == self.data).exists() == True:
                user = UserData.get(UserData.user_id == self.data)
                self.user_data.clear()

                text = """کاربر با کد کاربری\a[|{}|](tg://user?id={})
                
موجودی : {}
"""
                self.edit_message(text=text.format(self.data, self.data, user.wallet),
                                  reply_markup=RK_member(self.data), parse_mode=PARSEMODE_MARKDOWN)

        elif B_set_subscription in self.data:
            user_id = self.data.replace(B_set_subscription, "")
            user = UserData.get(UserData.user_id == user_id)

            self.user_data[B_set_subscription] = user_id

            text = """
لطفا یکی از کشور های زیر را انتخاب کنید👇"""

            list_key = []
            for location in Config.list_locations.keys():
                list_key.append(
                    [InlineKeyboardButton(location, callback_data='buy'+location)])
            list_key.append([InlineKeyboardButton(
                "کاربر 🔙", callback_data=user_id)])
            reply_markup = InlineKeyboardMarkup(list_key)
            self.edit_message(text=text, reply_markup=reply_markup)

        elif ('buy' in self.data) and B_set_subscription in self.user_data:
            user_id = self.user_data[B_set_subscription]
            location = self.data.replace('buy', '')
            self.user_data['location'] = location

            text = """
لطفا یکی از پلن های زیر را انتخاب کنید👇"""

            list_key = []
            for plan in Config.list_buy_vpn.keys():
                list_key.append(
                    [InlineKeyboardButton(plan, callback_data=plan)])
            list_key.append([InlineKeyboardButton(
                "کاربر 🔙", callback_data=user_id)])
            reply_markup = InlineKeyboardMarkup(list_key)
            self.edit_message(text=text, reply_markup=reply_markup)

        elif (self.data in Config.list_buy_vpn.keys()) and B_set_subscription in self.user_data:
            plan_pay = Config.list_buy_vpn[self.data]
            try:
                location = self.user_data['location']
            except:
                text = """❌ این پیام منقصی شده است لطفا دوباره به این بخش مراجعه کنید"""
                self.bot.answer_callback_query(
                    self.query.id, text, show_alert=True)
                return self.delete()

            user_id = self.user_data[B_set_subscription]
            user = UserData.get(UserData.user_id == user_id)

            self.user_data.clear()

            rand_panel = random.choice(
                Config.list_locations[location]['servers'])
            ip = rand_panel['ip']
            all_ports = list(
                range(rand_panel['start-port'], rand_panel['end-port']+1))
            used_ports = get_used_ports(ip)
            available_ports = list(set(all_ports)-set(used_ports))
            if len(available_ports) == 0:
                text = """سرویس موجود نمی باشد!"""
                return self.bot.answer_callback_query(
                    self.query.id, text, show_alert=True)

            port = available_ports[0]
            month = plan_pay['month']

            # create vpn
            days = 30*month
            volume = plan_pay['volume']
            expire_time = datetimeIR.timedelta_subs(days)
            vpn = genarate_config(
                user_id=user_id, ip=ip, port=port, volume=volume, expiryTime=int(expire_time.timestamp()))

            services = Services.select().where(Services.owner == user)
            if not services:
                _id = 1
            else:
                _id = len(services)+1

            name = f"سرویس {_id}"

            service = Services.create(
                owner=user, name=name, plan=self.data, location=location, ip=ip, port=port, expire_datetime=expire_time
            )

            caption = f"""
لینک مستقیم :
`{vpn['config']}`

لینک داخلی :
`{vpn['config'].replace(ip,rand_panel['ip-iran'])}`
"""
            self.bot.send_photo(
                chat_id=user_id,
                photo=vpn['qrcode'], caption=caption, parse_mode=PARSEMODE_MARKDOWN
            )

            text = """سرویس برای کاربر اضافه شد"""
            self.bot.answer_callback_query(
                self.query.id, text, show_alert=True)

        elif B_sendto_user in self.data:
            user_id = self.data.replace(B_sendto_user, "")
            self.user_data[B_sendto_user] = user_id

            reply_markup = InlineKeyboardMarkup(
                [[InlineKeyboardButton("کاربر 🔙", callback_data=user_id)]])

            text = """پیام خود را بنویسید✍🏻."""
            self.edit_message(text=text, reply_markup=reply_markup)

        elif self.data == B_backup:
            os.system("zip -r postgres-data.zip postgres-data")

            text = """بک آپ دیتابیس
{}"""
            self.bot.send_document(chat_id=self.user_id, document=open(
                'postgres-data.zip', 'rb'), filename="BackUp", caption=text.format(datetime.datetime.utcnow()), timeout=10)

        elif B_add_balance in self.data:
            user_id = self.data.replace(B_add_balance, "")
            self.user_data[B_add_balance] = user_id

            reply_markup = InlineKeyboardMarkup(
                [[InlineKeyboardButton("کاربر 🔙", callback_data=user_id)]])

            text = """لطفا موجودی را به تومان وارد کنید✍🏻."""
            self.edit_message(text=text, reply_markup=reply_markup)

        elif self.data == B_lock_sell:
            global lockSell
            lockSell = not lockSell

            reply_markup = RK_panel()
            text = "🔻🔻🔻 به کنترل پنل خوش آمدید. 🔻🔻🔻"
            self.edit_message(text=text, reply_markup=reply_markup)

    def run(self):
        if self.data == B_check:
            if checkJoin(self.bot, self.user_id, False):
                self.delete()
                text = f"""خوش اومدی!
چه کاری برات انجام بدم؟

برای خرید سرویس جدید پرسرعت و بدون قطعی روی دکمه '{B_buy_vpn}' کلیک کنید👇🏻"""
                self.message.reply_text(text)
            else:
                self.bot.answer_callback_query(
                    self.query.id, "⭕️لطفا عضو کانال شوید.⭕️", show_alert=True)

        elif ('buy' in self.data) and B_set_subscription not in self.user_data:
            location = self.data.replace('buy', '')
            self.user_data['location'] = location

            text = """
لطفا یکی از پلن های زیر را انتخاب کنید👇"""

            list_key = []
            for plan in Config.list_buy_vpn.keys():
                list_key.append(
                    [InlineKeyboardButton(plan, callback_data=plan)])
            reply_markup = InlineKeyboardMarkup(list_key)
            self.edit_message(text=text, reply_markup=reply_markup)

        elif (self.data in Config.list_buy_vpn.keys()) and B_set_subscription not in self.user_data:
            plan_pay = Config.list_buy_vpn[self.data]
            self.user_data[B_use_balance] = self.data
            try:
                location = self.user_data['location']
            except:
                text = """❌ این پیام منقصی شده است لطفا دوباره به این بخش مراجعه کنید"""
                self.bot.answer_callback_query(
                    self.query.id, text, show_alert=True)
                return self.delete()

            rand_panel = random.choice(
                Config.list_locations[location]['servers'])
            ip = rand_panel['ip']
            all_ports = list(
                range(rand_panel['start-port'], rand_panel['end-port']+1))
            used_ports = get_used_ports(ip)
            available_ports = list(set(all_ports)-set(used_ports))

            if (len(available_ports) == 0) and B_service_continuation not in self.user_data:
                text = """سرویس موجود نمی باشد!"""
                return self.bot.answer_callback_query(
                    self.query.id, text, show_alert=True)

            continuation = None
            if B_service_continuation in self.user_data:
                continuation = self.user_data[B_service_continuation]

            zarinpal_paying = ZarinpalPaying.create(
                owner=self.user, continuation=continuation)
            url_pay = config["SETTINGS"]["url_zarinpal"] + \
                f"id={zarinpal_paying}&membership=" + \
                str(list(Config.list_buy_vpn).index(self.data)) +\
                "&location=" +\
                str(list(Config.list_locations).index(location))

            print(zarinpal_paying, str(
                list(Config.list_buy_vpn).index(self.data)))

            text = """
▪️ پرداخت از طریق درگاه بانکی شتابی بصورت کاملا امن انجام میگیرد.

⚠️ هنگام پرداخت حتما باید فیلترشکن خود را خاموش کنید ❗️

محصول : '{}'

لینک خرید به مبلغ {:,} تومان برای شما ساخته شد 👇
            """
            reply_markup = InlineKeyboardMarkup(
                [[InlineKeyboardButton(
                    "ورود به درگاه پرداخت", url=url_pay)],
                    [InlineKeyboardButton(
                        B_use_balance, callback_data=B_use_balance)]]
            )
            self.message.reply_text(
                text=text.format(self.data, plan_pay['pay']), reply_markup=reply_markup)

        elif self.data == B_use_balance:
            try:
                location = self.user_data['location']
            except:
                text = """❌ این پیام منقصی شده است لطفا دوباره به این بخش مراجعه کنید"""
                self.bot.answer_callback_query(
                    self.query.id, text, show_alert=True)
                return self.delete()

            plan = self.user_data[B_use_balance]
            plan_pay = Config.list_buy_vpn[self.user_data[B_use_balance]]
            amount = plan_pay['pay']

            month = plan_pay['month']
            days = 30*month
            volume = plan_pay['volume']

            if self.user.wallet < amount:
                text = """موجودی شما کافی نیست!"""
                self.bot.answer_callback_query(
                    self.query.id, text, show_alert=True)
                return

            if B_service_continuation in self.user_data:
                continuation = self.user_data[B_service_continuation]

                service = Services.get(
                    Services.id == continuation)

                total = volume

                date_time = None
                if datetime.datetime.utcnow() < service.expire_datetime:
                    date_time = service.expire_datetime
                expire_time = timedelta_subs(days, date_time)

                edit_info_config(
                    ip=service.ip, port=service.port, expiryTime=int(expire_time.timestamp()), total=total, up_down=0)

                service.set_expire_datetime(expire_time)
                service.set_status(True)

                text = """✅ سرویس "{}" با موفقیت تمدید شد"""
                self.bot.send_message(chat_id=self.user_id,
                                      text=text.format(service.name))

            else:
                # create vpn
                rand_panel = random.choice(
                    Config.list_locations[location]['servers'])
                ip = rand_panel['ip']
                all_ports = list(
                    range(rand_panel['start-port'], rand_panel['end-port']+1))
                used_ports = get_used_ports(ip)
                available_ports = list(set(all_ports)-set(used_ports))

                port = available_ports[0]

                expire_time = timedelta_subs(days)

                self.user_data.clear()
                self.delete()
                self.user.set_wallet(self.user.wallet-amount)
                text = f"""{amount} تومن از کیف پول شما برداشت شد."""
                self.bot.answer_callback_query(
                    self.query.id, text, show_alert=True)

                vpn = genarate_config(
                    user_id=self.user_id, ip=ip, port=port, volume=volume, expiryTime=int(expire_time.timestamp()))

                services = Services.select().where(Services.owner == self.user)
                if not services:
                    _id = 1
                else:
                    _id = len(services)+1

                name = f"سرویس {_id}"

                service = Services.create(
                    owner=self.user, name=name, plan=plan, location=location, ip=ip, port=port, expire_datetime=expire_time
                )

                caption = f"""
    لینک مستقیم :
    `{vpn['config']}`

    لینک داخلی :
    `{vpn['config'].replace(ip,rand_panel['ip-iran'])}`
    """
                self.bot.send_photo(
                    chat_id=self.user_id,
                    photo=vpn['qrcode'], caption=caption, parse_mode=PARSEMODE_MARKDOWN
                )

            bot_info = self.bot.get_me()

            text = """خرید از ربات {}
اسم کاربر : {}
ایدی کاربر : {}
برداشت از کیف پول
مبلغ : {}

🆔 @{}"""
            self.bot.send_message(
                chat_id=Config.Id_Admins()[2],
                text=text.format(
                    bot_info.first_name,
                    self.name,
                    self.user_id,
                    amount,
                    bot_info.username))

            self.user_data.clear()

        elif 'see' in self.data:
            service_id = int(self.data.replace('see', ''))
            service = Services.get(Services.id == service_id)

            text = """
🌿 نام سرویس: {}
‏🇺🇳 لوکیشن: ‏{}
🔥 پروتکل سرویس: {}
💹 وضعیت: {}

📌 شما میتوانید با استفاده از دکمه های زیر سرویس خود را مدیریت کنید"""

            status = 'فعال'
            if not service.status:
                status = 'غیر فعال'

            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            B_service_details, callback_data=B_service_details+str(service.id)), InlineKeyboardButton(
                            B_service_editName, callback_data=B_service_editName+str(service.id))
                    ],
                    [
                        InlineKeyboardButton(
                            B_service_link, callback_data=B_service_link+str(service.id)),
                        InlineKeyboardButton(
                            B_service_internalLink, callback_data=B_service_internalLink+str(service.id))
                    ],
                    [InlineKeyboardButton(
                        B_service_changelink, callback_data=B_service_changelink+str(service.id))],
                    [InlineKeyboardButton(
                        B_delete_service, callback_data=B_delete_service+str(service.id))],
                    [InlineKeyboardButton(
                        B_service_continuation, callback_data=B_service_continuation+str(service.id))],
                    [InlineKeyboardButton(
                        B_back, callback_data=B_services)]
                ]
            )

            if self.message.photo:
                self.delete()
                self.message.reply_text(text.format(
                    service.name,
                    service.location,
                    service.protocol,
                    status
                ), reply_markup=reply_markup)
            else:
                try:
                    self.edit_message(text.format(
                        service.name,
                        service.location,
                        service.protocol,
                        status
                    ), reply_markup=reply_markup)
                except BadRequest:
                    pass

        elif self.data == B_services:
            self.user_data.clear()

            text = """🐉 جهت مدیریت سرویس، سرویس مورد نظر را انتخاب کنید
"""
            self.edit_message(text=text, reply_markup=RK_services(self.user))

        elif B_service_details in self.data:
            service_id = int(self.data.replace(B_service_details, ''))
            service = Services.get(Services.id == service_id)

            info = get_info_config(ip=service.ip, port=service.port)
            if not info:
                text = """سرویس در سرور پیدا نشد!"""
                return self.bot.answer_callback_query(
                    self.query.id, text, show_alert=True)

            datetime_now = datetime.datetime.utcnow()
            if info['expire-time'] < datetime_now:
                service.set_status(False)
            expire = (info['expire-time']-datetime_now)
            expire = convert_timedelta(expire)

            remain = info['total']-info['total-used']
            if remain <= 0:
                remain = 0
                service.set_status(False)
            else:
                remain = round(remain, 4)

            # day_expire = expire['days']

            days_expire = expire["days"]
            hours_expire = expire["hours"]
            if (expire["days"] < 0) or expire["hours"] < 0:
                days_expire = 0
                hours_expire = 0

            if info['total'] == 300.0:
                days = 90
            else:
                days = 30

            buy_datetime = timedelta_subs(
                days=-days, date_time=info['expire-time'])
            buy_datetime = persian_conventer(buy_datetime)

            text = """
🌿 نام سرویس: {}
🧾 نام پلن: {}
‏🇺🇳 لوکیشن: {}
🔥 پروتکل سرویس: {}
⏳ اعتبار: {} روز و {} ساعت دیگر
♾ آستانه مصرف: {} گیگابایت
📊 حجم مصرف شده: {} گیگابایت
🧮 حجم باقی مانده: {} گیگابایت

📅 تاریخ خرید/تمدید: {}
🕘 ساعت خرید/تمدید: {}
"""

            reply_markup = InlineKeyboardMarkup(
                [[InlineKeyboardButton(
                    B_back, callback_data=f'see{service.id}')]]
            )

            self.edit_message(text.format(
                service.name,
                service.plan,
                service.location,
                service.protocol,
                days_expire, hours_expire,
                info['total'],
                info['total-used'],
                remain,
                buy_datetime.strftime('%Y/%m/%d'),
                buy_datetime.strftime('%H:%M:%S')
            ), reply_markup=reply_markup)

        elif B_service_link in self.data:
            service_id = int(self.data.replace(B_service_link, ''))
            service = Services.get(Services.id == service_id)

            try:
                vpn = get_vlessurl(ip=service.ip, port=service.port)
            except:
                text = """سرویس با اختلال مواجه شده است ، لطفا بعدا سعی کنید!"""
                return self.bot.answer_callback_query(
                    self.query.id, text, show_alert=True)

            reply_markup = InlineKeyboardMarkup(
                [[InlineKeyboardButton(
                    B_back, callback_data=f'see{service.id}')]]
            )

            self.delete()
            self.bot.send_photo(
                chat_id=self.user_id,
                photo=vpn['qrcode'], caption=f"`{vpn['config']}`", reply_markup=reply_markup, parse_mode=PARSEMODE_MARKDOWN
            )

        elif B_service_internalLink in self.data:
            service_id = int(self.data.replace(B_service_internalLink, ''))
            service = Services.get(Services.id == service_id)

            try:
                vpn = get_vlessurl(ip=service.ip, port=service.port)
            except:
                text = """سرویس با اختلال مواجه شده است ، لطفا بعدا سعی کنید!"""
                return self.bot.answer_callback_query(
                    self.query.id, text, show_alert=True)

            reply_markup = InlineKeyboardMarkup(
                [[InlineKeyboardButton(
                    B_back, callback_data=f'see{service.id}')]]
            )

            self.delete()
            caption = f"""
`{vpn['config'].replace(service.ip,Config.list_locations[service.location]['servers'][0]['ip-iran'])}`

⁉️ لینک داخلی چیست؟!
لینک داخلی یا نیم بها برای اتصال به اینترنت آزاد در زمان داخلی شدن اینترنت می باشد، همچین این لینک نسبت به لینک مستقیم از سرعت بیشتری (خصوصا نت همراه) برخوردار است.
تعرفه دانلود لینک داخلی نیم بها می باشد.♨️"""
            self.bot.send_photo(
                chat_id=self.user_id,
                photo=vpn['qrcode'], caption=caption, reply_markup=reply_markup, parse_mode=PARSEMODE_MARKDOWN
            )

        elif B_service_changelink in self.data:
            service_id = int(self.data.replace(B_service_changelink, ''))
            service = Services.get(Services.id == service_id)
            info = edit_info_config(
                ip=service.ip, port=service.port, new_uuid=True)
            if not info:
                text = "خطا!"
            else:
                text = """لینک سرویس شما تغییر یافت و تمامی افراد متصل قطع شدند."""
            self.bot.answer_callback_query(
                self.query.id, text, show_alert=True)

        elif B_delete_service in self.data:
            service_id = int(self.data.replace(B_delete_service, ''))
            service = Services.get(Services.id == service_id)
            del_config(
                ip=service.ip, port=service.port)
            service.delete_instance()
            self.delete()
            text = """سرویس {} حذف شد."""
            self.bot.answer_callback_query(
                self.query.id, text.format(service.name), show_alert=True)

        elif B_service_continuation in self.data:
            self.user_data.clear()
            service_id = int(self.data.replace(B_service_continuation, ''))
            service = Services.get(Services.id == service_id)

            info = get_info_config(ip=service.ip, port=service.port)
            if not info:
                text = """سرویس در سرور پیدا نشد!"""
                return self.bot.answer_callback_query(
                    self.query.id, text, show_alert=True)

            self.user_data['location'] = service.location

            self.user_data[B_service_continuation] = service_id

            text = """
لطفا یکی از پلن های زیر را انتخاب کنید👇"""

            list_key = []
            for plan in Config.list_buy_vpn.keys():
                list_key.append(
                    [InlineKeyboardButton(plan, callback_data=plan)])
            list_key.append([InlineKeyboardButton(
                B_back, callback_data=f'see{service.id}')])
            reply_markup = InlineKeyboardMarkup(list_key)

            self.edit_message(text=text, reply_markup=reply_markup)

        elif B_service_editName in self.data:
            service_id = int(self.data.replace(B_service_editName, ''))

            self.user_data[B_service_editName] = service_id

            reply_markup = InlineKeyboardMarkup(
                [[InlineKeyboardButton(
                    B_back, callback_data=f'see{service_id}')]]
            )

            text = """📝 جهت تغییر نام سرویس، نام مورد نظر خود را ارسال کنید

📌 مثال: Test
"""

            self.edit_message(text, reply_markup=reply_markup)

        elif B_before_service in self.data:
            less = int(self.data.replace(B_before_service, ""))
            high = less

            if less <= 0:
                return

            less = high-Config.limit_list

            text = """🐉 جهت مدیریت سرویس، سرویس مورد نظر را انتخاب کنید
"""
            try:
                self.edit_message(
                    text=text, reply_markup=RK_services(self.user, less, high))
            except BadRequest:
                pass

        elif B_next_service in self.data:
            high = int(self.data.replace(B_next_service, ""))
            less = high

            if less >= len(UserData.select()):
                return

            high = high+Config.limit_list

            text = """🐉 جهت مدیریت سرویس، سرویس مورد نظر را انتخاب کنید
"""
            try:
                self.edit_message(
                    text=text, reply_markup=RK_services(self.user, less, high))
            except BadRequest:
                pass

        elif self.data == B_ask_capacity:
            text = """لطفا منتظر بمانیید..."""
            self.bot.answer_callback_query(
                self.query.id, text, show_alert=True)

            text_locations = ""
            for location, value in Config.list_locations.items():
                server = value['servers'][0]
                all_ports = list(
                    range(server['start-port'], server['end-port']+1))
                used_ports = get_used_ports(server['ip'])
                available_ports = list(set(all_ports)-set(used_ports))
                if len(available_ports) == 0:
                    text_locations += f"{location} : تکمیل ❌\n"
                else:
                    text_locations += f"{location} : {len(available_ports)} ✅\n"

            text = """استعلام موجودی سرورها :
            
{}"""
            try:
                self.edit_message(
                    text=text.format(text_locations))
            except BadRequest:
                pass

    def edit_message(self, text: str, reply_markup: InlineKeyboardMarkup = None, parse_mode=None):
        self.bot.edit_message_text(
            chat_id=self.user_id, message_id=self.message.message_id, text=text, reply_markup=reply_markup, parse_mode=parse_mode)

    def delete(self):
        self.bot.delete_message(
            chat_id=self.query.message.chat_id, message_id=self.query.message.message_id)


def RK_panel():
    countMember = len(UserData.select())

    global lockSell
    if lockSell:
        lock_sell = "✅"
    else:
        lock_sell = "❌"

    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton(str(countMember), callback_data="x"), InlineKeyboardButton("تعداد اعضا 👥", callback_data="x")],
         [InlineKeyboardButton(
             B_backup, callback_data=B_backup)],
         [InlineKeyboardButton(
             B_lock_sell+f" {lock_sell}", callback_data=B_lock_sell)],
         [InlineKeyboardButton(
             B_manage_members, callback_data=B_manage_members)],
         [InlineKeyboardButton(
             B_lastMembers, callback_data=B_lastMembers)],
         [InlineKeyboardButton(
             B_sendMembers, callback_data=B_sendMembers)],
         ]
    )
    return reply_markup


def RK_members(less=0, high=Config.limit_list):
    users = UserData.select().order_by(UserData.id)
    list_members = []

    for user in users[less:high]:
        name = user.name
        list_members.append([InlineKeyboardButton(
            "{} 👀".format(name), callback_data=user.user_id)])

    list_members.append([InlineKeyboardButton(
        B_before, callback_data=B_before+str(less)), InlineKeyboardButton(B_next, callback_data=B_next+str(high))])

    list_members.append([InlineKeyboardButton(B_panel, callback_data=B_panel)])

    reply_markup = InlineKeyboardMarkup(list_members)

    return reply_markup


def RK_member(user_id):
    user = UserData.get(UserData.user_id == user_id)

    reply_markup = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(
                B_add_balance, callback_data=B_add_balance+str(user_id))],
            [InlineKeyboardButton(
                B_set_subscription, callback_data=B_set_subscription+str(user_id))],
            [InlineKeyboardButton(
             B_sendto_user, callback_data=B_sendto_user+str(user_id))],
            [InlineKeyboardButton("پنل مدیریت 🔙", callback_data=B_panel), InlineKeyboardButton("مدیریت اعضا 🔙", callback_data=B_manage_members)]])

    return reply_markup


def RK_services(user, less=0, high=Config.limit_list):
    services = Services.select().where(
        Services.owner == user).order_by(Services.id)
    list_key = []
    for service in services[less:high]:
        status = ""
        if not service.status:
            status = "(غیر فعال)"
        list_key.append(
            [InlineKeyboardButton(f"{list(services).index(service)+1}) {service.name} / {service.location} {status}", callback_data=f'see{service.id}')])

    list_key.append([InlineKeyboardButton(
        B_before_service, callback_data=B_before_service+str(less)), InlineKeyboardButton(B_next_service, callback_data=B_next_service+str(high))])

    reply_markup = InlineKeyboardMarkup(list_key)

    return reply_markup


B_check = "عضو شدم ✅"


def checkJoin(bot, user_id, send_link=True):
    # return True
    channel = int(config['CHANNELS']['channel1'])
    status_one = bot.get_chat_member(chat_id=channel,
                                     user_id=user_id).status or None
    username = bot.get_chat(channel).username
    # print(status_one)
    # return True
    status = ['creator', 'member', 'administrator']
    if (status_one in status):
        return True
    else:
        if send_link == False:
            return False

        text = """خوش آمدید.🌹
جهت حمایت از اما لطفا داخل کانال اصلی ما عضو شوید.

@{}
@{}

بعد از عضویت روی دکمه【{}】کلیک کنید."""

        B_joinChannel1 = "JOIN CHANNEL"

        username_channel = bot.get_chat(channel).username

        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(
            B_joinChannel1, url=f"https://t.me/{username_channel}")],
            [InlineKeyboardButton(B_check, callback_data=B_check)]])

        bot.send_message(chat_id=user_id, text=text.format(
            username,
            username,
            B_check), reply_markup=reply_markup)

        return False
