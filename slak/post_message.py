#!/usr/bin/env python3
"""指定チャンネルに Slack メッセージを投稿するスクリプト。

事前準備:
  - Slack アプリを作成し、Bot User OAuth Token を取得する
  - OAuth スコープに chat:write を追加する
  - 対象チャンネルにボットを招待する（またはパブリックチャンネルで適切な権限）

環境変数 (.env からも自動読み込み):
  SLACK_BOT_TOKEN  Bot の OAuth Token（xoxb- で始まる）
  SLACK_CHANNEL    投稿先チャンネル ID または #channel-name
"""

from __future__ import annotations

import argparse
import os
import sys

from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def post_message(client: WebClient, channel: str, text: str) -> bool:
    try:
        response = client.chat_postMessage(channel=channel, text=text)
    except SlackApiError as e:
        print(f"Slack API エラー: {e.response['error']}", file=sys.stderr)
        if e.response.get("response_metadata", {}).get("messages"):
            for msg in e.response["response_metadata"]["messages"]:
                print(msg, file=sys.stderr)
        return False

    ts = response.get("ts")
    ch = response.get("channel")
    print(f"投稿しました channel={ch} ts={ts}")
    return True


def read_message_from_stdin() -> str:
    # 対話実行時は 1 行入力、パイプ実行時は標準入力を全文読む
    if sys.stdin.isatty():
        try:
            return input("送信するメッセージを入力してください: ").strip()
        except EOFError:
            return ""
    return sys.stdin.read().strip()


def main() -> int:
    # カレントディレクトリの .env を読み込む（既存の環境変数は上書きしない）
    load_dotenv(override=False)

    parser = argparse.ArgumentParser(
        description="Slack の指定チャンネルにメッセージを投稿します。"
    )
    parser.add_argument(
        "text_parts",
        nargs="*",
        metavar="text",
        help="投稿するテキスト（SLACK_CHANNEL または -c があるときはここだけで可）",
    )
    parser.add_argument(
        "-c",
        "--channel",
        default=os.environ.get("SLACK_CHANNEL"),
        help="投稿先チャンネル（省略時は .env / 環境変数 SLACK_CHANNEL）",
    )
    parser.add_argument(
        "-t",
        "--token",
        default=os.environ.get("SLACK_BOT_TOKEN"),
        help="Bot Token（省略時は .env / 環境変数 SLACK_BOT_TOKEN）",
    )
    args = parser.parse_args()

    if not args.token:
        print(
            "エラー: Bot Token が指定されていません。"
            " --token で渡すか、.env または環境変数 SLACK_BOT_TOKEN を設定してください。",
            file=sys.stderr,
        )
        return 1

    channel = args.channel
    parts = list(args.text_parts)
    is_interactive_loop = (
        bool(args.channel)
        and not parts
        and sys.stdin.isatty()
    )

    if channel:
        if parts:
            text = " ".join(parts).strip()
        elif is_interactive_loop:
            text = ""  # 連続投稿モードではループ内で読む
        else:
            text = read_message_from_stdin()
    elif len(parts) >= 2:
        channel = parts[0]
        text = " ".join(parts[1:]).strip()
    elif len(parts) == 1:
        print(
            "エラー: 投稿先チャンネルが分かりません。"
            " .env の SLACK_CHANNEL を設定するか、-c で指定してください。"
            " （チャンネル未設定のときは「チャンネル メッセージ」の順で 2 つ以上並べてください。）",
            file=sys.stderr,
        )
        return 1
    else:
        print(
            "エラー: メッセージを指定するか、標準入力から本文を渡してください。",
            file=sys.stderr,
        )
        return 1

    if not text.strip() and not is_interactive_loop:
        print("エラー: 投稿するテキストが空です。", file=sys.stderr)
        return 1

    client = WebClient(token=args.token)
    if is_interactive_loop:
        print("連続投稿モードです。終了するには /exit を入力してください。")
        while True:
            line = read_message_from_stdin()
            if not line:
                continue
            if line in {"/exit", "/quit"}:
                break
            if not post_message(client, channel, line):
                return 1
        return 0

    return 0 if post_message(client, channel, text) else 1


if __name__ == "__main__":
    raise SystemExit(main())
