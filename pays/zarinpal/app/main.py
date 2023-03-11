import configparser
from models import ZarinpalPaying, Payments,Services
from flask import Flask, url_for, redirect, request, render_template
from suds.client import Client

from telegram import Bot
from telegram.constants import PARSEMODE_MARKDOWN

import random
import logging
import coloredlogs
import datetime
import config as Config
from datetimeIR import *
from v2rayVpn import *

config = configparser.ConfigParser()
config.read('bot.ini')

logger = logging.getLogger(__name__)
coloredlogs.install(level=logging.DEBUG, logger=logger)

bot = Bot(token=config['KEYS']['bot_api'])

app = Flask(__name__)

MMERCHANT_ID = '916e905e-d3a7-11e9-b4a3-000c295eb8fc'  # Required
ZARINPAL_WEBSERVICE = 'https://www.zarinpal.com/pg/services/WebGate/wsdl'  # Required
amount = 1000  # Amount will be based on Toman  Required
description = u'خرید'  # Required
email = ''  # Optional
mobile = ''  # Optional
# /request?id=


@app.route('/')
def test():
    # return render_template('home.html')
    return redirect("https://t.me/"+bot.get_me().username)
    return "every thing is good."


@app.route('/request/')
def send_request():
    if 'id' not in request.args:
        return "Error: No id field provided."
    elif 'membership' not in request.args:
        return "Error: No membership field provided."
    elif 'location' not in request.args:
        return "Error: No location field provided."

    id = int(request.args['id'])
    if not ZarinpalPaying.select().where(ZarinpalPaying.id == id).exists():
        return "Error: No id field provided."
    membership = int(request.args['membership'])
    if membership not in range(0, len(Config.list_buy_vpn)):
        return "Error: No membership field provided."
    location = int(request.args['location'])
    if location not in range(0, len(Config.list_locations)):
        return "Error: No location field provided."

    # print(id, membership)

    key = list(Config.list_buy_vpn)[int(membership)]
    amount = Config.list_buy_vpn[key]['pay']

    zarinpal_paying = ZarinpalPaying.get(ZarinpalPaying.id == id)


####################################
    # amount = 100

    client = Client(ZARINPAL_WEBSERVICE)
    result = client.service.PaymentRequest(MMERCHANT_ID,
                                           amount,
                                           description,
                                           email,
                                           mobile,
                                           str(url_for('verify', _external=True, id=id, membership=membership, location=location)))
    print(str(url_for('verify', _external=True, id=id,
          membership=membership, location=location)))
    if result.Status == 100:
        logger.debug("zarin link created.")
        return redirect('https://www.zarinpal.com/pg/StartPay/' + result.Authority)
    else:
        return 'Error'


@app.route('/verify/', methods=['GET', 'POST'])
def verify():
    client = Client(ZARINPAL_WEBSERVICE)
    if request.args.get('Status') == 'OK':
        id = int(request.args['id'])
        membership = int(request.args['membership'])
        location = int(request.args['location'])

        key = list(Config.list_buy_vpn)[int(membership)]
        location = list(Config.list_locations)[location]
        amount = Config.list_buy_vpn[key]['pay']
        month = Config.list_buy_vpn[key]['month']

        zarinpal_paying = ZarinpalPaying.get(ZarinpalPaying.id == id)

        owner = zarinpal_paying.owner
        user_id = zarinpal_paying.owner.user_id

        date_time = datetime.datetime.utcnow()
        # expire_datetime = date_time + datetime.timedelta(expire_days)

####################################
        # amount = 100

        result = client.service.PaymentVerification(MMERCHANT_ID,
                                                    request.args['Authority'],
                                                    amount)

        if result.Status == 100:
            logger.debug('Transaction success. RefID: ' + str(result.RefID))

            membership = f'{month} ماهه'
            Payments.create(owner=zarinpal_paying.owner, ref_id=result.RefID, amount=amount, membership=membership,
                            datetime=date_time)

            bot_info = bot.get_me()

            text = """✅ تراکنش با موفقیت انجام شد

🎫 محصول: '{}'
💳 کد پیگیری شاپرک: {}
💰 مبلغ: {:,} تومان

🆔 @{}"""
            bot.send_message(chat_id=user_id,
                             text=text.format(
                                 key,
                                 result.RefID,
                                 amount,
                                 bot_info.username))

            text = """خرید از ربات {}
اسم کاربر : {}
ایدی کاربر : {}
مبلغ : {}

🆔 @{}"""
            bot.send_message(chat_id=Config.Id_Admins()[2],
                             text=text.format(
                                 bot_info.first_name,
                                 owner.name,
                                 user_id,
                                 amount,
                                 bot_info.username))

            # create vpn
            plan_pay = Config.list_buy_vpn[key]
            days = 30*month
            volume = plan_pay['volume']

            if zarinpal_paying.continuation:
                service = Services.get(
                    Services.id == zarinpal_paying.continuation)

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
                bot.send_message(chat_id=user_id,
                                 text=text.format(service.name))

            else:
                rand_panel = random.choice(
                    Config.list_locations[location]['servers'])
                ip = rand_panel['ip']
                all_ports = list(
                    range(rand_panel['start-port'], rand_panel['end-port']+1))
                used_ports = get_used_ports(ip)
                available_ports = list(set(all_ports)-set(used_ports))

                port = available_ports[0]

                expire_time = timedelta_subs(days)

                vpn = genarate_config(
                    user_id=f'{user_id}', ip=ip, port=port, volume=volume, expiryTime=int(expire_time.timestamp()))
                caption = f"""
    لینک مستقیم :
    `{vpn['config']}`

    لینک داخلی :
    `{vpn['config'].replace(ip,rand_panel['ip-iran'])}`
    """
                bot.send_photo(
                    chat_id=user_id,
                    photo=vpn['qrcode'], caption=caption, parse_mode=PARSEMODE_MARKDOWN
                )

                services = Services.select().where(Services.owner == zarinpal_paying.owner)
                if not services:
                    _id = 1
                else:
                    _id = len(services)+1

                name = f"سرویس {_id}"

                service = Services.create(
                    owner=zarinpal_paying.owner, name=name,
                    location=location, ip=ip, port=port, expire_datetime=expire_time
                )

                zarinpal_paying.owner.set_expire_vpn_datetime(expire_time)

            zarinpal_paying.delete_instance()

            print('Transaction success. RefID: ' + str(result.RefID))
            return 'Transaction success. RefID: ' + str(result.RefID)
            return redirect("https://t.me/"+bot.get_me().username)
        elif result.Status == 101:
            return 'Transaction submitted : ' + str(result.Status)
        else:
            return 'Transaction failed. Status: ' + str(result.Status)
    else:
        return 'Transaction failed or canceled by user'


if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host='0.0.0.0', debug=True, port=80)
