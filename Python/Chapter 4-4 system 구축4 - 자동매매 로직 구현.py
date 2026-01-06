import sys
from datetime import datetime, timedelta, time

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import QTimer
from PyQt5.QtTest import QTest

from pykiwoom.kiwoom import Kiwoom
from pykrx import stock
import pandas as pd


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # ---------- UI ----------
        uic.loadUi("gui.ui", self)

        # ---------- State ----------
        self.timer = QTimer(self)
        self.timer.setInterval(10_000)  # 10초 주기 (이전 요구 반영)
        self.timer.timeout.connect(self.on_tick)

        self.codes = []                 # 감시 종목
        self.running = False
        self.rate_wait_ms = 200         # TR 완화 (필요시 조정)
        self.breakout = {}              # code -> 돌파가격 (종가 + K*(H-L))
        self.bought = set()             # 금일 매수 완료한 종목 코드
        self.sell_executed_today = False
        self.price_queries_disabled_today = False  # <<< (추가) 당일 시세 조회 중단 플래그
        self.sell_time = time(15, 0, 0) # 15:00 정각 일괄 매도

        # ---------- Buttons ----------
        self.button_start.clicked.connect(self.on_start)
        self.button_stop.clicked.connect(self.on_stop)
        self.button_stop.setEnabled(False)

        # ---------- Kiwoom ----------
        try:
            self.kiwoom = Kiwoom()
            self.kiwoom.CommConnect(block=True)
            accs = self.kiwoom.GetLoginInfo("ACCNO")
            if isinstance(accs, list):
                self.account = accs[0]
            else:
                self.account = str(accs).split(";")[0].strip()
            if not self.account:
                raise RuntimeError("계좌번호 조회 실패")
        except Exception as e:
            QMessageBox.critical(self, "Kiwoom 로그인 실패", str(e))
            sys.exit(1)

    # ===========================================
    # UI Handlers
    # ===========================================
    def on_start(self):
        raw = (self.code_list.text() or "").strip()
        codes = [c.strip() for c in raw.split(",") if c.strip()]
        if not codes:
            QMessageBox.warning(self, "입력 필요", "code_list에 종목 코드를 입력하세요. (예: 005930,000270)")
            return

        try:
            k = float((self.k_value.text() or "").strip())
        except Exception:
            QMessageBox.warning(self, "입력 오류", "K 값을 실수로 입력하세요. (예: 0.5)")
            return
        if k <= 0:
            QMessageBox.warning(self, "입력 오류", "K 값은 0보다 커야 합니다.")
            return

        self.codes = codes
        self.running = True
        self.sell_executed_today = False
        self.price_queries_disabled_today = False     # <<< (추가) 시작 시 해제
        self.bought.clear()
        self.textboard.clear()
        self.buysell_log.clear()

        self.button_start.setEnabled(False)
        self.button_stop.setEnabled(True)

        try:
            self.prepare_breakout_levels(k)
        except Exception as e:
            QMessageBox.critical(self, "돌파 레벨 계산 실패", str(e))
            self.on_stop()
            return

        self.timer.start()

    def on_stop(self):
        self.timer.stop()
        self.running = False
        self.codes = []
        self.breakout.clear()
        self.bought.clear()
        self.sell_executed_today = False
        self.price_queries_disabled_today = False     # <<< (추가) 정지 시 초기화

        self.textboard.clear()
        self.buysell_log.clear()

        self.button_start.setEnabled(True)
        self.button_stop.setEnabled(False)

    def closeEvent(self, event):
        if self.timer.isActive():
            self.timer.stop()
        event.accept()

    # ===========================================
    # Strategy Core
    # ===========================================
    def prepare_breakout_levels(self, k: float):
        """pykrx로 각 종목의 직전 거래일 OHLC를 가져와 돌파 레벨 계산."""
        self.breakout = {}
        today = datetime.now().date()
        start = (today - timedelta(days=14)).strftime("%Y%m%d")
        end   = (today - timedelta(days=1)).strftime("%Y%m%d")

        for code in self.codes:
            df = stock.get_market_ohlcv_by_date(start, end, code)
            if df is None or df.empty:
                raise RuntimeError(f"{code} 직전 거래일 데이터 조회 실패")

            last = df.iloc[-1]
            high = float(last["고가"])
            low  = float(last["저가"])
            close= float(last["종가"])
            level = close + k * (high - low)
            self.breakout[code] = level

    def on_tick(self):
        """10초마다 호출: 시세 갱신, 돌파 체크, 15:00 일괄 매도."""
        if not self.running or not self.codes:
            return

        now = datetime.now()
        hhmmss = now.strftime("%H:%M:%S")

        # ---- 15:00 일괄 매도 또는 15:00 이후 조회 중단 처리 ----
        if now.time() >= self.sell_time and not self.sell_executed_today:
            if self.bought:
                # 보유 종목이 있으면 매도 주문 실행
                for code in list(self.bought):
                    # (로그용) 매도 직전 1회 현재가 조회는 허용
                    info = self.fetch_basic_info(code)
                    if info is None:
                        self.send_order_sell_market(code, 1)
                        self.append_buysell_log(code, "", 0, 1, side="매도")
                        self.bought.discard(code)
                        QTest.qWait(self.rate_wait_ms)
                        continue

                    self.send_order_sell_market(code, 1)
                    self.append_buysell_log(code, info["name"], info["price"], 1, side="매도")
                    self.bought.discard(code)
                    QTest.qWait(self.rate_wait_ms)

                self.sell_executed_today = True
                # (요구 1) 매도 주문 전송 후, 모든 종목 현재가 조회 중단
                self.price_queries_disabled_today = True
                return  # 이 틱에서 더 이상 조회/판단 안 함
            else:
                # (요구 2) 당일 매도할 주식이 없으면 15시 이후 현재가 조회 중단
                self.sell_executed_today = True
                self.price_queries_disabled_today = True
                return

        # 이미 중단 플래그가 켜졌다면 즉시 종료
        if self.price_queries_disabled_today:
            return

        # ---- 종목별 현재가 조회 + 로그 (단, 매수 완료 종목은 조회하지 않음) ----
        lines = []
        for code in self.codes:
            if code in self.bought:
                continue  # 하루 1회 매수: 매수 후 조회 중단

            info = self.fetch_basic_info(code)
            if info is None:
                lines.append(f"[{hhmmss}] [{code}] [조회실패] [-]")
            else:
                name = info["name"]
                price = info["price"]
                lines.append(f"[{hhmmss}] [{code}] [{name}] [{price:,}]")

                # 15:00 이전에만 신규 매수 판단
                if now.time() < self.sell_time:
                    brk = self.breakout.get(code)
                    if brk is not None and price is not None and price > brk:
                        self.send_order_buy_market(code, 1)
                        self.append_buysell_log(code, name, price, 1, side="매수")
                        self.bought.add(code)

            if self.rate_wait_ms > 0:
                QTest.qWait(self.rate_wait_ms)

        if lines:
            self.textboard.append("\n".join(lines))
            self.textboard.moveCursor(self.textboard.textCursor().End)

    # ===========================================
    # Kiwoom Helpers
    # ===========================================
    def fetch_basic_info(self, code: str):
        """opt10001 (주식기본정보)로 종목명/현재가 반환."""
        try:
            df = self.kiwoom.block_request(
                "opt10001",
                종목코드=code,
                output="주식기본정보",
                next=0
            )
        except Exception:
            return None

        if df is None or not isinstance(df, pd.DataFrame) or df.empty:
            return None

        name = str(df.at[0, "종목명"]) if "종목명" in df.columns else ""
        raw_price = df.at[0, "현재가"] if "현재가" in df.columns else None
        try:
            price = abs(int(str(raw_price).replace(",", "")))
        except Exception:
            price = None

        if not name or price is None:
            return None
        return {"name": name, "price": price}

    def send_order_buy_market(self, code: str, qty: int):
        """시장가 신규매수 (OrderType=1, HogaGb='03')."""
        try:
            self.kiwoom.SendOrder(
                "신규매수",
                "0101",                # ScreenNo
                self.account,
                1,                     # 1: 신규매수
                code,
                qty,
                0,                     # 시장가 -> 0
                "03",                  # 03: 시장가
                ""                     # 원주문번호 (신규는 공백)
            )
        except Exception as e:
            self.buysell_log.append(f"[주문오류] [{code}] [{e}]")

    def send_order_sell_market(self, code: str, qty: int):
        """시장가 신규매도 (OrderType=2, HogaGb='03')."""
        try:
            self.kiwoom.SendOrder(
                "신규매도",
                "0102",
                self.account,
                2,                     # 2: 신규매도
                code,
                qty,
                0,
                "03",
                ""
            )
        except Exception as e:
            self.buysell_log.append(f"[주문오류] [{code}] [{e}]")

    def append_buysell_log(self, code: str, name: str, price: int, qty: int, side: str):
        """매매 로그: [매수|매도] [종목코드] [종목명] [가격] [수량]"""
        tag = "매수" if side == "매수" else "매도"
        price_str = f"{price:,}" if price else "-"
        line = f"[{tag}] [{code}] [{name}] [{price_str}] [{qty}]"
        self.buysell_log.append(line)
        self.buysell_log.moveCursor(self.buysell_log.textCursor().End)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
