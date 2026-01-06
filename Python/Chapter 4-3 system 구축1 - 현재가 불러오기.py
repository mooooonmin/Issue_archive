# app.py
import sys
from datetime import datetime

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import QTimer
from PyQt5.QtTest import QTest

from pykiwoom.kiwoom import Kiwoom
import pandas as pd


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 1) Qt Designer로 만든 UI 로드 (파일명: gui.ui)
        #    gui.ui에는 다음 objectName을 사용했다고 가정합니다:
        #    - code_list : QLineEdit
        #    - button_start : QPushButton
        #    - button_stop  : QPushButton
        #    - textboard    : QTextBrowser
        uic.loadUi("gui.ui", self)

        # 2) 상태 변수
        self.timer = QTimer(self)
        self.timer.setInterval(1000)  # 1초마다 갱신
        self.timer.timeout.connect(self.update_prices)

        self.codes = []         # 사용자가 입력한 종목코드 리스트
        self.running = False
        self.rate_wait_ms = 200  # TR 제한 대응용 (필요 시 0~250ms 등으로 조정)

        # 3) 버튼 연결
        self.button_start.clicked.connect(self.on_start)
        self.button_stop.clicked.connect(self.on_stop)

        # 초기 버튼 상태
        self.button_stop.setEnabled(False)

        # 4) Kiwoom OpenAPI 로그인 (QApplication 생성 이후에 해야 함)
        try:
            self.kiwoom = Kiwoom()
            # 로그인 창 표시(동기)
            self.kiwoom.CommConnect(block=True)
        except Exception as e:
            QMessageBox.critical(self, "Kiwoom 로그인 실패", str(e))
            sys.exit(1)

    # =========================
    # 버튼 & 타이머 핸들러
    # =========================
    def on_start(self):
        # 종목코드 파싱 (콤마 구분)
        raw = (self.code_list.text() or "").strip()
        if not raw:
            QMessageBox.warning(self, "입력 필요", "code_list에 종목 코드를 입력하세요. (예: 005930,000270)")
            return

        # 공백 제거 및 빈 항목 제거
        codes = [c.strip() for c in raw.split(",") if c.strip()]
        if not codes:
            QMessageBox.warning(self, "입력 오류", "올바른 종목 코드를 입력하세요.")
            return

        self.codes = codes
        self.textboard.clear()  # 시작 전 상태로
        self.running = True

        self.button_start.setEnabled(False)
        self.button_stop.setEnabled(True)

        self.timer.start()

    def on_stop(self):
        # 모든 동작 중단 및 초기 상태 복귀
        self.timer.stop()
        self.running = False
        self.codes = []
        self.textboard.clear()

        self.button_start.setEnabled(True)
        self.button_stop.setEnabled(False)

    def closeEvent(self, event):
        # 종료 시 안전하게 타이머 정지
        if self.timer.isActive():
            self.timer.stop()
        event.accept()

    # =========================
    # 데이터 조회 & 로그 출력
    # =========================
    def update_prices(self):
        if not self.running or not self.codes:
            return

        timestamp = datetime.now().strftime("%H:%M:%S")
        lines = []

        for code in self.codes:
            try:
                info = self.fetch_basic_info(code)
                if info is None:
                    line = f"[{timestamp}] [{code}] [조회실패] [-]"
                else:
                    name = info["name"]
                    price = info["price"]
                    line = f"[{timestamp}] [{code}] [{name}] [{price:,}]"
                lines.append(line)

            except Exception as e:
                lines.append(f"[{timestamp}] [{code}] [오류] [{e}]")

            # TR 과다 요청 방지 (UI 멈춤 최소화를 위해 qWait 사용)
            if self.rate_wait_ms > 0:
                QTest.qWait(self.rate_wait_ms)

        # 한 번에 출력
        if lines:
            self.textboard.append("\n".join(lines))
            # 맨 아래로 스크롤
            self.textboard.moveCursor(self.textboard.textCursor().End)

    def fetch_basic_info(self, code: str):
        """
        opt10001 (주식기본정보) TR을 block_request로 호출하여
        종목명과 현재가를 반환합니다.
        반환: {"name": str, "price": int} 또는 None
        """
        # block_request 사용 시 'output' 인자를 반드시 지정해야 합니다.
        # opt10001의 output 블록명은 "주식기본정보" 입니다.
        df = self.kiwoom.block_request(
            "opt10001",
            종목코드=code,
            output="주식기본정보",
            next=0
        )

        if df is None or not isinstance(df, pd.DataFrame) or df.empty:
            return None

        # 컬럼 예시: ["종목코드","종목명","현재가", ...]
        name = str(df.at[0, "종목명"]) if "종목명" in df.columns else ""
        raw_price = df.at[0, "현재가"] if "현재가" in df.columns else None

        # 현재가는 부호가 포함된 문자열일 수 있음 → 정수 변환 후 절대값
        try:
            price = abs(int(str(raw_price).replace(",", "")))
        except Exception:
            price = None

        if not name or price is None:
            return None

        return {"name": name, "price": price}


if __name__ == "__main__":
    # 반드시 QApplication 생성 후 Kiwoom 사용
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
