"""第1回: 素のLLMに会話履歴を保って質問するスクリプト。

使い方:
    uv run python -m app.ask "LoRAとは何ですか？"
    uv run python -m app.ask            # 質問を省略すると、講座に固有の質問をする

ツールは使わず、会話履歴を保って質問する「素の」呼び出し。
講座に固有のことを聞くと、「分からない」と答えるか、一般論でもっともらしく答える
（講座の実際とは違う）ことを確かめよう。
（第3回で、用語集を検索できるエージェントにして改善する）
"""

import argparse

from google import genai
from google.genai import errors

from app.config import MODEL, api_error_message, get_api_key

# 講座に固有の質問。正しい答えは data/glossary.json の homework-levels にある
DEFAULT_QUESTION = "AIE2026の講座の宿題にある「3レベル」とは何ですか？"


def ask(chat, question: str):
    return chat.send_message(question)


def main() -> None:
    parser = argparse.ArgumentParser(description="会話履歴を保って素のLLMに質問する")
    parser.add_argument("question", nargs="?", default=DEFAULT_QUESTION)
    args = parser.parse_args()

    client = genai.Client(api_key=get_api_key())
    chat = client.chats.create(model=MODEL)
    question = args.question
    try:
        while True:
            print(f"[質問] {question}\n")
            print("--------------------------")
            response = ask(chat, question)
            print("[回答]")
            print(response.text)
            print(f"[model] {MODEL}")
            usage = response.usage_metadata
            if usage is not None:
                print(f"[トークン数] 入力: {usage.prompt_token_count}, 出力: {usage.candidates_token_count}")
            else:
                print("[トークン数] 使用量メタデータがありません")
            print("--------------------------")
            print(
                "\n### 会話履歴は引き継がれます。コンテキストをリフレッシュするには、###"
                "\n### 一度プログラムを終了する必要があります（Ctrl+Cで終了）。###"
            )
            question = input("\n続けて質問: ")
    except (KeyboardInterrupt, EOFError):
        print("\n終了します。")
    except errors.APIError as e:
        print(api_error_message(e.code, e.message))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
