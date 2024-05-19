# OpenAI API x Streamlitで作る生成AIサービス

## chat.py
LangChain(OpenAI API)を用いてユーザとAIが対話を行うChatGPTクローン
#### 技術的特徴
- Dockerを用いてハード環境に依存しない開発の実現
- Streamlitを用いたWebアプリケーション化
- get_openai_callback()を用いてAPI利用料を都度UIから確認できる

## browsing.py
BeautifulSoupでリクナビから企業情報をスクレイピングしAIがその企業にあった人材を提示する
#### 技術的特徴
- BeautifulSoupを用いたスクレイピング実装
- build_prompt()でプロンプト設計を別に実装し、より求める結果を得る

## askDoc.py
専門知識を持たない通常の生成AIに、PDFをアップロードし知識の外付けをすることで実現した専門家AI
#### 技術的特徴
- 一般的な専門家AIであるRetrievalQAの進化版ConversationalRetrievalChain(継続的な質問が可能)を実装
- RecursiveCharacterTextSplitterでPDF文書を分割し管理することで、質問に回答するために最も参照すべき文書箇所を簡単に探せる
- ベクトルDBを活用してより正確により高速に文書の参照を行う
