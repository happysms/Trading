# -*- coding: utf-8 -*-
import ccxt
import time
import datetime
import logger
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
logger = logger.make_logger("mylogger")

# binance 객체 생성
binance = ccxt.binance(config={
    'apiKey': api_key,
    'secret': secret,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'
    }
})

symbol = "ETH/USDT"
long_target, short_target, ma20_condition, before_day_condition = util.cal_target(binance, symbol)
op_mode = False
position = {
    "type": None,
    "amount": 0
}

# 잔고 조회
balance = binance.fetch_balance()
usdt = balance['total']['USDT']

eth = binance.fetch_ticker(symbol=symbol)
cur_price = eth['last']

logger.info(("long 목표가: ", long_target, "\nshort 목표가: ", short_target))

if short_target <= cur_price <= long_target:
    logger.info("프로그램 실행 시점에서 거래 가능 구간")
    op_mode = True

while True:
    try:
        now = datetime.datetime.now()

        # position 종료
        if now.hour == 8 and now.minute == 50 and (20 <= now.second < 30):
            if op_mode:
                order_id = util.exit_position(binance, symbol, position)
                op_mode = False
                position['type'] = None
                time.sleep(10)

                if order_id:
                    util.add_record_log(order_id, binance, symbol, position['type'])

        # 목표가 갱신
        if now.hour == 9 and now.minute == 0 and (20 <= now.second < 30):
            long_target, short_target, ma20_condition, before_day_condition = util.cal_target(binance, symbol)

            balance = binance.fetch_balance()
            usdt = balance['total']['USDT']
            op_mode = True
            time.sleep(10)

        # 현재가, 구매 가능 수량
        eth = binance.fetch_ticker(symbol=symbol)
        cur_price = eth['last']
        amount = util.cal_amount(usdt, cur_price, 0.99)

        if op_mode and position['type'] is None:
            position['type'], invest_amount, order_id = util.enter_position(binance, symbol, cur_price, long_target, short_target,
                                                                            amount, position, ma20_condition, before_day_condition)

            if position['type']:
                logger.info(f"{position['type']}포지션 진입, 투자금 {invest_amount}")
                time.sleep(10)
                util.add_record_log(order_id, binance, symbol, position['type'])

        time.sleep(1)
        logger.info(("long 목표가: ", long_target, "\nshort 목표가: ", short_target))

    except Exception as e:
        logger.error(e)




