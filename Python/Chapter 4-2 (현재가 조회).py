# -*- coding: utf-8 -*-
from pykiwoom.kiwoom import Kiwoom

# Kiwoom 숫자 문자열(부호/콤마 포함)을 정수로 변환
def parse_num(x: str) -> int:
    s = str(x).strip().replace(",", "")
    # 현재가/전일대비는 하락 시 음수로 내려오는 경우가 있어 절대값으로 처리
    # (가격의 "크기"가 필요할 때는 abs, 증감 표시가 필요하면 부호 유지)
    return int(s)

def parse_price(x: str) -> int:
    # 화면 표시용: 가격은 절대값으로
    return abs(parse_num(x))

def get_current_price(kiwoom: Kiwoom, code: str) -> dict:
    df = kiwoom.block_request(
        "opt10001",
        종목코드=code,
        output="주식기본정보",  # ★ 필수
        next=0                 # ★ 첫 요청은 0
    )
    if df is None or df.empty:
        raise RuntimeError(f"조회 실패 or 빈 응답 (종목코드: {code})")

    row = df.iloc[0]
    price = parse_price(row["현재가"])
    name = row.get("종목명", code)

    # 부호 있는 전일대비/등락률 (표시용)
    diff = parse_num(row.get("전일대비", "0"))
    rate = str(row.get("등락률", "0")).replace("%", "")

    return {
        "name": name,
        "code": code,
        "price": price,           # 원
        "diff": diff,             # 전일대비 (부호 포함)
        "rate": rate              # 등락률(%, 문자열)
    }

def main():
    kiwoom = Kiwoom()
    kiwoom.CommConnect(block=True)  # 로그인 완료까지 대기

    targets = {
        "삼성전자": "005930",
        "현대자동차": "005380",
    }

    for label, code in targets.items():
        info = get_current_price(kiwoom, code)
        sign = "▲" if info["diff"] > 0 else ("▼" if info["diff"] < 0 else "─")
        print(f"{label}({info['code']}) 현재가: {info['price']:,}원  "
              f"{sign} {info['diff']:+,} ({info['rate']}%)")

if __name__ == "__main__":
    main()
