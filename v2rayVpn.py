from datetimeIR import *
import datetime
import qrcode
import io
import random
import string
import uuid
import json

import config as Config

import requests
import json

import logging
def randStr(chars=string.digits*10 + string.ascii_lowercase, N=5):
    return ''.join(random.choice(chars) for _ in range(N))


def genarate_uuid():
    # uuid = randStr(N=8)+'-'+randStr(N=4)+'-'+randStr(N=4) + \
    #     '-'+randStr(N=4)+'-'+randStr(N=12)

    _uuid = uuid.uuid4()

    return _uuid


def genarate_port():
    port = random.randint(10000, 59999)
    return port


def convert_gbtobyte(gb: int):
    return int(gb*1073741824)


def convert_bytetogb(byte: int):
    return round(byte/1073741824, 4)


def login_panel(ip):
    session = requests.Session()

    url = f"http://{ip}:{Config.xui_port}/login"
    payload = f'username={Config.xui_user}&password={Config.xui_pass}'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = session.request("POST", url,  data=payload, headers=headers)

    data = json.loads(response.text)
    print(data)
    if data['success']:
        return session.cookies.get_dict()['session']


def get_cookie(ip):
    with open('xuicookies.json', 'r') as f:
        data_json = json.loads(f.read())

    if ip not in data_json:
        cookie = login_panel(ip)

        data_json[ip] = cookie
        with open('xuicookies.json', 'w') as f:
            f.write(json.dumps(data_json))

        return cookie

    return data_json[ip]


def add_vpn(name, uuid, ip, port, volume=100, expiryTime=1670665020):
    total = convert_gbtobyte(volume)

    cookie = get_cookie(ip)

    url = f"http://{ip}:{Config.xui_port}/xui/inbound/add"
    payload = f"up=0&down=0&total={total}&remark={name}&enable=true&expiryTime={expiryTime}000&autoreset=false&ipalert=false&listen=&port={port}&protocol=vless&settings=%7B%0A%20%20%22clients%22%3A%20%5B%0A%20%20%20%20%7B%0A%20%20%20%20%20%20%22id%22%3A%20%22{uuid}%22%2C%0A%20%20%20%20%20%20%22flow%22%3A%20%22xtls-rprx-direct%22%0A%20%20%20%20%7D%0A%20%20%5D%2C%0A%20%20%22decryption%22%3A%20%22none%22%2C%0A%20%20%22fallbacks%22%3A%20%5B%5D%0A%7D&streamSettings=%7B%0A%20%20%22network%22%3A%20%22ws%22%2C%0A%20%20%22security%22%3A%20%22none%22%2C%0A%20%20%22wsSettings%22%3A%20%7B%0A%20%20%20%20%22path%22%3A%20%22%2F%22%2C%0A%20%20%20%20%22headers%22%3A%20%7B%7D%0A%20%20%7D%0A%7D&sniffing=%7B%0A%20%20%22enabled%22%3A%20true%2C%0A%20%20%22destOverride%22%3A%20%5B%0A%20%20%20%20%22http%22%2C%0A%20%20%20%20%22tls%22%0A%20%20%5D%0A%7D"
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': f'session={cookie}',
        'X-Requested-With': 'XMLHttpRequest'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    data = json.loads(response.text)
    print(data)
    return data['success']


def genarate_config(user_id, ip, port, volume=0, expiryTime=0):

    name = 'U'+str(user_id)
    # ip = '5.75.247.203'
    # port = genarate_port()
    uuid = genarate_uuid()
    # print(port)
    # print(uuid)

    add_vpn(name=name, ip=ip, port=port, uuid=uuid,
            volume=volume, expiryTime=expiryTime)

    config = f"vless://{uuid}@{ip}:{port}?type=ws&path=%2F#Nextproxy_bot"

    _qrcode = genarate_qrcode(config)

    return {'config': config, 'qrcode': _qrcode}
# print(add_vpn('test'))


def genarate_qrcode(config):
    # Link for website
    input_data = config
    # Creating an instance of qrcode
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=2)
    qr.add_data(input_data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')

    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    # img.save('qrcode001.png')

    return img_byte_arr


def get_used_ports(ip):
    cookie = get_cookie(ip)

    url = f"http://{ip}:{Config.xui_port}/xui/inbound/list"
    headers = {
        'Cookie': f'session={cookie}',

    }

    response = requests.request("POST", url, headers=headers)

    data = json.loads(response.text)
    # print(data)
    ports_list = []
    for config in data['obj']:
        ports_list.append(config['port'])

    return ports_list


def get_info_config(ip, port):
    cookie = get_cookie(ip)

    url = f"http://{ip}:{Config.xui_port}/xui/inbound/list"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': f'session={cookie}',
        'X-Requested-With': 'XMLHttpRequest'

    }

    response = requests.request("POST", url, headers=headers)

    data_config = None
    data = json.loads(response.text)
    for config in data['obj']:
        if str(config['port']) == str(port):
            data_config = config
            break
    # print(data_config)
    if not data_config:
        return None

    remain_volume = convert_bytetogb(
        data_config['total']) - convert_bytetogb(data_config['up'] + data_config['down'])
    if remain_volume > 0:
        pass
    else:
        remain_volume = 0

    expire_time = data_config['expiryTime']/1000
    print(expire_time)
    expire_time = datetime.datetime.fromtimestamp(expire_time)

    total_used = data_config['up']+data_config['down']
    total_used = convert_bytetogb(total_used)

    total = convert_bytetogb(data_config['total'])

    transmission = json.loads(data_config['streamSettings'])['network']
    logging.warning(data_config)

    a = {'transmission': transmission,'protocol': data_config['protocol'],
         'total': total, 'total-used': total_used, 'expire-time': expire_time, 'remain-volume': remain_volume}

    data_config.update(a)
    return data_config


def edit_info_config(ip, port, new_uuid=False, expiryTime=None, total=None, protocol= None ,up_down=None, status=True,transmission = None):
    # print('def_edit_info_config', ip, port)

    cookie = get_cookie(ip)
    if total:
        total = convert_gbtobyte(total)

    url = f"http://{ip}:{Config.xui_port}/xui/inbound/list"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': f'session={cookie}',
        'X-Requested-With': 'XMLHttpRequest'

    }

    response = requests.request("POST", url, headers=headers, timeout=30)

    data_config = None
    data = json.loads(response.text)
    for config in data['obj']:
        if str(config['port']) == str(port):
            data_config = config
            break
    # print(data_config)
    if not data_config:
        return None

    if new_uuid:
        settings = json.loads(data_config['settings'])
        settings['clients'][0]['id'] = str(genarate_uuid())
        data_config['settings'] = json.dumps(settings)
    # print(data_config['settings'])
    if expiryTime:
        data_config['expiryTime'] = expiryTime*1000
        data_config['enable'] = True
    if total:
        data_config['total'] = total+data_config['total']
        data_config['enable'] = True

    if up_down == 0:
        data_config['up'] = 0
        data_config['down'] = 0
        data_config['enable'] = True

    if status == False:
        data_config['enable'] = False
    #
    if transmission != None:
        tmp = json.loads(data_config['streamSettings'])
        tmp['network'] = transmission
        data_config['streamSettings'] = json.dumps(tmp)
        data_config['enable'] = True

    if protocol != None:
        data_config['protocol'] = protocol
        data_config['enable'] = True

    url = f"http://{ip}:{Config.xui_port}/xui/inbound/update/{data_config['id']}"
    payload = data_config
    # print(payload)
    response = requests.request(
        "POST", url, headers=headers, data=payload, timeout=30)
    data = json.loads(response.text)
    return data['success']


def get_vlessurl(ip, port):
    data_config = get_info_config(ip, port)

    settings = json.loads(data_config['settings'])
    uuid = settings['clients'][0]['id']

    config = f"vless://{uuid}@{ip}:{port}?type=ws&path=%2F#Nextproxy_bot"

    _qrcode = genarate_qrcode(config)

    return {'config': config, 'qrcode': _qrcode}

def get_Allconfigs(ip):
    cookie = get_cookie(ip)

    url = f"http://{ip}:{Config.xui_port}/xui/inbound/list"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': f'session={cookie}',
        'X-Requested-With': 'XMLHttpRequest'

    }

    response = requests.request("POST", url, headers=headers, timeout=30)

    data = json.loads(response.text)
    config_list = []
    for config in data['obj']:
        used_volume = convert_bytetogb(config['up'] + config['down'])
        remain_volume = convert_bytetogb(
            config['total']) - used_volume
        if remain_volume > 0:
            pass
        else:
            remain_volume = 0

        expire_time = config['expiryTime']/1000
        # print(expire_time)
        expire_time = datetime.datetime.fromtimestamp(expire_time)

        port = config['port']

        settings = json.loads(config['settings'])
        uuid = settings['clients'][0]['id']

        uri = f"vless://{uuid}@{ip}:{port}?type=ws&path=%2F#Nextproxy_bot"

        config_list.append(
            {
                'name': config['remark'], 'status': config['enable'], 'port': port,
                'expire-time': expire_time, 'remain-volume': remain_volume, 'used-volume': used_volume, 'uri': uri
            }
        )
        # print(data_config)

    return config_list

def del_config(ip, port):
    cookie = get_cookie(ip)
    if not cookie:
        return

    url = f"http://{ip}:{Config.xui_port}/xui/inbound/list"
    headers = {
        'Cookie': f'session={cookie}',

    }

    response = requests.request("POST", url, headers=headers, timeout=30)

    data_config = None
    data = json.loads(response.text)
    # print(data)
    for config in data['obj']:
        if str(config['port']) == str(port):
            data_config = config
            break

    _id = data_config['id']

    url = f"http://{ip}:{Config.xui_port}/xui/inbound/del/{_id}"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': f'session={cookie}',
        'X-Requested-With': 'XMLHttpRequest'

    }

    response = requests.request("POST", url, headers=headers, timeout=30)

    data = json.loads(response.text)
    print(data)
    return data['success']