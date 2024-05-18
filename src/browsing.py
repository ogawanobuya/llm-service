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
    st.write('このサービスはリクナビに載っている企業の募集要項URLを入力すると、その企業にあった人材の特性をAIがアドバイスします。')


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
            # セレクタで指定の要素を取得(リクナビ企業募集要項に特化)
            element = soup.select("body > div.ts-p-l-root > div.ts-p-l-body > div.ts-p-company-individualArea")
            return element[0].get_text()
    except:
        st.write('このサービスはリクナビに特化しているので、URLを改めてください')
        return None


# より要望に沿う結果を得るために適切なプロンプトを作成する
def build_prompt(content, n_chars=240):
    return f"""以下はある企業の採用ページである。その企業の事業内容と魅力から、その企業が採用すべき人材のスキルと価値観を{n_chars}字程度の日本語で答えてください。
========
{content[:700]}
========
"""


def main():

    model_name = "gpt-3.5-turbo-0125"
    llm = ChatOpenAI(temperature=0, model_name=model_name)
    answer = None

    # 入力フォームからURLを取得
    if url := st.text_input("リクナビURL: ", key="input"):
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
        st.markdown("## AIの答え")
        st.write(answer)


if __name__ == '__main__':
    init_page()
    init_messages()
    main()
