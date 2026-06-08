import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

YOUTUBE_SEARCH_ENDPOINT = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_CHANNELS_ENDPOINT = "https://www.googleapis.com/youtube/v3/channels"
YOUTUBE_PLAYLIST_ITEMS_ENDPOINT = "https://www.googleapis.com/youtube/v3/playlistItems"
YOUTUBE_VIDEOS_ENDPOINT = "https://www.googleapis.com/youtube/v3/videos"
TOP_N = 10
VIDEOS_BATCH_SIZE = 50


def load_api_key() -> str | None:
    api_key = os.getenv("YOUTUBE_API_KEY")
    if api_key:
        return api_key.strip()

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


def youtube_api_get(endpoint: str, params: dict) -> dict:
    url = f"{endpoint}?{urlencode(params)}"
    with urlopen(url) as response:
        payload = response.read().decode("utf-8")
    return json.loads(payload)


def search_channel(api_key: str, keyword: str) -> dict | None:
    data = youtube_api_get(
        YOUTUBE_SEARCH_ENDPOINT,
        {
            "part": "snippet",
            "q": keyword,
            "type": "channel",
            "maxResults": 1,
            "key": api_key,
        },
    )

    items = data.get("items", [])
    if not items:
        return None

    item = items[0]
    channel_id = item.get("id", {}).get("channelId")
    title = item.get("snippet", {}).get("title")
    if not channel_id or not title:
        return None

    return {"channel_id": channel_id, "title": title}


def get_uploads_playlist_id(api_key: str, channel_id: str) -> str | None:
    data = youtube_api_get(
        YOUTUBE_CHANNELS_ENDPOINT,
        {
            "part": "contentDetails",
            "id": channel_id,
            "key": api_key,
        },
    )

    items = data.get("items", [])
    if not items:
        return None

    return items[0].get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads")


def fetch_all_channel_videos(api_key: str, uploads_playlist_id: str) -> list[dict]:
    videos: list[dict] = []
    page_token: str | None = None

    while True:
        params = {
            "part": "snippet",
            "playlistId": uploads_playlist_id,
            "maxResults": VIDEOS_BATCH_SIZE,
            "key": api_key,
        }
        if page_token:
            params["pageToken"] = page_token

        data = youtube_api_get(YOUTUBE_PLAYLIST_ITEMS_ENDPOINT, params)

        for item in data.get("items", []):
            video_id = item.get("snippet", {}).get("resourceId", {}).get("videoId")
            title = item.get("snippet", {}).get("title")
            if video_id and title:
                videos.append({"video_id": video_id, "title": title})

        page_token = data.get("nextPageToken")
        if not page_token:
            break

    return videos


def fetch_view_counts(api_key: str, video_ids: list[str]) -> dict[str, int]:
    view_counts: dict[str, int] = {}

    for i in range(0, len(video_ids), VIDEOS_BATCH_SIZE):
        batch = video_ids[i : i + VIDEOS_BATCH_SIZE]
        data = youtube_api_get(
            YOUTUBE_VIDEOS_ENDPOINT,
            {
                "part": "statistics",
                "id": ",".join(batch),
                "key": api_key,
            },
        )

        for item in data.get("items", []):
            video_id = item.get("id")
            view_count_str = item.get("statistics", {}).get("viewCount")
            if video_id and view_count_str is not None:
                view_counts[video_id] = int(view_count_str)

    return view_counts


def rank_videos_by_views(videos: list[dict], view_counts: dict[str, int]) -> list[dict]:
    for video in videos:
        video["view_count"] = view_counts.get(video["video_id"], 0)
    return sorted(videos, key=lambda v: v["view_count"], reverse=True)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    api_key = load_api_key()

    if not api_key:
        print(
            "エラー: APIキーが見つかりません。.env に YOUTUBE_API_KEY=... を設定してください。",
            file=sys.stderr,
        )
        return 1

    channel_name = input("チャンネル名: ").strip()
    if not channel_name:
        print("エラー: チャンネル名が空です。", file=sys.stderr)
        return 1

    try:
        channel = search_channel(api_key, channel_name)
        if not channel:
            print(f"「{channel_name}」に一致するチャンネルが見つかりませんでした。")
            return 0

        uploads_playlist_id = get_uploads_playlist_id(api_key, channel["channel_id"])
        if not uploads_playlist_id:
            print(f"チャンネル「{channel['title']}」の動画一覧を取得できませんでした。")
            return 0

        print(f"チャンネル「{channel['title']}」の動画を取得中...")
        videos = fetch_all_channel_videos(api_key, uploads_playlist_id)
        if not videos:
            print(f"チャンネル「{channel['title']}」に動画がありません。")
            return 0

        video_ids = [video["video_id"] for video in videos]
        view_counts = fetch_view_counts(api_key, video_ids)
        top_videos = rank_videos_by_views(videos, view_counts)[:TOP_N]
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

    print(f"【{channel['title']}】全 {len(videos)} 本中 再生回数 TOP {TOP_N}")
    print()
    for i, video in enumerate(top_videos, start=1):
        print(f"{i}. {video['title']}")
        print(f"   再生回数: {video['view_count']:,} 回")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
