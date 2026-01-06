# app_breakout.py
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
        # gui.ui에는 다음 objectName이 존재한다고 가정합니다.
        # code_list: QLineEdit, button_start: QPushButton, button_stop: QPushButton
        # textboard: QTextBrowser (시세 로그), k_value: QLineEdit, buysell_log: QTextBrowser
        uic.loadUi("gui.ui", self)

        # ---------- State ----------
        self.timer = QTimer(self)
        self.timer.setInterval(1000)  # 1초 주기
        self.timer.timeout.connect(self.on_tick)

        self.codes = []                 # 감시 종목
        self.running = False
        self.rate_wait_ms = 200         # TR 완화 (필요시 조정)
        self.breakout = {}              # code -> 돌파가격 (종가 + K*(H-L))
        self.bought = set()             # 금일 매수 완료한 종목 코드
        self.sell_executed_today = False
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
            # ACCNO는 '1234567890;0001112222' 형식의 문자열
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
        # 종목 코드 파싱
        raw = (self.code_list.text() or "").strip()
        codes = [c.strip() for c in raw.split(",") if c.strip()]
        if not codes:
            QMessageBox.warning(self, "입력 필요", "code_list에 종목 코드를 입력하세요. (예: 005930,000270)")
            return

        # K 값 파싱
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
        self.bought.clear()
        self.textboard.clear()
        self.buysell_log.clear()

        self.button_start.setEnabled(False)
        self.button_stop.setEnabled(True)

        # 직전 거래일 OHLC로 돌파 레벨 계산
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
        # 한국장 기준 오늘 날짜와 10영업일 범위로 조회
        today = datetime.now().date()
        start = (today - timedelta(days=14)).strftime("%Y%m%d")
        end   = (today - timedelta(days=1)).strftime("%Y%m%d")

        for code in self.codes:
            df = stock.get_market_ohlcv_by_date(start, end, code)
            if df is None or df.empty:
                raise RuntimeError(f"{code} 직전 거래일 데이터 조회 실패")

            # 마지막(가장 최근 거래일)의 OHLC
            last = df.iloc[-1]
            high = float(last["고가"])
            low  = float(last["저가"])
            close= float(last["종가"])
            level = close + k * (high - low)
            self.breakout[code] = level

    def on_tick(self):
        """1초마다 호출: 시세 갱신, 돌파 체크, 15:00 일괄 매도."""
        if not self.running or not self.codes:
            return

        now = datetime.now()
        hhmmss = now.strftime("%H:%M:%S")

        # 15:00 일괄 매도
        if (now.time() >= self.sell_time) and not self.sell_executed_today and self.bought:
            # 현재가 기준으로 모두 시장가 매도
            for code in list(self.bought):
                info = self.fetch_basic_info(code)  # name, price
                if info is None:
                    continue
                self.send_order_sell_market(code, 1)
                self.append_buysell_log(code, info["name"], info["price"], 1)
                # 보유 해제
                self.bought.discard(code)
                QTest.qWait(self.rate_wait_ms)

            self.sell_executed_today = True

        # 종목별 현재가 조회 + 로그
        lines = []
        for code in self.codes:
            info = self.fetch_basic_info(code)  # {"name":..., "price":...}
            if info is None:
                lines.append(f"[{hhmmss}] [{code}] [조회실패] [-]")
            else:
                name = info["name"]
                price = info["price"]
                lines.append(f"[{hhmmss}] [{code}] [{name}] [{price:,}]")

                # 15:00 이전에만 신규 매수 판단
                if now.time() < self.sell_time:
                    brk = self.breakout.get(code)
                    if brk is not None and code not in self.bought and price is not None:
                        if price > brk:
                            # 시장가 1주 매수
                            self.send_order_buy_market(code, 1)
                            self.append_buysell_log(code, name, price, 1)
                            self.bought.add(code)

            if self.rate_wait_ms > 0:
                QTest.qWait(self.rate_wait_ms)

        # 시세 로그 출력
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

    def append_buysell_log(self, code: str, name: str, price: int, qty: int):
        """매매 로그: [종목코드] [종목명] [매매가격] [매매수량]"""
        line = f"[{code}] [{name}] [{price:,}] [{qty}]"
        self.buysell_log.append(line)
        self.buysell_log.moveCursor(self.buysell_log.textCursor().End)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
