from openai import OpenAI


def summarize_messages(api_key: str, messages: list[dict]) -> str:
    if not messages:
        return "取得したメッセージはありませんでした。"

    formatted = "\n".join(
        f"- [{m['posted_at']}] {m['user']}: {m['text']}" for m in messages if m["text"]
    )

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "あなたはSlackチャンネルのメッセージを要約するアシスタントです。"
                    "日本語で簡潔にまとめ、重要なトピック・決定事項・アクションがあれば箇条書きで示してください。"
                ),
            },
            {
                "role": "user",
                "content": f"以下のSlackメッセージ（最新{len(messages)}件）を要約してください:\n\n{formatted}",
            },
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content.strip()
