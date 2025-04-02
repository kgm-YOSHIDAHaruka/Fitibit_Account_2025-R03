# 自動更新処理＆クラウド保存（ローカルパス指定）版
# =======================
# ✅ アプリ① 被験者用トークン登録ページ（refresh_token付き保存）
# =======================
# ファイル名: Fitbit_token_submit.py

import streamlit as st
import requests
import json
import os
from urllib.parse import urlparse, parse_qs

st.set_page_config(page_title="Fitbit認証コード登録", page_icon="🔑")
st.title("🔑 Fitbit認証コード 登録ページ")

st.markdown("""
このページでは、研究対象者のFitbitアプリから睡眠データを取得するためのアカウント連携の設定を行います。
以下の方法で作業を進めてください。

### Step.1 ⌚ Fitibit にログインしてください。
[https://www.fitbit.com/dashboard](https://www.fitbit.com/dashboard)

### Step.2 以下のURLにアクセスし、表示されたページのURLをコピーしてください。
```
https://www.fitbit.com/oauth2/authorize?response_type=code&client_id=23QCLW&redirect_uri=http://localhost:8000&scope=sleep%20profile
```

> ※「このサイトにアクセス出来ません」と表示されると思いますが、閉じずにURLをコピーしてください。

コピーしたURLを、下記にペーストしてください。
""")

解析用ID = st.text_input("研究対象者識別番号（例：Y001）")
認証URL = st.text_input("コピーしたURLをここに貼り付けてください")

#Client情報はコード内で固定かつ被験者には表示しない
#実際の情報は非公開にしてStreamlit Cloudに預けた情報を参照する
import streamlit as st

client_id = st.secrets["client_id"]
client_secret = st.secrets["client_secret"]

# 保存先を固定して非表示にする（OneDrive上のディレクトリ）
save_path = "C:/Users/21005/OneDrive - KAGOME/ドキュメント/CGM/Fitbit_API/PythonCode/TestData"

if st.button("アカウントを連携"):
    if 解析用ID and 認証URL and client_id and client_secret:
        try:
            parsed_url = urlparse(認証URL)
            code = parse_qs(parsed_url.query).get("code", [None])[0]

            if not code:
                st.error("認証コードがURLから取得できませんでした。URLを確認してください。")
            else:
                headers = {
                    "Authorization": f"Basic {requests.auth._basic_auth_str(client_id, client_secret)}",
                    "Content-Type": "application/x-www-form-urlencoded"
                }
                data = {
                    "client_id": client_id,
                    "grant_type": "authorization_code",
                    "redirect_uri": "http://localhost:8000",
                    "code": code
                }
                response = requests.post("https://api.fitbit.com/oauth2/token", headers=headers, data=data)

                if response.status_code == 200:
                    token_info = response.json()
                    token_info["client_id"] = client_id
                    token_info["client_secret"] = client_secret
                    os.makedirs(save_path, exist_ok=True)
                    with open(os.path.join(save_path, f"token_{解析用ID}.json"), "w", encoding="utf-8") as f:
                        json.dump(token_info, f, ensure_ascii=False, indent=2)
                    st.success("アカウントの連携に成功しました。ご協力ありがとうございました！")
                else:
                    st.error(f"アカウントの連携に成功に失敗しました: {response.text}")
        except Exception as e:
            st.error(f"URLの解析またはアカウントの連携中にエラーが発生しました: {str(e)}")
    else:
        st.warning("すべての項目を入力してください。")
