from .base import *


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

        elif B_services in self.user_data:
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

            if self.user_id in Config.Id_Admins():
                service = Services.select().where(
                    (Services.ip == ip) &
                    (Services.port == str(port))
                )
            else:
                service = Services.select().where(
                    (Services.owner == self.user) &
                    (Services.ip == ip) &
                    (Services.port == str(port))
                )
            service=service.get()

            if not service:
                text = """کانفیگ شما پیدا نشد!"""
                return self.message.reply_text(text)

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

            self.message.reply_text(text.format(
                service.name,
                service.location,
                service.protocol,
                status
            ), reply_markup=reply_markup)

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
            if lock.lockSell:
                text = """❌ بخش خرید موقتا غیرفعال می باشد لطفا بعدا تلاش کنید"""
                return self.message.reply_text(text=text)
            elif lock.lockLimitBuy:
                if not Services.select().where(Services.owner == self.user):
                    text = """❌ بخش خرید موقتا محدود می باشد لطفا بعدا تلاش کنید"""
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
            self.user_data.clear()
            self.user_data[B_services] = ""

            text = """🐉 جهت مدیریت سرویس، سرویس مورد نظر را انتخاب کنید
همچنین می توانید لینک خود را همینجا وارد کنید.
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
