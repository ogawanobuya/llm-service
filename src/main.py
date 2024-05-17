import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.schema import (SystemMessage, HumanMessage, AIMessage)


def main():
	# temperatureが大きくなるほど自由度に富んだ返答が返ってくる
    llm = ChatOpenAI(temperature=0)

    st.set_page_config(
        page_title="My First ChatGPT",
        page_icon="💩"
    )
    st.header("My First ChatGPT 💩")

    # チャット履歴の初期化
    if "messages" not in st.session_state:
    	# ここで初めて「messages」キーを持つ
        st.session_state.messages = [
        # 対話AIの設定を書く(ex. 返答は全て関西弁で行なってください)
            SystemMessage(content="You are a helpful assistant.")
        ]

    # ユーザーの入力を監視
    if user_input := st.chat_input("聞きたいことを入力してね！"):
        st.session_state.messages.append(HumanMessage(content=user_input))
        # Streamlitにおける「with」とは<div>のようなもの
        with st.spinner("ChatGPT is typing ..."):
        	# responseの中身「content="AI's response" additional_kwargs={} example=False」
        	# responseの型「<class 'langchain.schema.AIMessage'>」
            response = llm(st.session_state.messages)
        st.session_state.messages.append(AIMessage(content=response.content))

    # チャット履歴の表示
    messages = st.session_state.get('messages', [])
    for message in messages:
        if isinstance(message, AIMessage):
        	# st.chat_messageで囲むことでメッセージの頭にroleに応じたアイコンが付く
            with st.chat_message('assistant'):
                st.markdown(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message('user'):
                st.markdown(message.content)
        else:  # isinstance(message, SystemMessage):
            st.write(f"System message: {message.content}")


if __name__ == '__main__':
    main()

# 解説
# ChatGPT APIはステートレスなAPIで今までの話の内容を全く覚えていないので、毎回質問をするたびに今までの話の内容を教えてあげないといけない
# そこで今回のAIチャットでは「session_state」に「messages」というキーを設定し、そこにチャットの履歴を記録し、新たな質問をする際には必ず過去の履歴を送信するようにしている