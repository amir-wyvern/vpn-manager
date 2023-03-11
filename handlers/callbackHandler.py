from .base import *


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

            less = high - Config.limit_list

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

            high = high + Config.limit_list

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
                    [InlineKeyboardButton(location, callback_data='buy' + location)])
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
                range(rand_panel['start-port'], rand_panel['end-port'] + 1))
            used_ports = get_used_ports(ip)
            available_ports = list(set(all_ports) - set(used_ports))
            if len(available_ports) == 0:
                text = """سرویس موجود نمی باشد!"""
                return self.bot.answer_callback_query(
                    self.query.id, text, show_alert=True)

            port = available_ports[0]
            month = plan_pay['month']

            # create vpn
            days = 30 * month
            volume = plan_pay['volume']
            expire_time = datetimeIR.timedelta_subs(days)
            vpn = genarate_config(
                user_id=user_id, ip=ip, port=port, volume=volume, expiryTime=int(expire_time.timestamp()))

            services = Services.select().where(Services.owner == user)
            if not services:
                _id = 1
            else:
                _id = len(services) + 1

            name = f"سرویس {_id}"

            service = Services.create(
                owner=user, name=name, plan=self.data, location=location, ip=ip, port=port, expire_datetime=expire_time
            )

            caption = f"""
لینک مستقیم :
`{vpn['config']}`

لینک داخلی :
`{vpn['config'].replace(ip, rand_panel['ip-iran'])}`
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
            # os.system("zip -r postgres-data.zip postgres-data")

            text = """بک آپ دیتابیس
{}"""
            self.bot.send_document(chat_id=self.user_id, document=open(
                './postgres-data.zip', 'rb'), filename="BackUp", caption=text.format(datetime.datetime.utcnow()))

        elif B_add_balance in self.data:
            user_id = self.data.replace(B_add_balance, "")
            self.user_data[B_add_balance] = user_id

            reply_markup = InlineKeyboardMarkup(
                [[InlineKeyboardButton("کاربر 🔙", callback_data=user_id)]])

            text = """لطفا موجودی را به تومان وارد کنید✍🏻."""
            self.edit_message(text=text, reply_markup=reply_markup)

        elif self.data == B_lock_sell:
            # global lockSell
            lock.lockSell = not lock.lockSell

            reply_markup = RK_panel()
            text = "🔻🔻🔻 به کنترل پنل خوش آمدید. 🔻🔻🔻"
            self.edit_message(text=text, reply_markup=reply_markup)

        elif self.data == B_lock_limit_buy:
            # global lockLimitBuy
            lock.lockLimitBuy = not lock.lockLimitBuy

            reply_markup = RK_panel()
            text = "🔻🔻🔻 به کنترل پنل خوش آمدید. 🔻🔻🔻"
            self.edit_message(text=text, reply_markup=reply_markup)

    def run(self):
        if self.data == B_check:
            if checkJoin(self.bot, self.user_id, False):
                self.delete()
                text = f"""خوش اومدی!
چه کاری برات انجام بدم؟

برای خرید vpn پرسرعت و بدون قطعی روی دکمه '{B_buy_vpn}' کلیک کنید👇🏻"""
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
                range(rand_panel['start-port'], rand_panel['end-port'] + 1))
            used_ports = get_used_ports(ip)
            available_ports = list(set(all_ports) - set(used_ports))

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
                      str(list(Config.list_buy_vpn).index(self.data)) + \
                      "&location=" + \
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
            days = 30 * month
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
                    range(rand_panel['start-port'], rand_panel['end-port'] + 1))
                used_ports = get_used_ports(ip)
                available_ports = list(set(all_ports) - set(used_ports))

                port = available_ports[0]

                expire_time = timedelta_subs(days)

                self.user_data.clear()
                self.delete()
                self.user.set_wallet(self.user.wallet - amount)
                text = f"""{amount} تومن از کیف پول شما برداشت شد."""
                self.bot.answer_callback_query(
                    self.query.id, text, show_alert=True)

                vpn = genarate_config(
                    user_id=self.user_id, ip=ip, port=port, volume=volume, expiryTime=int(expire_time.timestamp()))

                services = Services.select().where(Services.owner == self.user)
                if not services:
                    _id = 1
                else:
                    _id = len(services) + 1

                name = f"سرویس {_id}"

                service = Services.create(
                    owner=self.user, name=name, plan=plan, location=location, ip=ip, port=port,
                    expire_datetime=expire_time
                )

                caption = f"""
    لینک مستقیم :
    `{vpn['config']}`

    لینک داخلی :
    `{vpn['config'].replace(ip, rand_panel['ip-iran'])}`
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
                            B_service_details, callback_data=B_service_details + str(service.id)), InlineKeyboardButton(
                        B_service_editName, callback_data=B_service_editName + str(service.id))
                    ],
                    [
                        InlineKeyboardButton(
                            B_service_link, callback_data=B_service_link + str(service.id)),
                        InlineKeyboardButton(
                            B_service_internalLink, callback_data=B_service_internalLink + str(service.id))
                    ],
                    [InlineKeyboardButton(
                        B_service_changeprotcol, callback_data=B_service_changeprotcol + str(service.id))],
                    [InlineKeyboardButton(
                        B_service_changelink, callback_data=B_service_changelink + str(service.id))],
                    [InlineKeyboardButton(
                        B_delete_service, callback_data=B_delete_service + str(service.id))],
                    [InlineKeyboardButton(
                        B_service_continuation, callback_data=B_service_continuation + str(service.id))],
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
            self.user_data[B_services] = ""

            text = """🐉 جهت مدیریت سرویس، سرویس مورد نظر را انتخاب کنید
همچنین می توانید لینک خود را همینجا وارد کنید.
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
            expire = (info['expire-time'] - datetime_now)
            expire = convert_timedelta(expire)

            remain = info['total'] - info['total-used']
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
                photo=vpn['qrcode'], caption=f"`{vpn['config']}`", reply_markup=reply_markup,
                parse_mode=PARSEMODE_MARKDOWN
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
`{vpn['config'].replace(service.ip, Config.list_locations[service.location]['servers'][0]['ip-iran'])}`

⁉️ لینک داخلی چیست؟!
لینک داخلی یا نیم بها برای اتصال به اینترنت آزاد در زمان داخلی شدن اینترنت می باشد، همچین این لینک نسبت به لینک مستقیم از سرعت بیشتری (خصوصا نت همراه) برخوردار است.
تعرفه دانلود لینک داخلی نیم بها می باشد.♨️"""
            self.bot.send_photo(
                chat_id=self.user_id,
                photo=vpn['qrcode'], caption=caption, reply_markup=reply_markup, parse_mode=PARSEMODE_MARKDOWN
            )
        elif B_service_changeprotcol in self.data:
            service_id = int(self.data.replace(B_service_changeprotcol, ''))
            service = Services.get(Services.id == service_id)

            info = get_info_config(ip=service.ip, port=service.port)
            if not info:
                text = """سرویس در سرور پیدا نشد!"""
                return self.bot.answer_callback_query(
                    self.query.id, text, show_alert=True)

            # datetime_now = datetime.datetime.utcnow()
            # if info['expire-time'] < datetime_now:
            #     service.set_status(False)
            # expire = (info['expire-time'] - datetime_now)
            # expire = convert_timedelta(expire)
            #
            # remain = info['total'] - info['total-used']
            # if remain <= 0:
            #     remain = 0
            #     service.set_status(False)
            # else:
            #     remain = round(remain, 4)
            #
            # # day_expire = expire['days']
            #
            # days_expire = expire["days"]
            # hours_expire = expire["hours"]
            # if (expire["days"] < 0) or expire["hours"] < 0:
            #     days_expire = 0
            #     hours_expire = 0
            #
            # if info['total'] == 300.0:
            #     days = 90
            # else:
            #     days = 30
            #
            # buy_datetime = timedelta_subs(
            #     days=-days, date_time=info['expire-time'])
            # buy_datetime = persian_conventer(buy_datetime)

            text = """
* توجه داشته باشید که پس از  تغییر پروتکل لینک اتصال فعلی شما باطل شده و لینک جدید دردسترس خواهد بود
پروتکل فعلی : {}
یکی از پروتکل های زیر را جهت تغییر سرویستان انتخاب کنید:
"""

            reply_markup = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton(
                        B_changeprotcol_vmessTcp, callback_data="change_protocol" + B_changeprotcol_vmessTcp + str(service.id)),
                        InlineKeyboardButton(
                            B_changeprotcol_vlessTcp, callback_data="change_protocol" + B_changeprotcol_vlessTcp + str(service.id))
                    ],
                    [
                        InlineKeyboardButton(
                            B_changeprotcol_vmessWc, callback_data="change_protocol" + B_changeprotcol_vmessWc + str(service.id)),
                        InlineKeyboardButton(
                            B_changeprotcol_vlessWs, callback_data="change_protocol" + B_changeprotcol_vlessWs + str(service.id))
                    ],
                    [InlineKeyboardButton(
                        B_back, callback_data=f'see{service.id}')]]
            )

            self.edit_message(text.format(
                f'{service.protocol}+{service.transmission}'
            ), reply_markup=reply_markup)

        elif "change_protocol" in self.data:
            service_id = None
            newtransmission = None
            newprotcol = None
            if B_changeprotcol_vmessTcp in self.data:
                service_id = int(self.data.replace("change_protocol" + B_changeprotcol_vmessTcp, ''))
                newtransmission = "tcp"
                newprotcol = "vmess"
            if B_changeprotcol_vlessTcp in self.data:
                service_id = int(self.data.replace("change_protocol" + B_changeprotcol_vlessTcp, ''))
                newtransmission = "tcp"
                newprotcol = "vless"
            if B_changeprotcol_vmessWc in self.data:
                service_id = int(self.data.replace("change_protocol" + B_changeprotcol_vmessWc, ''))
                newtransmission = "ws"
                newprotcol = "vmess"
            if B_changeprotcol_vlessWs in self.data:
                service_id = int(self.data.replace("change_protocol" + B_changeprotcol_vlessWs, ''))
                newtransmission = "ws"
                newprotcol = "vless"

            if service_id != None:
                service = Services.get(Services.id == service_id)
                info = edit_info_config(
                    ip=service.ip, port=service.port, transmission = newtransmission ,protocol = newprotcol)

            if not info:
                text = "خطا!"
            else:
                text = """✅ سرویس "{}" با موفقیت بروز شد"""

            service.set_protocol(newprotcol)
            service.set_transmission(newtransmission)

            self.bot.send_message(chat_id=self.user_id,
                                  text=text.format(service.name))
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
            try:
                del_config(
                    ip=service.ip, port=service.port)
            except:
                pass
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

            less = high - Config.limit_list

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

            high = high + Config.limit_list

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
                    range(server['start-port'], server['end-port'] + 1))
                used_ports = get_used_ports(server['ip'])
                available_ports = list(set(all_ports) - set(used_ports))
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
            chat_id=self.user_id, message_id=self.message.message_id, text=text, reply_markup=reply_markup,
            parse_mode=parse_mode)

    def delete(self):
        self.bot.delete_message(
            chat_id=self.query.message.chat_id, message_id=self.query.message.message_id)
