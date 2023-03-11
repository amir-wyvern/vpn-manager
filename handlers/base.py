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

B_ask_capacity = "استعلام ظرفیت📊"
B_next_service = ">>"
B_before_service = "<<"
B_service_editName = "📝تغییر نام سرویس"
B_service_details = "📜مشخصات سرویس"
B_service_link = "🔗لینک مستقیم"
B_service_internalLink = "🇮🇷 لینک داخلی"
B_service_changeprotcol = "تغییر پروتکل"
B_service_changelink = "🚫تغییر لینک اتصال"
B_service_continuation = "🔃تمدید"
B_delete_service = "حذف سرویس 🗑"

B_changeprotcol_vmessTcp = "vmess + tcp"
B_changeprotcol_vmessWc = "vmess + wc"
B_changeprotcol_vlessTcp = "vless + tcp"
B_changeprotcol_vlessWs = "vless + wc"

B_manage_members = "مدیریت اعضا👨‍👩‍👧‍👧"
B_lastMembers = "کاربران اخیر 🚻"
B_report_members = "گزارش کاربران 🗂"
B_sendMembers = "ارسال پیام به کاربران 📮"
B_backup = "بک آپ 📥"
B_lock_sell = "قفل فروش"
B_lock_limit_buy = "قفل محدودیت خرید"

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


class Lock:
    lockSell = False
    lockLimitBuy = False


lock = Lock()


def RK_panel():
    countMember = len(UserData.select())

    # global lockSell, lockLimitBuy
    if lock.lockSell:
        lock_sell = "✅"
    else:
        lock_sell = "❌"

    if lock.lockLimitBuy:
        lock_limit_buy = "✅"
    else:
        lock_limit_buy = "❌"

    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton(str(countMember), callback_data="x"), InlineKeyboardButton("تعداد اعضا 👥", callback_data="x")],
         [InlineKeyboardButton(
             B_backup, callback_data=B_backup)],
         [InlineKeyboardButton(
             B_lock_sell+f" {lock_sell}", callback_data=B_lock_sell)],
         [InlineKeyboardButton(
             B_lock_limit_buy+f" {lock_limit_buy}", callback_data=B_lock_limit_buy)],
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
