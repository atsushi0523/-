FAQ_MENU_TEXT = """【FAQメニュー】

1. 営業時間
2. 所在地
3. お問い合わせ

番号を送信してください。"""

FAQ_ANSWERS = {
    "1": "営業時間は10:00〜18:00です。",
    "2": "所在地は名古屋市〇〇区です。",
    "3": "お問い合わせ先は〇〇@example.comです。",
}

DEFAULT_REPLY = "『メニュー』と送信してください。"


def get_faq_reply(text: str) -> str:
    """ユーザー入力に対するFAQボットの返信文を返す"""
    message = text.strip()
    if message == "メニュー":
        return FAQ_MENU_TEXT
    if message in FAQ_ANSWERS:
        return FAQ_ANSWERS[message]
    return DEFAULT_REPLY
