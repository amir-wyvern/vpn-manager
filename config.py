import configparser
config = configparser.ConfigParser()
config.read('bot.ini')

DB = 'botsdb'

Id_AdminDebug = config['SETTINGS']['Id_adminDebug']


def Id_Admins():
    return [int(_) for _ in config['ADMINS'].values()]


limit_list = 30


list_locations = {

    "🇮🇷 1": {
        'servers': [{'ip': 's1.weserver.space', 'ip-iran': "s2.weserver.space", 'start-port': 490, 'end-port': 500}]
    },

    "🇮🇷 2": {
        'servers': [{'ip': 's3.weserver.space', 'ip-iran': "s4.weserver.space", 'start-port': 2527, 'end-port': 2550}]
    },
    "🇮🇷 3": {
        'servers': [{'ip': 's5.weserver.space', 'ip-iran': "s6.weserver.space", 'start-port': 3422, 'end-port': 3471}]
    },
    "🇮🇷 4": {
        'servers': [{'ip': 's7.weserver.space', 'ip-iran': "s8.weserver.space", 'start-port': 4475, 'end-port': 4495}]
    },
    "🇮🇷 5": {
        'servers': [{'ip': 's9.weserver.space', 'ip-iran': "s10.weserver.space", 'start-port': 715, 'end-port': 730}]
    },
    "🇮🇷 6": {
        'servers': [{'ip': 's11.weserver.space', 'ip-iran': "s12.weserver.space", 'start-port': 670, 'end-port': 680}]
    },
    "🇮🇷 7": {
        'servers': [{'ip': 's13.weserver.space', 'ip-iran': "s14.weserver.space", 'start-port': 680, 'end-port': 700}]
    },
    "🇮🇷 8": {
        'servers': [{'ip': 's15.weserver.space', 'ip-iran': "s16.weserver.space", 'start-port': 760, 'end-port': 780}]
    },
    "🇮🇷 9": {
        'servers': [{'ip': 's17.weserver.space', 'ip-iran': "s18.weserver.space", 'start-port': 6899, 'end-port': 6910}]
    },
    "🇮🇷 10": {
        'servers': [{'ip': 's19.weserver.space', 'ip-iran': "s20.weserver.space", 'start-port': 2500, 'end-port': 2515}]
    },
    "🇮🇷 11": {
        'servers': [{'ip': 's21.weserver.space', 'ip-iran': "s22.weserver.space", 'start-port': 9324, 'end-port': 9371}]
    },
        "🇮🇷 12": {
        'servers': [{'ip': 'finland.irannewvps.xyz', 'ip-iran': "finir.irannewvps.xyz", 'start-port': 1151, 'end-port': 1255}]
    },
    "🇮🇷 13": {
        'servers': [{'ip': 'serv101.irannewvps.xyz', 'ip-iran': "server301.irannewvps.xyz", 'start-port': 3000, 'end-port': 3010}]
    },
        "🇮🇷 14": {
        'servers': [{'ip': 'lv101.irannewvps.xyz', 'ip-iran': "lv102.irannewvps.xyz", 'start-port': 286, 'end-port': 296}]
    },
     "🇮🇷 15": {
        'servers': [{'ip': 'lol103.irannewvps.xyz', 'ip-iran': "lol104.irannewvps.xyz", 'start-port': 489, 'end-port': 499}]
    }
    
}

list_buy_vpn = {
    "2 کاربره 25 گیگ 1 ماهه 40.000 تومان": {'pay': 40000, 'month': 1, 'volume': 25},
    "4 کاربره 25 گیگ 1 ماهه 52.000 تومان": {'pay': 52000, 'month': 1, 'volume': 25},
    "2 کاربره 50 گیگ 1 ماهه 70.000 تومان": {'pay': 70000, 'month': 1, 'volume': 50},
    "4 کاربره 50 گیگ 1 ماهه 82.000 تومان": {'pay': 82000, 'month': 1, 'volume': 50},
    "2 کاربره 100 گیگ 1 ماهه 100,000 تومان": {'pay': 100000, 'month': 1, 'volume': 100},
    "4 کاربره 100 گیگ 1 ماهه 112,000 تومان": {'pay': 112000, 'month': 1, 'volume': 100},
    "2 کاربره 200 گیگ 1 ماهه 180,000 تومان": {'pay': 180000, 'month': 1, 'volume': 200},
    "4 کاربره 200 گیگ 1 ماهه 192,000 تومان": {'pay': 192000, 'month': 1, 'volume': 200},

}

xui_user = "admin"
xui_pass = "admin"
xui_port = "9390/bot"


list_servers = [
    {'ip': '217.30.10.234', 'password': '09198553323', 'port': 22},
    {'ip': '185.73.203.182', 'password': 'rjtAAC558', 'port': 22},
    {'ip': '91.132.167.61', 'password': 'stqaXCCE2570a', 'port': 8989},
    {'ip': '91.107.186.77', 'password': 'sjaJvpPiibUvt7i3xqnpa', 'port': 22},
    {'ip': '165.227.236.20', 'password': 'fAya3323farzada', 'port': 22},
    {'ip': '217.30.10.213', 'password': 'Ry7GvdQ3e5jF8WM8x2a', 'port': 22},
    {'ip': '217.30.10.212', 'password': 'i0oVuy03C6KdSR6Ot9a', 'port': 22},
    {'ip': '138.68.156.226', 'password': 'fAya3323farzada', 'port': 22},
    {'ip': '95.217.183.3', 'password': '7TUsUpTXFrArq9MV9vuKa', 'port': 22},
    {'ip': '91.201.65.155', 'password': '11JjAMioa7vHX546cG', 'port': 22},
    {'ip': '109.122.208.113', 'password': '09198553323', 'port': 22},
    {'ip': '95.217.183.3', 'password': '7TUsUpTXFrArq9MV9vuK', 'port': 22},
    {'ip': '185.246.153.178', 'password': 'zhWs6Bb5P2T94xsKQ9', 'port': 8989},
    {'ip': '91.244.197.180', 'password': 'faya8553323', 'port': 22},
    
    # {'ip': '11', 'password': 'admin', 'port': 22},
]
