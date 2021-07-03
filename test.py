import pyupbit

access = "KIfpgABROQxyxPedL6KXhTg8GEchN2y0R4MgJddp"          # 본인 값으로 변경
secret = "CC83w57xLaUIW7w3dunHBrglx53VCO8QXbK69Fu2"          # 본인 값으로 변경
upbit = pyupbit.Upbit(access, secret)

print(upbit.get_balance("KRW-XRP"))     # KRW-XRP 조회
print(upbit.get_balance("KRW"))         # 보유 현금 조회
