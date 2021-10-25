import math
import pandas as pd
from datetime import datetime
from db import MariaDB


def cal_target(exchange, symbol):
    data = exchange.fetch_ohlcv(
        symbol=symbol,
        timeframe='1d',
        since=None,
        limit=21
    )

    df = pd.DataFrame(
        data=data,
        columns=['datetime', 'open', 'high', 'low', 'close', 'volume']
    )

    df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
    df.set_index('datetime', inplace=True)
    yesterday = df.iloc[-2]
    today = df.iloc[-1]

    ma20 = df['close'].rolling(window=20).mean().iloc[-1]
    is_rise = False
    before_day_condition = (yesterday['close'] / yesterday['open']) < 1.08

    if today['open'] > ma20:
        is_rise = True

    long_target = today['open'] + (yesterday['high'] - yesterday['low']) * 0.4
    short_target = today['open'] - (yesterday['high'] - yesterday['low']) * 0.4

    return long_target, short_target, is_rise, before_day_condition


def cal_amount(usdt_balance, cur_price, portion):
    usdt_trade = usdt_balance * portion
    amount = math.floor((usdt_trade * 1000000) / cur_price) / 1000000
    return amount


def enter_position(exchange, symbol, cur_price, long_target, short_target, amount, position, ma20_condition, before_day_condition):
    order = None

    if cur_price > long_target and ma20_condition and before_day_condition:
        position['type'] = 'long'
        position['amount'] = amount
        order = exchange.create_market_buy_order(symbol=symbol, amount=amount)
    elif cur_price < short_target and not ma20_condition:
        position['type'] = 'short'
        position['amount'] = amount
        order = exchange.create_market_sell_order(symbol=symbol, amount=amount)

    if order:
        return position['type'], position['amount'], order['info']['orderId']

    return position['type'], position['amount'], order

def exit_position(exchange, symbol, position):
    order = None
    amount = position['amount']
    if position['type'] == 'long':
        order = exchange.create_market_sell_order(symbol=symbol, amount=amount)
    elif position['type'] == 'short':
        order = exchange.create_market_buy_order(symbol=symbol, amount=amount)

    if order:
        return order['info']['orderId']

    return order

def add_record_log(order_id, binance, symbol):
    db = MariaDB()
    record = binance.fetch_order(order_id, symbol)['info']
    avg_price = float(record['avgPrice'])
    executed_qty = float(record['executedQty'])
    side = record['side']
    status = record['status']
    _type = record['type']
    symbol = record['symbol']
    time = datetime.fromtimestamp(int(record['time']) / 1000)
    fee = float(record['cumQuote']) * 0.0004
    cum_quote = float(record['cumQuote'])

    with db.conn.cursor() as curs:
        sql = """
                INSERT INTO trading_bot_tradingrecord (avg_price, executed_qty, fee, cum_quote, side, status, type, symbol, datetime) 
                     VALUES ({}, {}, {}, {}, {}, {}, {}, {}, {}
                     """.format(avg_price, executed_qty, fee, cum_quote, side, status, _type, symbol) + f", '{time}')"

        curs.execute(sql)
        db.conn.commit()

