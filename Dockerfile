FROM python:3.9-bullseye

# このDockerfile内限定で使用できる環境変数
ARG dir=/workdir

# コンテナに入った後の初期ディレクトリとして指定(無ければ自動作成される)、いわゆる「cd /workdir」と同じ
WORKDIR $dir

# この時すでにWORKDIRによって、コンテナ内での作業ディレクトリは/workdirになっている
# . .で「コピー元はビルド実行の時のpath」「コピー先は/workdir直下」を示す
COPY . .

# --no-cache-dirをつけることでpipにおけるインストールキャッシュを残さずコンテナ容量を軽くできる
RUN pip install -U pip && \
    pip install --no-cache-dir -r requirements.txt

# Streamlitを使うためにコンテナのポートを開けておく
EXPOSE 8501