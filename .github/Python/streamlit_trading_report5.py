# app.py
# pip install streamlit pykrx plotly pandas python-dateutil holidays

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
st.sidebar.caption("형식: 기준날짜(YYYYMMDD), 종목/종목코드, 손익금액, 수익률, (선택) 매수수량/수량/매매구분 등")

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

def _pick_col(df: pd.DataFrame, candidates: list[str], required: bool = True) -> str | None:
    cols = {c.lower().strip(): c for c in df.columns}
    for k in candidates:
        if k in df.columns:
            return k
        if k.lower() in cols:
            return cols[k.lower()]
    if required:
        raise KeyError(f"필수 컬럼 누락: {candidates}")
    return None

def detect_and_rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """CSV의 한국어/영어 열 이름을 유연하게 감지해 표준화합니다."""
    date_col   = _pick_col(df, ["기준날짜", "날짜", "일자", "date"])
    ticker_col = _pick_col(df, ["종목", "종목명", "종목코드", "티커", "code", "ticker"])
    pnl_col    = _pick_col(df, ["손익금액", "손익", "손익(원)", "pnl", "profit", "금액"])
    ret_col    = _pick_col(df, ["수익률", "수익률(%)", "수익%", "return", "ret"])

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
        try:
            return pd.to_datetime(dtparser.parse(v).date())
        except Exception:
            return pd.NaT

    out["Date"] = out["DateRaw"].map(parse_date)

    # 숫자 컬럼 정규화
    out["PnL"] = pd.to_numeric(out["PnL"].astype(str).str.replace(",", ""), errors="coerce")
    out["Return"] = pd.to_numeric(out["Return"].astype(str).str.replace("%", ""), errors="coerce")

    # Return을 % 단위로 통일
    if out["Return"].abs().max(skipna=True) <= 1.0:
        out["Return(%)"] = out["Return"] * 100.0
    else:
        out["Return(%)"] = out["Return"]

    # 선택 컬럼(매수수량/수량/매매구분) 탐지
    buyqty_col = _pick_col(df, ["매수수량", "매수 수량", "buy_qty"], required=False)
    qty_col    = _pick_col(df, ["수량", "거래수량", "체결수량", "qty", "quantity"], required=False)
    side_col   = _pick_col(df, ["매매구분", "매수매도", "구분", "side", "type", "transaction", "buy/sell"], required=False)

    out["BuyQty"] = np.nan
    if buyqty_col:
        out["BuyQty"] = pd.to_numeric(df[buyqty_col].astype(str).str.replace(",", ""), errors="coerce")
    elif qty_col:
        qty_vals = pd.to_numeric(df[qty_col].astype(str).str.replace(",", ""), errors="coerce")
        if side_col:
            side_raw = df[side_col].astype(str).str.strip().str.upper()
            # 매수 판단 키워드
            is_buy = side_raw.str.contains("매수|BUY|B", regex=True)
            out.loc[is_buy.index, "BuyQty"] = qty_vals.where(is_buy, np.nan)
        else:
            # 매매구분이 없으면 전체 수량을 매수수량으로 볼 수 없으므로 경고 표시를 위해 남겨둠
            out["BuyQty"] = np.nan

    return out[["Date", "Ticker", "PnL", "Return(%)", "BuyQty"]].dropna(subset=["Date"])

def make_csv_dual_axis_chart(df_csv: pd.DataFrame, tickers: list[str]) -> go.Figure:
    """일자-종목 집계 후 y1=수익률(%) 라인, y2=손익금액 바"""
    grouped = (
        df_csv.groupby(["Date", "Ticker"], as_index=False)
              .agg(PnL=("PnL", "sum"), ReturnPct=("Return(%)", "mean"))
    )
    if tickers:
        grouped = grouped[grouped["Ticker"].isin(tickers)]

    grouped = grouped.sort_values("Date")
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    for tk in grouped["Ticker"].unique():
        sub = grouped[grouped["Ticker"] == tk]
        fig.add_trace(
            go.Bar(
                x=sub["Date"], y=sub["PnL"],
                name=f"{tk} 손익(원)", opacity=0.6,
                hovertemplate="날짜=%{x|%Y-%m-%d}<br>손익=%{y:,.0f}원<extra></extra>",
            ),
            secondary_y=True,
        )
        fig.add_trace(
            go.Scatter(
                x=sub["Date"], y=sub["ReturnPct"],
                name=f"{tk} 수익률(%)", mode="lines+markers",
                line=dict(width=2), marker=dict(size=6),
                hovertemplate="날짜=%{x|%Y-%m-%d}<br>수익률=%{y:.2f}%<extra></extra>",
            ),
            secondary_y=False,
        )

    fig.update_layout(
        title="일자별 손익(막대, 오른쪽축) & 수익률(선, 왼쪽축)",
        barmode="group", hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=40, r=40, t=60, b=40),
    )
    fig.update_xaxes(title_text="날짜")
    fig.update_yaxes(title_text="수익률 (%)", secondary_y=False)
    fig.update_yaxes(title_text="손익금액 (원)", secondary_y=True)
    return fig

def get_kr_working_days(start: pd.Timestamp, end: pd.Timestamp) -> pd.DatetimeIndex:
    """주말 제외 + 한국 공휴일 제외 working days"""
    bdays = pd.date_range(start, end, freq="B")  # 월~금
    try:
        import holidays as pyholidays
        kr = pyholidays.KR(years=range(start.year, end.year + 1))
        mask = [d.date() not in kr for d in bdays]
        return bdays[mask]
    except Exception:
        st.warning("⚠️ 'holidays' 패키지를 사용할 수 없어 공휴일 제외 없이 '영업일(월~금)'만 계산합니다. (pip install holidays)")
        return bdays

# =========================
# Main — Section 1: OHLC & 목표가 (기존)
# =========================
st.subheader("① 종목 OHLC & 변동성 돌파 목표가")

if not fetch_btn:
    st.info("좌측에서 종목코드와 K 값을 입력한 뒤 **데이터 가져오기**를 누르면 차트가 표시됩니다.")
else:
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
                fig.add_trace(
                    go.Scatter(
                        x=df["Date"], y=df["Target"],
                        mode="lines", name=f"목표가 (K={K})",
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
# Main — Section 2: CSV 기반 일별 손익/수익률 (이전 요구)
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
            # 종목 선택
            all_tickers = sorted(df_csv["Ticker"].dropna().astype(str).unique().tolist())
            selected = st.multiselect("표시할 종목 선택", options=all_tickers, default=all_tickers)

            fig2 = make_csv_dual_axis_chart(df_csv, selected)
            st.plotly_chart(fig2, use_container_width=True)

            grouped_preview = (
                df_csv.groupby(["Date", "Ticker"], as_index=False)
                      .agg(손익금액=("PnL", "sum"), 수익률_평균=("Return(%)", "mean"))
                      .sort_values(["Date", "Ticker"])
            )
            with st.expander("집계 데이터 미리보기"):
                st.dataframe(grouped_preview, use_container_width=True)

            st.caption("집계 로직: **손익금액=합계, 수익률=평균** (필요 시 가중평균으로 수정하세요).")

            st.divider()
            st.subheader("③ 추가 분석 (3개 컬럼)")

            col1, col2, col3 = st.columns(3)

            # -------- Chart 1: 종목별 전체 기간 '매수수량' 파이차트 --------
            with col1:
                st.markdown("**차트 1 — 종목별 매수수량 파이차트**")
                pie_df = None
                if df_csv["BuyQty"].notna().any():
                    pie_df = (
                        df_csv.groupby("Ticker", as_index=False)
                              .agg(BuyQty=("BuyQty", "sum"))
                              .dropna(subset=["BuyQty"])
                    )
                    # 0 또는 NaN은 제외
                    pie_df = pie_df[pie_df["BuyQty"] > 0]
                if pie_df is None or pie_df.empty:
                    st.warning("CSV에 **매수수량/수량** 정보가 없거나 매수수량이 0입니다. 파이차트를 생략합니다.")
                else:
                    if selected:
                        pie_df = pie_df[pie_df["Ticker"].isin(selected)]
                    fig_pie = go.Figure(
                        go.Pie(
                            labels=pie_df["Ticker"],
                            values=pie_df["BuyQty"],
                            hole=0.35,
                            textinfo="label+percent",
                            hovertemplate="%{label}<br>매수수량=%{value:,.0f}<extra></extra>",
                        )
                    )
                    fig_pie.update_layout(title="종목별 누적 매수수량")
                    st.plotly_chart(fig_pie, use_container_width=True)

            # -------- Chart 2: 종목별 전체 기간 '수익률 평균' 막대차트 --------
            with col2:
                st.markdown("**차트 2 — 종목별 평균 수익률(%) 막대차트**")
                bar_ret = (
                    df_csv.groupby("Ticker", as_index=False)
                          .agg(AvgReturnPct=("Return(%)", "mean"))
                )
                if selected:
                    bar_ret = bar_ret[bar_ret["Ticker"].isin(selected)]
                fig_bar_ret = go.Figure(
                    go.Bar(
                        x=bar_ret["Ticker"],
                        y=bar_ret["AvgReturnPct"],
                        text=[f"{v:.2f}%" for v in bar_ret["AvgReturnPct"]],
                        textposition="outside",
                        hovertemplate="종목=%{x}<br>평균 수익률=%{y:.2f}%<extra></extra>",
                    )
                )
                fig_bar_ret.update_layout(
                    title="종목별 평균 수익률(%)",
                    yaxis_title="평균 수익률(%)",
                    xaxis_title="종목",
                    margin=dict(l=20, r=20, t=60, b=20),
                )
                st.plotly_chart(fig_bar_ret, use_container_width=True)

            # -------- Chart 3: 종목별 매수 진행 확률 막대차트 --------
            with col3:
                st.markdown("**차트 3 — 종목별 매수 진행 확률**")
                # 전체 working days (주말 + 한국 공휴일 제외)
                dmin, dmax = df_csv["Date"].min(), df_csv["Date"].max()
                working_days = get_kr_working_days(dmin, dmax)
                total_working = len(working_days)
                if total_working == 0:
                    st.warning("유효한 working day가 없습니다.")
                else:
                    wd_set = set(working_days.normalize())  # 날짜 비교를 위해 normalize
                    # 각 종목이 거래된 날짜(working days 교집합) 개수
                    traded = (
                        df_csv.dropna(subset=["Date"])
                              .assign(DateNorm=lambda x: x["Date"].dt.normalize())
                              .groupby("Ticker")["DateNorm"]
                              .agg(lambda s: len(set(s) & wd_set))
                              .rename("TradeDays")
                              .reset_index()
                    )
                    traded["Prob"] = traded["TradeDays"] / total_working
                    if selected:
                        traded = traded[traded["Ticker"].isin(selected)]

                    fig_prob = go.Figure(
                        go.Bar(
                            x=traded["Ticker"],
                            y=traded["Prob"] * 100.0,
                            text=[f"{p*100:.1f}%" for p in traded["Prob"]],
                            textposition="outside",
                            hovertemplate="종목=%{x}<br>매수 진행 확률=%{y:.1f}%"
                                          f"<br>거래일수={traded['TradeDays']}"
                                          f"<br>전체 거래일={total_working}<extra></extra>",
                        )
                    )
                    fig_prob.update_layout(
                        title="종목별 매수 진행 확률 (영업일 기준)",
                        yaxis_title="확률 (%)",
                        xaxis_title="종목",
                        margin=dict(l=20, r=20, t=60, b=20),
                    )
                    st.plotly_chart(fig_prob, use_container_width=True)

    except KeyError as ke:
        st.error(f"CSV 열을 해석하지 못했습니다: {ke}")
        st.markdown(
            """
            **필수 열(이름 예시)**  
            - 날짜: `기준날짜`/`날짜`/`일자`/`date` (YYYYMMDD 권장)  
            - 종목: `종목`/`종목명`/`종목코드`/`티커`/`ticker`  
            - 손익금액: `손익금액`/`손익`/`pnl`/`profit`  
            - 수익률: `수익률`/`수익률(%)`/`return`/`ret`  
            
            **선택 열(있으면 추가 차트 활성화)**  
            - 매수수량: `매수수량`/`매수 수량`/`buy_qty`  
              또는 `수량` + `매매구분(매수/매도)`/`side(BUY/SELL)`
            """
        )
    except Exception as e:
        st.error(f"CSV 처리 중 오류: {e}")