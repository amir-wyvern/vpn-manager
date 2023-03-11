import requests
import json


def payment_gateway(payment_number):
    url = hub_gateway()+f"/payment/{payment_number}"
    return url


def hub_gateway():
    res = requests.get('http://GTHUB.iR/url.json')
    return json.loads(res.text)['url']


def request(merchant_code, amount, call_back_url, invoice_number=None, payer_email=None, payer_mobile=None, description=None, payerIp=None):

    data = {
        'merchantCode': merchant_code,
        'amount': amount,
        'callBackUrl': call_back_url,
        'invoiceNumber': invoice_number,
        'payerEmail': payer_email,
        'payerMobile': payer_mobile,
        'description': description,
        'payerIp': payerIp
    }
    headers = {'Content-Type': 'application/json'}
    url = hub_gateway()+"/ws/payments/request.json"
    res = requests.post(url, headers=headers, data=json.dumps(data))
    try:
        data = json.loads(res.text)
    except:
        return res.text
    return data


def verify(merchant_code, payment_number, invoice_number=None):
    data = {
        'merchantCode': merchant_code,
        'paymentNumber': payment_number,
        'invoiceNumber': invoice_number
    }
    headers = {'Content-Type': 'application/json'}
    url = hub_gateway()+"/ws/payments/verify.json"
    res = requests.post(url, headers=headers, data=json.dumps(data))
    data = json.loads(res.text)
    return data
