# app.py
# pip install streamlit pykrx plotly pandas

import streamlit as st
import pandas as pd
from datetime import date, timedelta
from pykrx import stock
from plotly.subplots import make_subplots
import plotly.graph_objects as go

st.set_page_config(page_title="변동성 돌파 대시보드", layout="wide")
st.title("📈 변동성 돌파 백테스트 미니 대시보드")

# ---- Sidebar: Inputs ----
codes_input = st.sidebar.text_input(
    "종목코드(콤마로 구분, 예: 005930,000660)",
    value="005930"
)
k_input = st.sidebar.text_input("K 값 (예: 0.5)", value="0.5")
fetch_btn = st.sidebar.button("데이터 가져오기")

# ---- Helper: Fetch OHLCV ----
@st.cache_data(ttl=60)
def fetch_ohlcv_15d(code: str) -> pd.DataFrame:
    end = date.today()
    start = end - timedelta(days=15)
    df = stock.get_market_ohlcv_by_date(
        start.strftime("%Y%m%d"),
        end.strftime("%Y%m%d"),
        code
    )
    # 표준 컬럼명으로 정리
    col_map = {"시가": "Open", "고가": "High", "저가": "Low", "종가": "Close"}
    df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})
    df = df[["Open", "High", "Low", "Close"]].copy()
    df.index = pd.to_datetime(df.index)
    df.reset_index(names="Date", inplace=True)
    return df

def add_breakout_target(df: pd.DataFrame, k: float) -> pd.DataFrame:
    # x일의 목표가 = (전일(고가-저가)*K + 전일 종가)
    rng = (df["High"] - df["Low"]) * k
    target = (df["Close"] + rng).shift(1)
    df["Target"] = target
    return df

# ---- Main ----
if not fetch_btn:
    st.info("좌측 사이드바에서 종목코드와 K 값을 입력한 뒤 **데이터 가져오기**를 누르세요.")
else:
    # 입력 파싱 & 검증
    try:
        K = float(k_input)
    except ValueError:
        st.error("K 값은 숫자여야 합니다. 예: 0.5")
        st.stop()

    codes = [c.strip() for c in codes_input.split(",") if c.strip()]
    if not codes:
        st.error("최소 1개의 종목코드를 입력하세요. 예: 005930")
        st.stop()

    tabs = st.tabs(codes)
    for tab, code in zip(tabs, codes):
        with tab:
            try:
                df = fetch_ohlcv_15d(code)
                if df.empty:
                    st.warning(f"{code}: 조회된 데이터가 없습니다.")
                    continue
                df = add_breakout_target(df, K)

                fig = make_subplots(specs=[[{"secondary_y": True}]])
                # y1: OHLC (캔들스틱)
                fig.add_trace(
                    go.Candlestick(
                        x=df["Date"],
                        open=df["Open"],
                        high=df["High"],
                        low=df["Low"],
                        close=df["Close"],
                        name="OHLC",
                        increasing_line_color="#ef4444",
                        decreasing_line_color="#22c55e",
                    ),
                    secondary_y=False,
                )
                # y2: 목표가 (라인)
                fig.add_trace(
                    go.Scatter(
                        x=df["Date"],
                        y=df["Target"],
                        mode="lines",
                        name=f"목표가 (K={K})",
                        line=dict(color="dodgerblue", width=2),
                    ),
                    secondary_y=True,
                )

                fig.update_layout(
                    title=f"{code} - 최근 15일 OHLC & 목표가",
                    xaxis_title="날짜",
                    yaxis_title="가격 (OHLC)",
                    yaxis2_title="가격 (목표가)",
                    xaxis_rangeslider_visible=False,
                    hovermode="x unified",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
                    margin=dict(l=40, r=40, t=60, b=40),
                )
                st.plotly_chart(fig, use_container_width=True)

                st.caption(
                    "목표가 산식: **(전일 고가 − 전일 저가) × K + 전일 종가**  → 해당일에 표시됩니다."
                )
            except Exception as e:
                st.error(f"{code} 데이터 처리 중 오류: {e}")
