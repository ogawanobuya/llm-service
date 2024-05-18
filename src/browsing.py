import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.schema import (SystemMessage, HumanMessage, AIMessage)
from langchain.callbacks import get_openai_callback

import requests
from bs4 import BeautifulSoup

def init_page():
    st.set_page_config(
        page_title="AI Recruit Adviser",
        page_icon="🐷"
    )
    st.header("AI採用コンサル🐷")


def init_messages():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            SystemMessage(content="You are a recruit consultant.")
        ]


def get_content(url):
    try:
        with st.spinner("サイト情報取得中 ..."):
            # スクレイピングでURL先の情報取得
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            # <main>の中の"テキストデータ"を取得
            return soup.main.get_text()
    except:
        st.write('スクレイピングエラー発生')
        return None


# より要望に沿う結果を得るために適切なプロンプトを作成する
def build_prompt(content, n_chars=300):
    return f"""以下はとある企業の採用ページである。事業内容と会社の魅力からその企業が採用すべき人材のスキルと価値観を{n_chars}字程度の日本語で答えてください。
========
{content[:1000]}
========
"""


def main():

    model_name = "gpt-3.5-turbo-0125"
    llm = ChatOpenAI(temperature=0, model_name=model_name)
    answer = None

    # 入力フォームからURLを取得
    if url := st.text_input("URL: ", key="input"):
        content = get_content(url)
        if content:
            prompt = build_prompt(content)
            st.session_state.messages.append(HumanMessage(content=prompt))
            with st.spinner("ChatGPT is typing ..."):
                answer = llm(st.session_state.messages)
                answer = answer.content
        else:
            answer = None

    if answer:
        st.markdown("## 要約")
        st.write(answer)
        st.markdown("---")
        st.markdown("## 原文")
        st.write(content)


if __name__ == '__main__':
    init_page()
    init_messages()
    main()
