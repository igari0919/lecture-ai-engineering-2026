# 第6回 解答

## 演習

<!-- [tool call] の行は、表示された行をそのまま貼り付けてください。終わらなかった STEP は、空欄のままでかまいません。 -->

- STEP 1 のツールの名前：[glossary_search_glossary]
- STEP 2 の [tool call]：[tool call]   glossary_search_glossary({'query': '3レベル'})
- STEP 3 の [tool call]：[tool call]   fetch_fetch({'url': 'https://modelcontextprotocol.io/'})
- STEP 4 の [tool call]：[tool call]   aws_aws___search_documentation({'search_phrase': 'Amazon S3 バージョニング 概要', 'topics': ['general']})
[tool return] aws_aws___search_documentation -> {'content': {'result': [{'rank_order': 1, 'title': 'querying-aws-s3', 'skill_description': 'Queries S3 object metadata, …
[tool call]   aws_aws___search_documentation({'search_phrase': '"Versioning" "Amazon S3" what is versioning', 'topics': ['general']})
- 気づき・疑問：思ったよりもMCPサーバの追加が楽だった。また、外部のツールを自分の環境に入れるより、外部のMCPサーバに聞きに行くほうがセキュアだと思った。

## 宿題

<!-- 基礎・実装・発展のどれか1つに取り組めば完了です。 -->

- 取り組んだレベル：実装
- やったこと：make_quizをMCPサーバ化
- 結果：第3回のクイズを出してもらったら、問題なく出題された。
- 気づき・疑問：ツールとして準備してあれば、MCPサーバ化はそれほど修正が要らないことが分かった。
