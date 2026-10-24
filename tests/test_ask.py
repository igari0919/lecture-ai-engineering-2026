import sys

from app import ask as ask_module


class FakeChat:
    def __init__(self):
        self.questions = []

    def send_message(self, question):
        self.questions.append(question)
        usage = type("Usage", (), {"prompt_token_count": 7, "candidates_token_count": 577})()
        return type("Response", (), {"text": f"回答: {question}", "usage_metadata": usage})()


def test_main_reuses_chat_for_follow_up_questions(monkeypatch, capsys):
    chat = FakeChat()
    fake_client = type("Client", (), {"chats": type("Chats", (), {"create": lambda self, **kwargs: chat})()})()
    monkeypatch.setattr(ask_module.genai, "Client", lambda **kwargs: fake_client)
    monkeypatch.setattr(ask_module, "get_api_key", lambda: "test-key")
    monkeypatch.setattr(sys, "argv", ["app.ask", "最初の質問"])

    questions = iter(["続きの質問"])

    def input_question(_prompt):
        try:
            return next(questions)
        except StopIteration:
            raise KeyboardInterrupt

    monkeypatch.setattr("builtins.input", input_question)

    ask_module.main()

    assert chat.questions == ["最初の質問", "続きの質問"]
    output = capsys.readouterr().out
    assert output.count("コンテキストをリフレッシュするには") == len(chat.questions)
    assert output.count("Ctrl+Cで終了") == len(chat.questions)
    assert output.count(f"[model] {ask_module.MODEL}") == len(chat.questions)
    assert output.count("[回答]") == len(chat.questions)
    assert output.count("[トークン数] 入力: 7, 出力: 577") == len(chat.questions)
    assert output.count("--------------------------") == 2 * len(chat.questions)

    first_question = output.index("[質問] 最初の質問")
    first_separator = output.index("--------------------------", first_question)
    first_answer = output.index("[回答]", first_separator)
    first_response = output.index("回答: 最初の質問", first_answer)
    first_model = output.index(f"[model] {ask_module.MODEL}", first_response)
    first_usage = output.index("[トークン数] 入力: 7, 出力: 577", first_model)
    assert first_question < first_separator < first_answer < first_response < first_model < first_usage