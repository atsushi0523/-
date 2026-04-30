import argparse
import os
import sys
from urllib.parse import urlencode
from urllib.request import urlopen
from urllib.error import HTTPError, URLError
import json


YOUTUBE_SEARCH_ENDPOINT = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_WATCH_URL = "https://www.youtube.com/watch"


def load_api_key() -> str | None:
    # Prefer environment variable first.
    api_key = os.getenv("YOUTUBE_API_KEY")
    if api_key:
        return api_key.strip()

    # Fallback: read .env in the current directory.
    env_path = ".env"
    if not os.path.exists(env_path):
        return None

    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                if key.strip() == "YOUTUBE_API_KEY":
                    return value.strip().strip('"').strip("'")
    except OSError:
        return None

    return None


def search_youtube_videos(api_key: str, keyword: str, max_results: int = 10) -> list[dict]:
    params = {
        "part": "snippet",
        "q": keyword,
        "type": "video",
        "maxResults": max_results,
        "key": api_key,
    }
    url = f"{YOUTUBE_SEARCH_ENDPOINT}?{urlencode(params)}"

    with urlopen(url) as response:
        payload = response.read().decode("utf-8")
        data = json.loads(payload)

    results = []
    for item in data.get("items", []):
        video_id = item.get("id", {}).get("videoId")
        title = item.get("snippet", {}).get("title")
        if not video_id or not title:
            continue
        video_url = f"{YOUTUBE_WATCH_URL}?v={video_id}"
        results.append({"title": title, "url": video_url})

    return results


def main() -> int:
    parser = argparse.ArgumentParser(
        description="YouTube Data API を使ってキーワード検索を行い、タイトルとURLを表示します。"
    )
    parser.add_argument("--keyword", help="検索キーワード")
    parser.add_argument(
        "--max-results",
        type=int,
        default=10,
        help="取得件数 (1〜50, デフォルト: 10)",
    )
    args = parser.parse_args()
    api_key = load_api_key()

    if not api_key:
        print(
            "エラー: APIキーが見つかりません。.env に YOUTUBE_API_KEY=... を設定してください。",
            file=sys.stderr,
        )
        return 1

    keyword = (args.keyword or "").strip()
    if not keyword:
        keyword = input("検索ワードを入力してください: ").strip()
    if not keyword:
        print("エラー: 検索ワードが空です。", file=sys.stderr)
        return 1

    if not (1 <= args.max_results <= 50):
        print("エラー: --max-results は 1〜50 の範囲で指定してください。", file=sys.stderr)
        return 1

    try:
        videos = search_youtube_videos(api_key, keyword, args.max_results)
    except HTTPError as e:
        message = e.read().decode("utf-8", errors="ignore")
        print(f"HTTPエラー: {e.code} {e.reason}", file=sys.stderr)
        if message:
            print(message, file=sys.stderr)
        return 1
    except URLError as e:
        print(f"接続エラー: {e.reason}", file=sys.stderr)
        return 1
    except json.JSONDecodeError:
        print("レスポンスのJSON解析に失敗しました。", file=sys.stderr)
        return 1

    if not videos:
        print("検索結果が見つかりませんでした。")
        return 0

    for i, video in enumerate(videos, start=1):
        print(f"{i}. {video['title']}")
        print(f"   {video['url']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
