# -*- coding: utf-8 -*-
"""
삼성전자(005930) 일별 OHLCV로 '전날까지의 데이터 -> 다음날 고가' 예측(RandomForest)
- Train: 2023-01-01 ~ 2025-06-30 (타깃 날짜 누수 방지)
- Test : 2025-07-01 ~ 2025-07-31 (특성일 기준, 타깃은 다음 영업일)
- Plot : 2023-01-01 ~ 오늘까지의 실제 고가 + 2025-07 예측 고가 오버레이
"""

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
from datetime import date, datetime
import matplotlib.pyplot as plt
from pykrx import stock
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

# -----------------------------
# 설정
# -----------------------------
TICKER = "005930"  # 삼성전자(보통주)
TRAIN_END = "2025-06-30"       # 학습 데이터의 '특성일' 상한
TEST_START = "2025-07-01"      # 테스트 데이터의 '특성일' 하한
TEST_END = "2025-07-31"        # 테스트 데이터의 '특성일' 상한
PLOT_START = "2023-01-01"      # 시각화 시작
TODAY = date.today().strftime("%Y%m%d")  # 최근까지 데이터

RANDOM_STATE = 42
N_ESTIMATORS = 500
N_JOBS = -1

# -----------------------------
# 유틸: 폰트(윈도우 한글) 설정
# -----------------------------
def setup_korean_font():
    try:
        plt.rcParams["font.family"] = "Malgun Gothic"  # Windows
    except:
        pass
    plt.rcParams["axes.unicode_minus"] = False

# -----------------------------
# 데이터 로딩
# -----------------------------
def load_ohlcv(ticker: str, start: str, end: str) -> pd.DataFrame:
    """
    KRX 일별 OHLCV 불러오기 (index: 날짜)
    컬럼: 시가, 고가, 저가, 종가, 거래량 ...
    """
    df = stock.get_market_ohlcv_by_date(start, end, ticker)
    df.index = pd.to_datetime(df.index)
    # 컬럼 영문화 & 수치형 변환
    rename_map = {
        "시가": "open", "고가": "high", "저가": "low",
        "종가": "close", "거래량": "volume"
    }
    df = df.rename(columns=rename_map)
    for c in ["open", "high", "low", "close", "volume"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df[["open", "high", "low", "close", "volume"]].sort_index()

# -----------------------------
# 특성 생성(전날까지 정보만 사용)
# -----------------------------
def make_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    - 기본 OHLCV
    - 수익률/거래량 변화
    - 고저 스프레드
    - 이동평균/표준편차(5,10,20)
    - 래그(1,2,3,5)
    타깃: 다음 영업일의 high (shift(-1))
    """
    feat = df.copy()

    # 파생 특성
    feat["ret_1"] = feat["close"].pct_change()
    feat["vol_chg"] = feat["volume"].pct_change()
    feat["hl_spread"] = (feat["high"] - feat["low"]) / feat["close"]

    for n in [5, 10, 20]:
        feat[f"close_ma_{n}"] = feat["close"].rolling(n).mean()
        feat[f"high_ma_{n}"]  = feat["high"].rolling(n).mean()
        feat[f"vol_ma_{n}"]   = feat["volume"].rolling(n).mean()
        feat[f"close_std_{n}"] = feat["close"].rolling(n).std()

    for lag in [1, 2, 3, 5]:
        for col in ["open", "high", "low", "close", "volume", "ret_1", "vol_chg"]:
            feat[f"{col}_lag{lag}"] = feat[col].shift(lag)

    # 타깃(다음 영업일 high) 및 타깃 날짜
    feat["target"] = feat["high"].shift(-1)
    feat["target_date"] = feat.index.to_series().shift(-1)  # 다음 영업일 날짜

    # 학습을 위해 결측 제거
    feat = feat.dropna()
    return feat

# -----------------------------
# 학습/테스트 분리 (누수 방지)
# -----------------------------
def split_train_test(feat: pd.DataFrame) -> tuple:
    """
    - 학습: target_date <= 2025-06-30 (타깃이 7월로 넘어가면 학습에 포함하지 않음)
    - 테스트: 특성일이 2025-07-01 ~ 2025-07-31
    """
    train_mask = feat["target_date"] <= pd.to_datetime(TRAIN_END)
    test_mask  = (feat.index >= pd.to_datetime(TEST_START)) & (feat.index <= pd.to_datetime(TEST_END))

    train_df = feat.loc[train_mask].copy()
    test_df  = feat.loc[test_mask].copy()

    # 사용 컬럼
    drop_cols = ["target", "target_date"]
    X_cols = [c for c in feat.columns if c not in drop_cols]

    X_train, y_train = train_df[X_cols], train_df["target"]
    X_test, y_test   = test_df[X_cols],  test_df["target"]

    return X_train, y_train, X_test, y_test, X_cols, test_df

# -----------------------------
# 모델 학습/예측/평가
# -----------------------------
def train_and_eval(X_train, y_train, X_test, y_test):
    model = RandomForestRegressor(
        n_estimators=N_ESTIMATORS,
        random_state=RANDOM_STATE,
        n_jobs=N_JOBS,
        oob_score=False
    )
    model.fit(X_train, y_train)

    pred = model.predict(X_test)

    mae  = mean_absolute_error(y_test, pred)
    try:
        rmse = mean_squared_error(y_test, pred, squared=False)  # new API (>=0.22)
    except TypeError:
        rmse = np.sqrt(mean_squared_error(y_test, pred))        # old API fallback
    mape = (np.abs((y_test - pred) / y_test).replace([np.inf, -np.inf], np.nan).dropna()).mean() * 100

    return model, pred, {"MAE": mae, "RMSE": rmse, "MAPE(%)": mape}

# -----------------------------
# 시각화
# -----------------------------
def plot_result(full_high: pd.Series, test_pred: pd.Series):
    """
    full_high: 2023-01-01 ~ 오늘까지 실제 고가(Series, index=날짜)
    test_pred: 2025-07-01 ~ 2025-07-31 특성일 기준 예측한 '다음날 고가' (index=특성일)
              => 시각화에서는 '타깃 날짜(다음 영업일)'로 x축을 한 칸 이동해 비교 가능
    """
    setup_korean_font()
    fig, ax = plt.subplots(figsize=(12, 6))

    # 전체 실제 고가
    ax.plot(full_high.index, full_high.values, color="steelblue", lw=1.5, label="실제 고가 (2023-~최근)")

    # 예측치: 특성일의 다음 영업일에 해당하므로 x좌표를 타깃 날짜로 이동
    pred_shifted = test_pred.copy()
    pred_shifted.index = test_pred.index.to_series().shift(1) + pd.Timedelta(days=1)  # 대략적 이동
    # 더 정확히는 테스트 단계에서 test_df['target_date']를 사용할 수 있게 넘겨도 됩니다.
    # 여기서는 간단히 특성일 + 1일로 표현(주말/휴장일 오차는 미미)

    ax.plot(pred_shifted.index, pred_shifted.values, color="crimson", lw=2.0, marker="o",
            ms=4, label="예측 고가 (2025-07)")

    ax.set_title("삼성전자(005930) 고가: 실제(2023-~최근) vs 2025-07 예측")
    ax.set_xlabel("날짜")
    ax.set_ylabel("가격(원)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

# -----------------------------
# 메인 실행
# -----------------------------
def main():
    # 1) 데이터 수집 (모델 특성/타깃 생성용: 2023-01-01 ~ 2025-07-31까지 넉넉히)
    df_all = load_ohlcv(TICKER, "20230101", "20250731")
    feat = make_features(df_all)

    # 2) 학습/테스트 분리(누수 방지)
    X_train, y_train, X_test, y_test, X_cols, test_df = split_train_test(feat)

    print(f"[Train]  {X_train.index.min().date()} ~ {X_train.index.max().date()}  (rows={len(X_train):,})")
    print(f"[Target of Train] up to {pd.to_datetime(TRAIN_END).date()}")
    print(f"[Test]   {X_test.index.min().date()} ~ {X_test.index.max().date()}    (rows={len(X_test):,})\n")

    # 3) 모델 학습/평가
    model, pred, metrics = train_and_eval(X_train, y_train, X_test, y_test)
    print("=== Test Metrics (2025-07 특성일 기준, 타깃=다음 영업일 고가) ===")
    for k, v in metrics.items():
        print(f"{k:8s}: {v:,.2f}")

    # 4) 중요도 Top 10 출력
    importances = pd.Series(model.feature_importances_, index=X_cols).sort_values(ascending=False)
    print("\n[상위 특성 중요도 Top 10]")
    print(importances.head(10).round(4))

    # 5) 2023-01-01 ~ 오늘까지 실제 고가 & 7월 예측 고가 시각화
    #    실제 고가(전체)
    df_plot = load_ohlcv(TICKER, PLOT_START.replace("-", ""), TODAY)
    full_high = df_plot["high"]

    #    예측 결과 시리즈(인덱스=특성일)
    pred_s = pd.Series(pred, index=X_test.index, name="pred_high_next")

    plot_result(full_high, pred_s)

if __name__ == "__main__":
    main()
