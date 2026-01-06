# -*- coding: utf-8 -*-
from pykiwoom.kiwoom import Kiwoom

def to_int(x):
    return int(str(x).replace(",", "").strip())

def first_account_from(accno):
    # pykiwoom 버전에 따라 'ACCNO'는 리스트 또는 세미콜론 구분 문자열로 옵니다.
    if isinstance(accno, list):
        return accno[0].strip()
    return str(accno).split(";")[0].strip()

def main():
    kiwoom = Kiwoom()
    kiwoom.CommConnect(block=True)  # 로그인 대기

    accno_raw = kiwoom.GetLoginInfo("ACCNO")
    account = first_account_from(accno_raw)
    if not account:
        raise RuntimeError("계좌번호를 가져오지 못했습니다.")

    # opw00001: 예수금상세현황요청
    # 필수 입력: 계좌번호, 비밀번호, 비밀번호입력매체구분("00"), 조회구분(2:일반, 3:추정)
    df = kiwoom.block_request(
        "opw00001",
        계좌번호=account,
        비밀번호="",                # 실계좌는 필요 시 입력
        비밀번호입력매체구분="00",
        조회구분=2,
        output="예수금상세현황",     # ★ 반드시 지정
        next=0                      # ★ 첫 요청은 0
    )

    if df is None or df.empty:
        raise RuntimeError("예수금 조회 결과가 비었습니다. (모의/실계좌, 조회구분을 확인하세요)")

    # 환경에 따라 컬럼명이 다를 수 있어 후보를 순차 탐색
    cash_col_candidates = ["예수금", "예수금액", "추정예수금", "D+2추정예수금"]
    cash_col = next((c for c in cash_col_candidates if c in df.columns), None)
    if cash_col is None:
        print("반환 컬럼:", list(df.columns))
        raise RuntimeError("예수금 컬럼을 찾지 못했습니다. 위 컬럼을 참고해 코드의 컬럼명을 맞춰 주세요.")

    cash = to_int(df.iloc[0][cash_col])
    print(f"[계좌: {account}] {cash_col}: {cash:,} 원")

    if "출금가능금액" in df.columns:
        withdrawable = to_int(df.iloc[0]["출금가능금액"])
        print(f"출금가능금액: {withdrawable:,} 원")

if __name__ == "__main__":
    main()
