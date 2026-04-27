import argparse
import base64
import os
from email.message import EmailMessage
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Gmail API で送信のみを許可するスコープ
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

# 特定の宛先（必要に応じて変更）
DEFAULT_TO_EMAIL = "recipient@example.com"


def get_gmail_service(
    credentials_path: Path = Path("credentials.json"),
    token_path: Path = Path("token.json"),
):
    creds = None

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not credentials_path.exists():
                raise FileNotFoundError(
                    "credentials.json が見つかりません。Google Cloud で OAuth クライアントを作成し、"
                    "このファイル名で同じフォルダに配置してください。"
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
            creds = flow.run_local_server(port=0)

        with token_path.open("w", encoding="utf-8") as token_file:
            token_file.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def send_email(
    service,
    to_email: str,
    subject: str,
    body: str,
    from_email: str = "me",
):
    message = EmailMessage()
    message["To"] = to_email
    message["From"] = from_email
    message["Subject"] = subject
    message.set_content(body)

    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    create_message = {"raw": encoded_message}

    sent = service.users().messages().send(userId="me", body=create_message).execute()
    return sent["id"]


def parse_args():
    parser = argparse.ArgumentParser(description="Gmail API でメールを送信します。")
    parser.add_argument(
        "--to",
        default=os.getenv("GMAIL_TO_EMAIL", DEFAULT_TO_EMAIL),
        help=f"送信先メールアドレス（未指定時: {DEFAULT_TO_EMAIL}）",
    )
    parser.add_argument(
        "--subject",
        default="Gmail API テストメール",
        help="件名",
    )
    parser.add_argument(
        "--body",
        default="PythonからGmail APIで送信したテストメールです。",
        help="本文",
    )
    parser.add_argument(
        "--from-email",
        dest="from_email",
        default="me",
        help='送信者メールアドレス（通常は "me" を指定）',
    )
    return parser.parse_args()


def prompt_required(label: str, default: str | None = None) -> str:
    while True:
        if default:
            value = input(f"{label} [{default}]: ").strip()
            if not value:
                value = default
        else:
            value = input(f"{label}: ").strip()

        if value:
            return value

        print(f"{label} は必須です。もう一度入力してください。")


def prompt_multiline_body(default: str) -> str:
    print("\n本文を入力してください。")
    print("複数行入力する場合は、入力を終えたら単独で . を入力してください。")
    print("そのまま Enter のみを押すとデフォルト本文を使います。\n")

    lines = []
    first_line = input()

    if first_line.strip() == "":
        return default

    if first_line.strip() == ".":
        return default

    lines.append(first_line)

    while True:
        line = input()
        if line.strip() == ".":
            break
        lines.append(line)

    return "\n".join(lines).strip() or default


def collect_email_inputs(args):
    print("=== Gmail 送信情報を入力してください ===")
    to_email = prompt_required("宛先メールアドレス", args.to)
    subject = prompt_required("件名", args.subject)
    body = prompt_multiline_body(args.body)
    from_email = prompt_required("送信者メールアドレス", args.from_email)
    return to_email, subject, body, from_email


def main():
    args = parse_args()

    try:
        to_email, subject, body, from_email = collect_email_inputs(args)
        service = get_gmail_service()
        message_id = send_email(
            service=service,
            to_email=to_email,
            subject=subject,
            body=body,
            from_email=from_email,
        )
        print(f"送信成功: message_id={message_id}")
    except FileNotFoundError as e:
        print(f"設定エラー: {e}")
    except HttpError as e:
        print(f"Gmail API エラー: {e}")


if __name__ == "__main__":
    main()
