### 外部ライブラリをインポートする ###
from lib2to3.pgen2.pgen import DFAState
import streamlit as st
import folium
import pandas as pd

### 自作のモジュールをインポートする ###
#from modules import VRProblem

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

_colors = [
    "green",
    "orange",
    "blue",
    "red",
    "purple",
    "pink",
    "darkblue",
    "cadetblue",
    "darkred",
    "lightred",
    "darkgreen",
    "lightgreen",
    "lightblue",
    "darkpurple",
]

def plot_solution(coord: dict, title: str, best_tour: dict = dict()):
    l = len(coord)
    center = [
        sum(lat for _, lat in coord.values()) / l,
        sum(lon for lon, _ in coord.values()) / l,
    ]
    m = folium.Map(center, tiles="OpenStreetMap", zoom_start=10.5)
    folium.Marker(
        location=coord[0][::-1],
        popup=f"depot",
        icon=folium.Icon(icon="car", prefix="fa"),
    ).add_to(m)

    _color = _colors[1]
    if best_tour:
        for k, tour in best_tour.items():
            _color = _colors[k % len(_colors)]
            for city in tour:
                if city == 0:
                    continue

                folium.Marker(
                    location=coord[city][::-1],
                    popup=f"person{k}",
                    icon=folium.Icon(
                        icon="school", prefix="fa", color="white", icon_color=_color
                    ),
                ).add_to(m)
            folium.vector_layers.PolyLine(
                locations=[coord[city][::-1] for city in tour], color=_color, weight=3
            ).add_to(m)
    else:
        for k, node in coord.items():
            if k == 0:
                continue
            folium.Marker(
                location=node[::-1],
                popup=f"customer{k}",
                icon=folium.Icon(
                    icon="school", prefix="fa", color="white", icon_color=_color
                ),
            ).add_to(m)

    title = f"<h4>{title}</h4>"
    m.get_root().html.add_child(folium.Element(title))

    # 緯度経度の範囲を取得
    latitudes = [lat for _, lat in coord.values()]
    longitudes = [lon for lon, _ in coord.values()]
    m.fit_bounds([[min(latitudes), min(longitudes)], [max(latitudes), max(longitudes)]])

    return m


#----------------------------------------------#
# シミュレーター画面の表示の処理群
#----------------------------------------------#
def view_mockup():

    # セレクトボックス（メインメニュー）
    menu = ['【選択してください】', '配送最適化', '献立最適化']
    choice = st.sidebar.selectbox('モードを選択してください', menu)

    txt_apikey = st.sidebar.text_input('APIキー', type='password')

    if menu.index(choice) == 0:
        st.info('左側のメニューから「モード」を選択してください')

    if menu.index(choice) == 1:
        st.title('容量制約つき運搬経路問題')
        # 画像のパス
        image_path = "assets/image/CapacitatedVehicleRoutingProblem.png"
        # 画像を表示
        st.image(image_path, caption="(Capacitated Vehicle Routing Problem, CVRP)", use_column_width=True)
        st.write('運搬経路(配送計画)問題とは、配送拠点(depot)から複数の需要地への配送を効率的に行おうとする配送ルート決定問題です。より具体的には、配送車両の総移動距離が最小になるような配送車両と需要地の割り当て、需要地の訪問順序を決定します。')
        st.write('このデモで取り扱う容量制約付き運搬経路問題は、上記運搬経路問題に各車両の積載上限が追加された問題です。つまり、各配送車両は積載量制約を満たした上で配送を行う必要があります。')
        st.write('今回は配送拠点(デポ)が一つかつ、各需要地の需要と車の容量が整数値のみを取るような場合を考えます。')
        st.write('運搬経路問題の具体的な応用先として、')
        st.write('郵便などの運送業における効率的な配送計画の策定')
        st.write('ごみ収集や道路清掃における訪問順序の決定')
        st.write('などがあります。')
        st.markdown("---")

        df = st.sidebar.file_uploader("データをアップロードしてください", type=["csv"])

        # スライダーを表示
        selected_value = st.sidebar.slider('車の台数を選択してください', 1, 5, 3)

        if df is not None:
            # アップロードされたファイルを直接読み込む
            df_read = pd.read_csv(df)
            df_base = df_read.iloc[0:1]
            df_data = df_read.iloc[1:]
            unique_districts = df_data['District'].unique()

            col1, col2 = st.sidebar.columns(2)
            selected_districts = {}
            count = 0
            for i, district in enumerate(unique_districts):
                c = df_data[df_data['District'] == district].shape[0]
                count += c
                label = f"{district} ({c}件)"
                # 2列目までにチェックボックスを配置
                if i % 2 == 0:
                    checkbox = col1.checkbox(label)
                else:
                    checkbox = col2.checkbox(label)
                selected_districts[district] = checkbox

            selected_data = df_data[df_data['District'].isin([district for district, selected in selected_districts.items() if selected])]
            ind2coord = pd.concat([df_base, selected_data]).reset_index(drop=True).apply(lambda row: (row[3], row[2]), axis=1).to_dict()
            map_ = plot_solution(ind2coord, "title", None)
            html_map = folium.Figure().add_child(map_).render()

            st.write(f'車の台数：{selected_value}件')
            st.write(f'配送先：{len(ind2coord)}件')
            st.components.v1.html(html_map, height=500)


        # 実行ボタンを追加
        if st.sidebar.button('✔RUN'):
            # ボタンがクリックされた場合の処理をここに追加
            st.sidebar.write('選択された値:', selected_value)

            selected_data = df_data[df_data['District'].isin([district for district, selected in selected_districts.items() if selected])]
            ind2coord = selected_data.reset_index(drop=True).apply(lambda row: (row[3], row[2]), axis=1).to_dict()
            map_ = plot_solution(ind2coord, "title", None)
            html_map = folium.Figure().add_child(map_).render()

            st.components.v1.html(html_map, height=500)
            st.write("map_の中身:", map_)

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
