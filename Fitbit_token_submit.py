# =======================
# ✅ アプリ① 被験者用トークン登録ページ（refresh_token付き保存）
# =======================

import streamlit as st
import requests
import json
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
https://www.fitbit.com/oauth2/authorize?response_type=code&client_id=23QCLW&redirect_uri=https://localhost:8000&scope=sleep
```

> ※「このサイトにアクセス出来ません」と表示されると思いますが、閉じずにURLをコピーしてください。

""")

redirected_url = st.text_input("コピーしたURLを貼り付けてください")
subject_id = st.text_input("研究対象者識別番号（例 Y001）", max_chars=10)


# 初期化処理
if "download_success" not in st.session_state:
    st.session_state["download_success"] = False

if "filename" not in st.session_state:
    st.session_state["filename"] = None

if st.button("アカウントを連携"):
    st.session_state["download_success"] = False  # 連携開始時にリセット
    
    if not subject_id or not redirected_url:
        st.error("URLと識別番号の両方を入力してください。")
    else:
        try:
            # 認証コードを抽出
            parsed_url = urlparse(redirected_url)
            code = parse_qs(parsed_url.query).get("code", [None])[0]

            if not code:
                st.error("URLから認証コードが取得できませんでした。URLが正しいか確認してください。")
            else:
                # トークン取得用の情報
                client_id = st.secrets["client_id"]
                client_secret = st.secrets["client_secret"]
                redirect_uri = "https://localhost:8000"

                token_url = "https://api.fitbit.com/oauth2/token"
                headers = {
                    "Authorization": f"Basic {requests.auth._basic_auth_str(client_id, client_secret).split(' ')[1]}",
                    "Content-Type": "application/x-www-form-urlencoded"
                }
                data = {
                    "client_id": client_id,
                    "grant_type": "authorization_code",
                    "redirect_uri": redirect_uri,
                    "code": code
                }

                response = requests.post(token_url, headers=headers, data=data)

                if response.status_code == 200:
                    token_data = response.json()

                    # ✅ client_id / secret をトークン情報に追加して保存！
                    token_data["client_id"] = client_id
                    token_data["client_secret"] = client_secret

                    filename = f"token_{subject_id}.json"
                    with open(filename, "w", encoding="utf-8") as f:
                        json.dump(token_data, f, ensure_ascii=False, indent=2)

                    # ✅ セッションに保存
                    st.session_state["filename"] = filename
                    st.session_state["download_success"] = True
                    st.success(f"○ アカウントの連携に成功しました！\nファイル名：{filename} トークンファイルをダウンロードしてください")
                    
                else:
                    st.error(f"❌ アカウントの連携に失敗しました：{response.status_code}\n{response.text}")

        except Exception as e:
            st.error(f"⚠ エラーが発生しました：{str(e)}")

            
# ✅ ダウンロード後の案内はセッションで制御
if st.session_state["download_success"] and st.session_state["filename"]:
    try:
        with open(st.session_state["filename"], "rb") as f:
            st.download_button(
                label="トークンファイルをダウンロード",
                data=f,
                file_name=st.session_state["filename"],
                mime="application/json"
            )

        # アップロード先の案内（ここにDriveリンクを入れる）
        upload_url = "Haruka_Yoshida@kagome.co.jp"  # 用意したアップロード先
        st.markdown("---")
        st.markdown(f"""
        ### Step.3 📝 ファイルをアップロードしてください
        
        以下のリンクから、上でダウンロードしたファイルのアップロードをお願いいたします。
        
        🔗 [アップロード用フォルダ]({upload_url})
        """)   
        
    except FileNotFoundError:
        st.error("ファイルが見つかりませんでした。再度連携処理を行ってください。")

