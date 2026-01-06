# app.py
# pip install streamlit pykrx plotly pandas python-dateutil

import streamlit as st
import pandas as pd
import numpy as np
from datetime import date, timedelta
from dateutil import parser as dtparser
from pykrx import stock
from plotly.subplots import make_subplots
import plotly.graph_objects as go

st.set_page_config(page_title="변동성 돌파 & 매매일지 대시보드", layout="wide")
st.title("📈 변동성 돌파 & 📒 매매일지 대시보드")

# =========================
# Sidebar — Inputs
# =========================
st.sidebar.header("입력")
codes_input = st.sidebar.text_input(
    "종목코드(콤마로 구분, 예: 005930,000660)",
    value="005930",
)
k_input = st.sidebar.text_input("K 값 (예: 0.5)", value="0.5")
fetch_btn = st.sidebar.button("데이터 가져오기")

st.sidebar.divider()
uploaded_file = st.sidebar.file_uploader("매매일지 CSV 업로드", type=["csv"])
st.sidebar.caption("형식: 기준날짜(YYYYMMDD), 종목(또는 종목코드), 손익금액, 수익률 등 열 포함")

# =========================
# Helpers
# =========================
@st.cache_data(ttl=60)
def fetch_ohlcv_15d(code: str) -> pd.DataFrame:
    """최근 15일 OHLCV 데이터 (pykrx)"""
    end = date.today()
    start = end - timedelta(days=15)
    df = stock.get_market_ohlcv_by_date(
        start.strftime("%Y%m%d"),
        end.strftime("%Y%m%d"),
        code,
    )
    # 표준화
    col_map = {"시가": "Open", "고가": "High", "저가": "Low", "종가": "Close"}
    df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})
    df = df[["Open", "High", "Low", "Close"]].copy()
    df.index = pd.to_datetime(df.index)
    df.reset_index(names="Date", inplace=True)
    return df

def add_breakout_target(df: pd.DataFrame, k: float) -> pd.DataFrame:
    """목표가: (전일 (고-저) * K + 전일 종가) → 당일에 표시"""
    rng = (df["High"] - df["Low"]) * k
    df["Target"] = (df["Close"] + rng).shift(1)
    return df

def detect_and_rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """CSV의 한국어/영어 열 이름을 유연하게 감지해 표준화합니다."""
    cols = {c.lower().strip(): c for c in df.columns}

    def pick(keys, required=True):
        for k in keys:
            # 직접 일치 또는 lower 일치
            if k in df.columns:
                return k
            if k.lower() in cols:
                return cols[k.lower()]
        if required:
            raise KeyError(f"필수 컬럼 누락: {keys}")
        return None

    date_col   = pick(["기준날짜", "날짜", "일자", "date"])
    ticker_col = pick(["종목", "종목명", "종목코드", "티커", "code", "ticker"])
    pnl_col    = pick(["손익금액", "손익", "손익(원)", "pnl", "profit", "금액"])
    ret_col    = pick(["수익률", "수익률(%)", "수익%", "return", "ret"])

    out = df.rename(
        columns={
            date_col: "DateRaw",
            ticker_col: "Ticker",
            pnl_col: "PnL",
            ret_col: "Return",
        }
    ).copy()

    # 날짜 표준화 (YYYYMMDD → datetime)
    def parse_date(v):
        v = str(v).strip()
        if v.isdigit() and len(v) == 8:
            return pd.to_datetime(v, format="%Y%m%d", errors="coerce")
        # 그 외 형식도 허용
        try:
            return pd.to_datetime(dtparser.parse(v).date())
        except Exception:
            return pd.NaT

    out["Date"] = out["DateRaw"].map(parse_date)
    # 숫자 컬럼 정규화 (콤마 제거 등)
    out["PnL"] = pd.to_numeric(out["PnL"].astype(str).str.replace(",", ""), errors="coerce")
    out["Return"] = pd.to_numeric(out["Return"].astype(str).str.replace("%", ""), errors="coerce")

    # Return이 1.0 이하 절댓값이면 퍼센트가 아니라 비율로 보고 100배
    if out["Return"].abs().max(skipna=True) <= 1.0:
        out["Return(%)"] = out["Return"] * 100.0
    else:
        out["Return(%)"] = out["Return"]

    return out[["Date", "Ticker", "PnL", "Return(%)"]].dropna(subset=["Date"])

def make_csv_dual_axis_chart(df_csv: pd.DataFrame, tickers: list[str]) -> go.Figure:
    """일자-종목 집계 후 y1=수익률(%) 라인, y2=손익금액 바"""
    # 일자-종목별 집계: 손익금액=합계, 수익률(%)=평균  (※ 가중치 컬럼이 있으면 가중평균으로 바꾸세요)
    grouped = (
        df_csv.groupby(["Date", "Ticker"], as_index=False)
              .agg(PnL=("PnL", "sum"), ReturnPct=("Return(%)", "mean"))
    )
    if tickers:
        grouped = grouped[grouped["Ticker"].isin(tickers)]

    grouped = grouped.sort_values("Date")
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    # 종목별 trace 생성
    for tk in grouped["Ticker"].unique():
        sub = grouped[grouped["Ticker"] == tk]
        # y2: 손익금액 (막대, secondary)
        fig.add_trace(
            go.Bar(
                x=sub["Date"],
                y=sub["PnL"],
                name=f"{tk} 손익(원)",
                opacity=0.6,
                hovertemplate="날짜=%{x|%Y-%m-%d}<br>손익=%{y:,.0f}원<extra></extra>",
            ),
            secondary_y=True,
        )
        # y1: 수익률(%) (꺾은선, primary)
        fig.add_trace(
            go.Scatter(
                x=sub["Date"],
                y=sub["ReturnPct"],
                name=f"{tk} 수익률(%)",
                mode="lines+markers",
                line=dict(width=2),
                marker=dict(size=6),
                hovertemplate="날짜=%{x|%Y-%m-%d}<br>수익률=%{y:.2f}%<extra></extra>",
            ),
            secondary_y=False,
        )

    fig.update_layout(
        title="일자별 손익(막대, 오른쪽축) & 수익률(선, 왼쪽축)",
        barmode="group",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=40, r=40, t=60, b=40),
    )
    fig.update_xaxes(title_text="날짜")
    fig.update_yaxes(title_text="수익률 (%)", secondary_y=False)
    fig.update_yaxes(title_text="손익금액 (원)", secondary_y=True)
    return fig

# =========================
# Main — Section 1: OHLC & 목표가 (기존)
# =========================
st.subheader("① 종목 OHLC & 변동성 돌파 목표가")

if not fetch_btn:
    st.info("좌측에서 종목코드와 K 값을 입력한 뒤 **데이터 가져오기**를 누르면 차트가 표시됩니다.")
else:
    # 입력 검증
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
                # y1: OHLC (캔들)
                fig.add_trace(
                    go.Candlestick(
                        x=df["Date"],
                        open=df["Open"], high=df["High"],
                        low=df["Low"], close=df["Close"],
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
                st.caption("목표가 산식: **(전일 고가 − 전일 저가) × K + 전일 종가**  → 해당일에 표시됩니다.")
            except Exception as e:
                st.error(f"{code} 데이터 처리 중 오류: {e}")

# =========================
# Main — Section 2: CSV 기반 일별 손익/수익률
# =========================
st.subheader("② 매매일지: 일별 손익(원) & 수익률(%)")

if uploaded_file is None:
    st.info("좌측에서 CSV 파일을 업로드하면, 일자별 손익/수익률 차트가 표시됩니다.")
else:
    try:
        raw = pd.read_csv(uploaded_file)
        df_csv = detect_and_rename_columns(raw)
        if df_csv.empty:
            st.warning("CSV에서 유효한 데이터가 없습니다.")
        else:
            # 종목 선택 멀티셀렉트
            all_tickers = sorted(df_csv["Ticker"].dropna().astype(str).unique().tolist())
            selected = st.multiselect("표시할 종목 선택", options=all_tickers, default=all_tickers)
            fig2 = make_csv_dual_axis_chart(df_csv, selected)
            st.plotly_chart(fig2, use_container_width=True)

            # 표도 간단히 제공 (집계 형태로)
            grouped = (
                df_csv.groupby(["Date", "Ticker"], as_index=False)
                      .agg(손익금액=("PnL", "sum"), 수익률_평균=("Return(%)", "mean"))
                      .sort_values(["Date", "Ticker"])
            )
            with st.expander("집계 데이터 미리보기"):
                st.dataframe(grouped, use_container_width=True)

            st.caption("집계 로직: **손익금액=합계, 수익률=평균** (필요 시 가중평균으로 수정하세요).")
    except KeyError as ke:
        st.error(f"CSV 열을 해석하지 못했습니다: {ke}")
        st.markdown(
            """
            **필수 열(이름 예시)**  
            - 날짜: `기준날짜`/`날짜`/`일자`/`date` (YYYYMMDD 권장)  
            - 종목: `종목`/`종목명`/`종목코드`/`티커`/`ticker`  
            - 손익금액: `손익금액`/`손익`/`pnl`/`profit`  
            - 수익률: `수익률`/`수익률(%)`/`return`/`ret`
            """
        )
    except Exception as e:
        st.error(f"CSV 처리 중 오류: {e}")
