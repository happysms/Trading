from datetime import datetime, timedelta
from pytz import timezone
import time
import pyupbit
import datetime
from slacker import Slacker
import argparse
import logger


def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0


def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]


def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['low']) * k
    return target_price


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--access', metavar='access', required=True,
                        help='access')
    parser.add_argument('--secret', metavar='secret', required=True,
                        help='secret')
    parser.add_argument('--token', metavar='token', required=True,
                        help='token')  # 슬랙 토큰
    args = parser.parse_args()

    access = args.access
    secret = args.secret
    token = args.token

    KST = timezone('Asia/Seoul')
    slack = Slacker(token)
    upbit = pyupbit.Upbit(access, secret)
    mylogger = logger.make_logger("main")

    mylogger.info("ETH Trading Start")
    slack.chat.post_message('#stock', "ETH Trading Start")

    while True:
        try:
            now = (KST.localize(datetime.datetime.now()))
            start_time = KST.localize(datetime.datetime(now.year, now.month, now.day, 9, 0, 0))

            if now.hour < 9:
                start_time = start_time - timedelta(days=1)

            end_time = start_time + timedelta(days=1)

            if start_time < now < end_time - timedelta(seconds=10):  # 가격 감시 시간
                target_price = get_target_price(ticker="KRW-ETH", k=0.4)
                current_price = get_current_price("KRW-ETH")

                if target_price <= current_price:
                    krw = upbit.get_balance("KRW")

                    if krw > 5006:  # 최소 주문 금액
                        buy_result = upbit.buy_market_order("KRW-ETH", 10000)
                        mylogger.info(f"{krw}원 매수 주문 ")
                        slack.chat.post_message('#stock', f"{krw}원 매수 주문")

            else:  # 파는 시간
                eth = get_balance("ETH")
                sell_result = upbit.sell_market_order("KRW-ETH", eth)
                mylogger.info(f"ETH {eth}개 매도 주문 ")
                slack.chat.post_message('#stock', f"ETH {eth}개 매도 주문")

            time.sleep(0.5)

        except Exception as e:
            mylogger.info(e)
            slack.chat.post_message('#stock', e)
            time.sleep(0.5)
