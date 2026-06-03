import base64
import hashlib
import hmac
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

from dotenv import load_dotenv

load_dotenv()

PORT = int(os.getenv("PORT", "3000"))
SKIP_VERIFY = os.getenv("WEBHOOK_SKIP_VERIFY", "").lower() in ("1", "true", "yes")


def get_channel_secret() -> str:
    return (os.getenv("LINE_CHANNEL_SECRET") or "").strip()


def get_line_signature(headers) -> str | None:
    for key, value in headers.items():
        if key.lower() == "x-line-signature" and value:
            return value.strip()
    return None


def is_line_verify_request(body: bytes) -> bool:
    """LINE Developers の「検証」は events が空の POST のことがある"""
    try:
        payload = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError:
        return False
    return payload.get("events") == []


def verify_signature(body: bytes, signature: str | None, channel_secret: str) -> bool:
    if not channel_secret or not signature:
        return False
    digest = hmac.new(
        channel_secret.encode("utf-8"),
        body,
        hashlib.sha256,
    ).digest()
    expected = base64.b64encode(digest).decode("utf-8")
    return hmac.compare_digest(expected, signature)


def log_user_ids(events: list) -> None:
    for event in events:
        source = event.get("source") or {}
        user_id = source.get("userId")
        if not user_id:
            continue

        if event.get("type") == "follow":
            print("\n★ 友だち追加 — この userId を .env の LINE_USER_ID にコピー:")
            print(user_id)
        if event.get("type") == "message":
            print("\n★ メッセージ受信 — この userId を .env の LINE_USER_ID にコピー:")
            print(user_id)
            message = event.get("message") or {}
            if message.get("type") == "text":
                print("  本文:", message.get("text"))


class WebhookHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:
        return

    def do_GET(self) -> None:
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"LINE Webhook server is running.")
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/webhook":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        signature = get_line_signature(self.headers)
        channel_secret = get_channel_secret()

        if not signature and is_line_verify_request(body):
            print("LINE Webhook 検証リクエストを受理しました。", flush=True)
            self.send_response(200)
            self.end_headers()
            return

        if SKIP_VERIFY:
            print("注意: 署名検証をスキップしています (WEBHOOK_SKIP_VERIFY=1)", flush=True)
            if body:
                try:
                    log_user_ids(json.loads(body.decode("utf-8")).get("events", []))
                except json.JSONDecodeError:
                    pass
            self.send_response(200)
            self.end_headers()
            return

        if not verify_signature(body, signature, channel_secret):
            print("署名検証に失敗しました。", flush=True)
            if not channel_secret:
                print("  → .env の LINE_CHANNEL_SECRET が空です。", flush=True)
            elif not signature:
                print("  → X-Line-Signature ヘッダーがありません。", flush=True)
            else:
                print(
                    "  → チャネルシークレットが違う可能性があります。",
                    flush=True,
                )
                print(
                    "     LINE Developers → チャネル基本設定 → チャネルシークレット",
                    flush=True,
                )
                print(
                    "     をコピーし直して .env を更新し、サーバーを再起動してください。",
                    flush=True,
                )
            self.send_response(401)
            self.end_headers()
            return

        payload = json.loads(body.decode("utf-8"))
        log_user_ids(payload.get("events", []))

        self.send_response(200)
        self.end_headers()


def main() -> None:
    secret = get_channel_secret()
    server = HTTPServer(("", PORT), WebhookHandler)
    print(f"Webhook サーバー起動: http://localhost:{PORT}")
    print("Webhook URL に登録するパス: /webhook")
    if not secret:
        print("警告: .env に LINE_CHANNEL_SECRET を設定してください")
    else:
        print(f"チャネルシークレット読み込み済み（{len(secret)} 文字）")
    if SKIP_VERIFY:
        print("警告: WEBHOOK_SKIP_VERIFY=1（開発用・署名検証オフ）")
    server.serve_forever()


if __name__ == "__main__":
    main()
