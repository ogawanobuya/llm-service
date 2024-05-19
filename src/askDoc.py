import streamlit as st
from langchain.callbacks import get_openai_callback
from langchain.chat_models import ChatOpenAI

from PyPDF2 import PdfReader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Qdrant
from langchain.chains import RetrievalQA

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

QDRANT_PATH = "./local_qdrant"
COLLECTION_NAME = "my_collection"


def init_page():
    st.set_page_config(
        page_title="Master of PDF",
        page_icon="🐉"
    )
    st.sidebar.title("メニュー")


# 「PDF Upload」でPDFをテキストデータにする
def get_pdf_text():
    uploaded_file = st.file_uploader(
        label='Upload your PDF here',
        type='pdf'
    )
    if uploaded_file:
        pdf_reader = PdfReader(uploaded_file)
        # extract_text())でファイルからテキスト抽出
        text = '\n\n'.join([page.extract_text() for page in pdf_reader.pages])
        # 「RecursiveCharacterTextSplitter」は複数のセパレータ(\n\nから順に)を使って、chunk_sizeを満たすまで再帰的にテキストを分割
        # 「from_tiktoken_encoder」はテキストを分割するサイズ規定であるchunk_sizeがデフォルトで文字数であるのを「トークン数」に変える
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            # 適切なchunk sizeは質問対象のPDFによって変わる→大きいと内容が混ざり特徴のないEmbeddingになり質問に合う箇所を探せない・小さいとchunkに十分なサイズの文脈が入らない
            chunk_size=150,
            # chunk_overlapはchunk間で文字を被らせることができ、分割する際に段落間で文脈を維持したい場合などに有効
            chunk_overlap=0,
            # 日本語文章用などデフォルトセパレータに追加したい時
            separators=["\n\n", "\n", "。", "、", " ", ""],
        )
        return text_splitter.split_text(text)
    else:
        return None

# 「PDF Upload」「Ask PDF」でベクトルDBの立ち上げ
def load_qdrant():
    client = QdrantClient(path=QDRANT_PATH)
    # Qdrant cloudへの保存
    # client = QdrantClient(
    #     url="Qdrant CloudのURL",
    #     api_key="Qdrant CloudのAPIキー"
    # )

    # すべてのコレクション名を取得
    collections = client.get_collections().collections
    collection_names = [collection.name for collection in collections]

    # コレクションが存在しなければ作成
    if COLLECTION_NAME not in collection_names:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
        )
        print('************collection created!************')

    # langchainの「Qdrant」は与えられたテキストを指定モデルを用いてEmbedding化し、ベクトルDBのclientを用いて、生成したEmbeddingをcollection_nameに保管する
    return Qdrant(
        client=client,
        collection_name=COLLECTION_NAME, 
        embeddings=OpenAIEmbeddings()
    )

# 「PDF Upload」でベクトルDBに格納して、次にあるテキストをEmbedding(ベクトルデータ)にした際、その類似のEmbedding(すなわち類似文書)を高速に検索できる
def build_vector_store(pdf_text):
    qdrant = load_qdrant()
    # add_texts()でQdrantにベクトルDBへの保管をさせる
    qdrant.add_texts(pdf_text)


# 「Ask PDF」で質疑応答するためのAIモデルを作る
def build_qa_model(llm):
    # 入力だけでなく出力の際もDBを立ち上げる
    qdrant = load_qdrant()
    retriever = qdrant.as_retriever(
        # どんな観点からデータを取得するか(similarityはベクトルDBを構築したときに設定した距離関数で類似度を計算)
        search_type="similarity",
        # 類似する上位何件のchunkを取り出すか？
        search_kwargs={"k": 3}
    )
    # from_chain_typeは複数のチャンクの連結処理をする
    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff", 
        retriever=retriever,
        # 回答のために参照したchunkをresultと共に返す
        return_source_documents=True,
    )



def page_pdf_upload_and_build_vector_db():
    st.title("PDF Upload")
    # PDFファイルをアップし、テキストデータ(chunkに分割している)に変換
    pdf_text = get_pdf_text()
    if pdf_text:
        with st.spinner("Loading PDF ..."):
            # テキストデータをベクトルデータに変換し、Qdrantデータベースに保存
            build_vector_store(pdf_text)


def page_ask_my_pdf():
    st.title("Ask PDF")
    model_name = "gpt-3.5-turbo-0125"
    llm = ChatOpenAI(temperature=0, model_name=model_name)
    answer = None

    if query := st.text_input("質問: ", key="input"):
        qa = build_qa_model(llm)
        if qa:
            with st.spinner("ChatGPT is typing ..."):
                answer = qa(query)
                answer = answer["result"]
        else:
            answer = None

    if answer:
        st.markdown("## 回答")
        st.write(answer)


def main():
    selection = st.sidebar.radio("ページ切り替え", ["PDF Upload", "Ask PDF"])
    if selection == "PDF Upload":
        page_pdf_upload_and_build_vector_db()
    elif selection == "Ask PDF":
        page_ask_my_pdf()


if __name__ == '__main__':
    init_page()
    main()

# プログラムの流れ
# PDF Upload: PDFアップロード→テキスト抽出しベクトル化→ベクトルデータをQdrantに保存
# Ask PDF: 質問を入力→「質問をベクトル化する→Qdrantから質問ベクトルに近いchunkを抜き出す→chunkをベクトルからテキストに戻しRetrievalQAデフォルトプロンプトに挿入→llmモデルにプロンプトを流し回答を得る」→回答表示
# 「」の部分は全てRetrievalQAが行う