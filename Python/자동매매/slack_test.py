import requests

WEBHOOK_URL = ""  # 본인 웹훅 URL
requests.post(WEBHOOK_URL, json={"text": "안녕하세요, 웹훅 테스트입니다! 메시지를 변경하겠습니다."})
