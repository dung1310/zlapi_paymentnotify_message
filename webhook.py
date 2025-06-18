from flask import Flask, request, jsonify
from zlapi.simple import ZaloAPI
from zlapi.models import *
from zlapi._threads import ThreadType
import json
import asyncio


app = Flask(__name__)


with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
    imei = config["imei"]
    cookies = config["cookies"]

bot = ZaloAPI("<numberPhone>", "<passwd>", imei, cookies, prefix="[prefix]")


def send_zalo_message(content, thread_id, thread_type):
    msg = Message(text=content)
    try:
        loop = asyncio.get_running_loop()
        asyncio.run_coroutine_threadsafe(bot.send_message(msg, thread_id, thread_type), loop)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(bot.send_message(msg, thread_id, thread_type))
        loop.close()


#Reciver table data for webhook from Sepay:
@app.route('/receiver', methods=['POST'])
def sepay_webhook():
    data = request.get_json()
    print('icoming webhook request')
    print('headers:', dict(request.headers))
    print('body:', data)
    if not data:
        print('no data received, passed.')
        return jsonify({'success': False, 'message': 'No data'}), 400
    gateway = data.get('gateway')
    transaction_date = data.get('transactionDate')
    account_number = data.get('accountNumber')
    sub_account = data.get('subAccount')
    transfer_type = data.get('transferType')
    transfer_amount = data.get('transferAmount', 0)
    accumulated = data.get('accumulated', 0)
    code = data.get('code')
    transaction_content = data.get('content')
    reference_number = data.get('referenceCode')
    body = data.get('description')

# Send message to Zalo account:
    try:
        message = (
            f"📢 | Thông báo giao dịch mới từ Sepay\n"
            f"💵 | Giao dịch mới từ tài khoản: {account_number}\n"
            f"📟 | Số tài khoản VA nhận: {sub_account}\n"
            f"🌐 | Cổng thanh toán: {gateway}\n"
            f"📫 | Phương thức (in/out): {transfer_type.upper()}\n"
            f"💸 | Số tiền chuyển khoản: {transfer_amount}đ\n"
            f"📝 | Nội dung chuyển khoản: {transaction_content}\n"
            f"📅 | Thời gian chuyển tiền: {transaction_date}\n"
            f"🗒 | Mã giao dịch: {reference_number}\n"
            f"Made by vdung1310, using Sepay API and ZaloAPI.\n"
        )
        thread_id = "7329548851056192815"  
        thread_type = ThreadType.GROUP  
        send_zalo_message(message, thread_id, thread_type)
        print(f'message sent into: {thread_id}!')
    except Exception as e:
        print(f'message not sent, error: {e}')
        return jsonify({'success': True, 'warning': f'message not sent, check error: {e}'}), 201

    return jsonify({'success': True}), 201

# GET methods for checking if the webhook is alive:
"""@app.route('/', methods=['GET'])
def alive():
    print('incoming GET request')
    return 'webhook is alive!', 200

@app.route('/receiver', methods=['GET'])
def receiver_alive():
    print('incoming GET request.')
    return jsonify({'success': True, 'message': 'receiver URL is alive.'}), 200"""
if __name__ == '__main__':
    app.run(port=5000, debug=True)



