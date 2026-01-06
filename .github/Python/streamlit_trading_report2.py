# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import time
import pandas as pd
from pykiwoom.kiwoom import Kiwoom

# 개별 날짜 1건 조회 + "기준날짜" 컬럼 추가
def fetch_day_journal(kiwoom, account, password, date_str,
                      danju=2,        # 1: 당일매수에 대한 당일매도, 2: 당일매도전체
                      cash_credit=0   # 0: 전체, 1: 현금만, 2: 신용만
                      ):
    df = kiwoom.block_request(
        "opt00000",
        계좌번호=account,
        비밀번호=password,
        기준일자=date_str,     # YYYYMMDD
        단주구분=danju,
        현금신용구분=cash_credit,
        output="당일매매일지",  # opt10170의 출력 레코드명
        next=0
    )
    if df is not None and not df.empty:
        df["기준날짜"] = date_str
    return df


def get_accounts(kiwoom) -> list[str]:
    """pykiwoom 버전/환경에 따라 ACCNO가 str 또는 list로 오는 것을 모두 처리"""
    acc_raw = kiwoom.GetLoginInfo("ACCNO")

    # 1) 이미 list/tuple인 경우
    if isinstance(acc_raw, (list, tuple)):
        return [a for a in acc_raw if a]

    # 2) 문자열로 오는 경우: '123;456;' 형태
    if isinstance(acc_raw, str):
        return [a for a in acc_raw.split(";") if a.strip()]

    # 3) 혹시 모를 dict 형태까지 방어
    if isinstance(acc_raw, dict):
        for key in ("ACCNO", "accno", "accounts"):
            if key in acc_raw:
                v = acc_raw[key]
                if isinstance(v, (list, tuple)):
                    return [a for a in v if a]
                if isinstance(v, str):
                    return [a for a in v.split(";") if a.strip()]

def main():
    kiwoom = Kiwoom()
    kiwoom.CommConnect(block=True)

    accounts = get_accounts(kiwoom)
    if not accounts:
        raise RuntimeError("로그인된 계좌를 찾지 못했습니다. HTS/모의투자 로그인 상태 및 권한을 확인하세요.")

    account = accounts[0]  # 첫 계좌 사용
    print("사용 계좌:", account)

    # 3) 계좌 비밀번호(필요 시 입력)
    PASSWORD = ""  # 비번 필요 없으면 빈 문자열 유지, 필요하면 입력하세요.

    # 4) 조회 기간 설정: 오늘 포함 과거 15일
    end_date = datetime.today()
    days = 15

    frames = []
    for i in range(days):
        d = end_date - timedelta(days=i)
        date_str = d.strftime("%Y%m%d")

        try:
            df = fetch_day_journal(kiwoom, account, PASSWORD, date_str,
                                   danju=2,        # 당일매도전체
                                   cash_credit=0)  # 전체
            if df is not None and not df.empty:
                frames.append(df)
                print(f"{date_str}: {len(df)} rows")
            else:
                print(f"{date_str}: no data")
        except Exception as e:
            print(f"{date_str}: error -> {e}")

        # 5) TR 사이 0.5초 대기
        time.sleep(0.5)

    # 6) 합치고 CSV 저장
    if frames:
        all_df = pd.concat(frames, ignore_index=True)
    else:
        all_df = pd.DataFrame()

    out_path = "매매일지.csv"
    all_df.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"Saved {len(all_df)} rows to {out_path}")

if __name__ == "__main__":
    main()
