### 外部ライブラリをインポートする ###
import streamlit as st
from amplify.client import FixstarsClient

# CSSの設定をする関数
def set_font_style():

    st.markdown(
        """
        <style>
        textarea {
            font-size: 1.2rem !important;
            font-family:  monospace !important;
        }

        code {
            font-size: 1.2rem !important;
            font-family:  monospace !important;
        }

        div.stButton > button:first-child  {
            margin: 0 auto;
            max-width: 240px;
            padding: 10px 10px;
            background: #6bb6ff;
            color: #FFF;
            transition: 0.3s ease-in-out;
            font-weight: 600;
            border-radius: 100px;
            box-shadow: 0 5px 0px #4f96f6, 0 10px 15px #4f96f6;            
            border: none            
        }

        div.stButton > button:first-child:hover  {
            color: #FFF;
            background:#FF2F2F;
            box-shadow: 0 5px 0px #B73434,0 7px 30px #FF2F2F;
            border: none            
          }

        div.stButton > button:first-child:focus {
            color: #FFF;
            background: #6bb6ff;
            box-shadow: 0 5px 0px #4f96f6, 0 10px 15px #4f96f6;
            border: none            
          }


        button[title="View fullscreen"]{
            visibility: hidden;}

        </style>
        """,
        unsafe_allow_html=True,
    )

# 各種フラグなどを初期化する関数（最初の1回だけ呼ばれる）
def init_parameters():

    # タブに表示されるページ名の変更
    st.set_page_config(page_title="量子アルゴリズム", initial_sidebar_state="expanded", )


#----------------------------------------------#
# シミュレーター画面の表示の処理群
#----------------------------------------------#
def view_mockup():

    # セレクトボックス（メインメニュー）
    menu = ['【選択してください】', '配送最適化', '献立最適化']
    choice = st.sidebar.selectbox('モードを選択してください', menu)

    if menu.index(choice) == 0:
        st.info('左側のメニューから「モード」を選択してください')

    if menu.index(choice) == 1:
        # スライダーを表示
        selected_value = st.sidebar.slider('車の台数を選択してください', 1, 5, 3)

        # 実行ボタンを追加
        if st.sidebar.button('✔RUN'):
            # ボタンがクリックされた場合の処理をここに追加
            st.sidebar.write('選択された値:', selected_value)

    if menu.index(choice) == 2:
        # スライダーを表示
        selected_value = st.sidebar.slider('車の台数を選択してください', 1, 5, 3)

        # 実行ボタンを追加
        if st.sidebar.button('✔RUN'):
            # ボタンがクリックされた場合の処理をここに追加
            st.sidebar.write('選択された値:', selected_value)


#----------------------------------------------#
# メイン関数
#----------------------------------------------#
def main():

    ### 各種フラグなどを初期化する関数をコール ###
    init_parameters()

    # フォントスタイルの設定
    set_font_style()

    # メニューを表示する
    view_mockup()


if __name__ == "__main__":
    main()
