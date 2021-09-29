import ccxt
import time
import datetime
import util
import argparse

parser = argparse.ArgumentParser(description='')
parser.add_argument('--api_key', metavar='api_key', required=True,
                    help='api_key')
parser.add_argument('--secret', metavar='secret', required=True,
                    help='secret')

args = parser.parse_args()
api_key = args.api_key
secret = args.secret

# binance 객체 생성
binance = ccxt.binance(config={
    'apiKey': api_key,
    'secret': secret,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'
    }
})

op_mode = False
symbol = "BTC/USDT"
long_target, short_target = util.cal_target(binance, symbol)

# 잔고 조회
balance = binance.fetch_balance()
usdt = balance['total']['USDT']

position = {
    "type": None,
    "amount": 0
}

print("long 목표가: ", long_target, "\nshort 목표가: ", short_target)

while True:
    now = datetime.datetime.now()

    # position 종료
    if now.hour == 8 and now.minute == 50 and (20 <= now.second < 30):
        if op_mode and position['type'] is not None:
            util.exit_position(binance, symbol, position)
            op_mode = False

    # 목표가 갱신
    if now.hour == 9 and now.minute == 0 and (20 <= now.second < 30):
        long_target, short_target = util.cal_target(binance, symbol)
        balance = binance.fetch_balance()
        usdt = balance['total']['USDT']
        op_mode = True
        time.sleep(10)

    # 현재가, 구매 가능 수량
    btc = binance.fetch_ticker(symbol=symbol)
    cur_price = btc['last']
    amount = util.cal_amount(usdt, cur_price, 0.95)

    if op_mode and position['type'] is None:
        util.enter_position(binance, symbol, cur_price, long_target, short_target, amount, position)

    print("long 목표가: ", long_target, "\nshort 목표가: ", short_target)
    print(now, "현재가 : ", cur_price)
    time.sleep(1)
