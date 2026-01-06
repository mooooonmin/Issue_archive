# !pip install pykrx pandas numpy matplotlib

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pykrx import stock

# -----------------------------
# 파라미터
# -----------------------------
TICKER = "005930"           # 삼성전자
START  = "20240101"
END    = "20241231"
k      = 0.5                # 변동성 돌파 계수
fee    = 0.0005             # 왕복 거래비용(수수료+슬리피지 가정, 0.05%) - 필요 시 조정

# -----------------------------
# 데이터 불러오기 (pykrx)
# -----------------------------
df = stock.get_market_ohlcv_by_date(START, END, TICKER, adjusted=False)

# 컬럼 표준화 (환경에 따라 컬럼명이 다를 수 있음)
rename_map = {
    '시가':'open', '고가':'high', '저가':'low', '종가':'close',
    '거래량':'volume', '거래대금':'value', '등락률':'chg'
}
df = df.rename(columns={c: rename_map.get(c, c) for c in df.columns})
df = df[['open','high','low','close']].copy()

# -----------------------------
# 변동성 돌파 목표가 계산 (전일 기준)
# -----------------------------
prev_high  = df['high'].shift(1)
prev_low   = df['low'].shift(1)
prev_close = df['close'].shift(1)

range_prev = (prev_high - prev_low)
target     = prev_close + k * range_prev
df['target'] = target

# -----------------------------
# 진입 조건 & 진입가
# - 당일 고가가 목표가 이상이면 체결
# - 시가가 목표가보다 높으면 시가로, 아니면 목표가로 체결 가정
# -----------------------------
breakout = df['high'] >= df['target']
entry_price = np.where(df['open'] > df['target'], df['open'], df['target'])
df['entry_price'] = np.where(breakout, entry_price, np.nan)

# -----------------------------
# 당일 청산 (종가)
# -----------------------------
exit_price = df['close']
raw_ret = np.where(breakout, exit_price / df['entry_price'] - 1.0, 0.0)

# 왕복 비용 차감
net_ret = np.where(breakout, raw_ret - fee, 0.0)  # fee는 왕복(진입+청산) 가정
df['strategy_ret'] = net_ret

# -----------------------------
# 성과 지표 계산
# -----------------------------
df['equity'] = (1 + df['strategy_ret']).cumprod()
df['bh'] = df['close'] / df['close'].iloc[0]  # 매수후보유(Buy&Hold)

# 트레이드 수, 승률
n_trades = int(np.isfinite(df['entry_price']).sum())
win_rate = (df.loc[breakout, 'strategy_ret'] > 0).mean() if n_trades > 0 else np.nan

# 총수익률, 최대낙폭(MDD)
total_return = df['equity'].iloc[-1] - 1
rolling_max = df['equity'].cummax()
drawdown = df['equity'] / rolling_max - 1
mdd = drawdown.min()

print("=== 변동성 돌파 백테스트 (삼성전자, 2024, k=0.5) ===")
print(f"거래 횟수         : {n_trades}")
print(f"승률              : {win_rate:.2%}" if n_trades > 0 else "승률              : N/A")
print(f"전략 총 수익률     : {total_return:.2%}")
print(f"최대 낙폭 (MDD)    : {mdd:.2%}")

# -----------------------------
# 시각화
# -----------------------------
plt.rcParams['font.family'] = 'Malgun Gothic'  # 윈도우 한글 폰트 예시

x = df.index.to_numpy()                  # DatetimeIndex -> numpy
equity = df['equity'].to_numpy()
bh = df['bh'].to_numpy()
close_ = df['close'].to_numpy()
target_ = df['target'].to_numpy()

fig, ax = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

# Equity Curve
ax[0].plot(x, equity, label='전략(Equity)', color='navy', lw=2)
ax[0].plot(x, bh, label='매수-보유(BH)', color='gray', lw=1.5, ls='--')
ax[0].set_title('Equity Curve (전략 vs. Buy & Hold)')
ax[0].legend()
ax[0].grid(True, alpha=0.3)

# 가격 + 목표가
ax[1].plot(x, close_, label='종가', color='black', lw=1)
ax[1].plot(x, target_, label='목표가(전일기반)', color='tomato', lw=1, alpha=0.8)

# 진입 지점 산점도도 numpy로
breakout = (df['high'] >= df['target']).to_numpy()
entry_np = df['entry_price'].to_numpy()

ax[1].scatter(x[breakout], entry_np[breakout],
              label='진입 (체결일)', color='green', s=12, alpha=0.8)

ax[1].set_title('가격과 변동성 돌파 목표가')
ax[1].legend()
ax[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()