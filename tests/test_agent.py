"""エージェントの配線テスト。

TestModel は実際のLLMを呼ばない偽モデルで、登録されたツールを全部呼んでから
ダミーの回答を返す。APIキーも利用枠も使わずに、
「ツールが登録され、呼ばれ、結果がモデルに戻るか」を確かめられる。
"""

import json

from pydantic_ai.messages import ToolCallPart, ToolReturnPart
from pydantic_ai.models.test import TestModel

from app.agent import agent, quiz_log_details, run_interactive_chat
from app import tools

BASE_TOOLS = {"search_glossary", "get_lecture_summary", "make_quiz"}


def _parts(result, kind):
    return [p for m in result.all_messages() for p in m.parts if isinstance(p, kind)]


def test_base_tools_are_registered_and_called():
    model = TestModel()
    with agent.override(model=model):
        result = agent.run_sync("LoRAとは？")

    offered = {t.name for t in model.last_model_request_parameters.function_tools}
    assert BASE_TOOLS <= offered  # 演習でツールを足しても壊れないよう「含む」で判定

    called = {p.tool_name for p in _parts(result, ToolCallPart)}
    assert BASE_TOOLS <= called
    assert len(_parts(result, ToolReturnPart)) == len(_parts(result, ToolCallPart))
    assert result.output


def test_glossary_result_reaches_the_model():
    model = TestModel(call_tools=["search_glossary"])
    with agent.override(model=model):
        result = agent.run_sync("RAGとは？")
    returns = _parts(result, ToolReturnPart)
    assert returns and returns[0].tool_name == "search_glossary"


def test_interactive_chat_saves_final_answer_after_user_approval(tmp_path, monkeypatch):
    monkeypatch.setattr(tools, "LEARNING_LOG_DIR", tmp_path)
    prompts = iter(["y", ""])
    monkeypatch.setattr("builtins.input", lambda _: next(prompts))

    class Result:
        output = "LLMの正解です。"

        def all_messages(self):
            return []

    class Target:
        def run_sync(self, question, *, model, message_history):
            return Result()

    run_interactive_chat(Target(), model=None, initial_question="質問者の入力")

    entry = json.loads(next(tmp_path.glob("*.jsonl")).read_text(encoding="utf-8"))
    assert entry["question"] == "質問者の入力"
    assert entry["answer"] == "LLMの正解です。"


def test_quiz_log_details_uses_actual_quiz_return():
    class Result:
        def all_messages(self):
            return [
                type(
                    "Message",
                    (),
                    {
                        "parts": [
                            ToolCallPart(
                                tool_name="make_quiz",
                                args={"lecture": 3},
                                tool_call_id="quiz-call",
                            ),
                            ToolReturnPart(
                                tool_name="make_quiz",
                                content=json.dumps(
                                    {
                                        "question": "「LoRA」の意味は？",
                                        "answer": "低ランク適応。",
                                    },
                                    ensure_ascii=False,
                                ),
                                tool_call_id="quiz-call",
                            ),
                        ]
                    },
                )()
            ]

    assert quiz_log_details(Result()) == (
        3,
        "「LoRA」の意味は？ 答え: 低ランク適応。",
    )


def test_interactive_chat_passes_previous_turns_as_history(monkeypatch):
    prompts = iter(["n", "続きの質問", "n", ""])
    monkeypatch.setattr("builtins.input", lambda _: next(prompts))

    class Result:
        def __init__(self, prompt):
            self.output = f"回答: {prompt}"

        def all_messages(self):
            return [self.output]

    class Target:
        def __init__(self):
            self.calls = []

        def run_sync(self, prompt, *, model, message_history):
            self.calls.append((prompt, message_history))
            return Result(prompt)

    target = Target()
    run_interactive_chat(target, model=None, initial_question="最初の質問")

    assert target.calls == [
        ("最初の質問", None),
        ("続きの質問", ["回答: 最初の質問"]),
    ]
