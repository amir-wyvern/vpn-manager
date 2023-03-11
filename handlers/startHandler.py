from .base import *

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

