### 外部ライブラリをインポートする ###
from lib2to3.pgen2.pgen import DFAState
import streamlit as st
import japanize_matplotlib
import matplotlib.pyplot as plt
import folium
import numpy as np
import pandas as pd

### 自作のモジュールをインポートする ###
from modules import VRProblem

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
        st.write('・　郵便などの運送業における効率的な配送計画の策定')
        st.write('・　ごみ収集や道路清掃における訪問順序の決定')
        st.write('などがあります。')
        st.markdown("---")

        colA, colB = st.columns([3, 1])
        # スライダーを表示
        with colA:
            selected_value = st.slider('車の台数を選択してください', 1, 5, 3)
        with colB:
            # 実行ボタンを追加
            button_pressed = st.button('✔RUN')

        df_read = pd.read_csv("pos_data.csv")
        df_base = df_read.iloc[0:1]
        df_data = df_read.iloc[1:]
        unique_districts = df_data['District'].unique()

        col1, col2, col3, col4 = st.columns(4)
        selected_districts = {}
        for i, district in enumerate(unique_districts):
            count = df_data[df_data['District'] == district].shape[0]
            label = f"{district} ({count}件)"
            # 2列目までにチェックボックスを配置
            if i % 4 == 0:
                checkbox = col1.checkbox(label)
            elif i % 4 == 1:
                checkbox = col2.checkbox(label)
            elif i % 4 == 2:
                checkbox = col3.checkbox(label)
            else:
                checkbox = col4.checkbox(label)
            selected_districts[district] = checkbox

        selected_data = df_data[df_data['District'].isin([district for district, selected in selected_districts.items() if selected])]
        ind2coord = pd.concat([df_base, selected_data]).reset_index(drop=True).apply(lambda row: (row[3], row[2]), axis=1).to_dict()

        if button_pressed:
            VRProblem.set_api_key(txt_apikey)
            best_tour = VRProblem.find_best_tour(selected_data, selected_value)

            '''
            ind2coord = {0: (139.1257139, 37.9421493),
             1: (139.0132897, 37.91213966),
             2: (139.0252257, 37.916064),
             3: (139.0316096, 37.9152699),
             4: (139.042371, 37.91432293),
             5: (139.0399173, 37.92395128),
             6: (139.049079, 37.935616),
             7: (139.0650007, 37.91721818),
             8: (139.0737316, 37.91603945),
             9: (139.0715896, 37.88928017),
             10: (139.044237, 37.90275993),
             11: (139.0186776, 37.88349631),
             12: (139.0686038, 37.9114295),
             13: (139.0437186, 37.89248784),
             14: (139.0112291, 37.90186835),
             15: (139.0503463, 37.91341667),
             16: (139.0313033, 37.89557017),
             17: (139.0792831, 37.89194292),
             18: (139.0600418, 37.89862968),
             19: (139.0359703, 37.925097),
             20: (139.0734401, 37.94018564),
             21: (139.1197372, 37.92467675),
             22: (139.1008652, 37.90289282),
             23: (139.0863825, 37.9158178),
             24: (139.0910009, 37.93430489),
             25: (139.0785557, 37.94307354),
             26: (139.1160849, 37.94408186),
             27: (139.098454, 37.9186991),
             28: (139.1194044, 37.90466903),
             29: (139.0894125, 37.91099187),
             30: (139.1058765, 37.89581331),
             31: (139.0839817, 37.90391173)}

            best_tour = {
                0: np.array([0, 7, 15, 4, 5, 19, 6, 20, 25, 0]),
                1: np.array([0, 10, 13, 16, 11, 14, 1, 2, 3, 0]),
                2: np.array([0, 8, 12, 18, 9, 17, 31, 22, 30, 28, 0]),
                3: np.array([0, 26, 24, 23, 29, 27, 21, 0])
            }
            '''
        else:
            best_tour = None

        map_ = plot_solution(ind2coord, "title", best_tour)
        html_map = folium.Figure().add_child(map_).render()

        st.write(f'配送先：{len(ind2coord)-1}件')
        st.components.v1.html(html_map, height=500)

    if menu.index(choice) == 2:
        st.title('献立最適化問題')
        # 画像のパス
        image_path = "assets/image/MenuOptimization.png"
        # 画像を表示
        st.image(image_path, use_column_width=True)
        st.write('献立最適化問題とは、特定の制約や要求に基づいて、最も効率的かつ栄養価の高い食事を計画することを目的とした問題です。より具体的には、目標となる栄養素の必要量を満たす献立の組み合わせを決定します。')
        st.write('このデモで取り扱う献立最適化問題は、バランスの取れた食事を実現するための最適な組み合わせを見つけることに焦点を当てています。')
        st.write('献立最適化問題の具体的な応用先として、')
        st.write('・　家庭や学校の食事計画で、予算内で栄養バランスのとれたメニューの作成')
        st.write('・　特定の健康上の制約（例えば、糖尿病や高血圧など）を持つ人々のための個別の食事計画')
        st.write('・　顧客の好みや季節に応じた献立の提案')
        st.write('などがあります。')
        st.markdown("---")

        num_cols = 4
        colsA = st.columns(num_cols)

        min_values = [10, 0, 0, 0]
        max_values = [2000, 100, 30, 30]

        for col_index in range(num_cols):
            with colsA[col_index]:
                if col_index == 0:
                    calorie_value = st.slider('カロリー (kcal)', min_values[0], max_values[0], 700)
                elif col_index == 1:
                    protein_value = st.slider('たんぱく質 (g)', min_values[1], max_values[1], 30)
                elif col_index == 2:
                    vitamin_c_value = st.slider('ビタミンC (mg)', min_values[2], max_values[2], 10)
                elif col_index == 3:
                    iron_value = st.slider('鉄 (mg)', min_values[3], max_values[3], 10)
                    button_pressed = st.button('✔RUN')

        df_read = pd.read_csv("menu_data.csv")
        unique_vals = df_read['データ区分'].unique()
        num_cols = len(unique_vals)
        cols = [st.columns(num_cols) for _ in range((len(unique_vals) + num_cols - 1) // num_cols)]
        # 各栄養素の合計を初期化
        total_calories = 0
        total_protein = 0
        total_vitamin_c = 0
        total_iron = 0

        for i, val in enumerate(unique_vals):
            col_index = i % num_cols
            with cols[i // num_cols][col_index]:
                selected_dish = st.selectbox(f'{val}を選択してください:', df_read[df_read['データ区分']==val]['料理名'])
                selected_row = df_read[(df_read['データ区分']==val) & (df_read['料理名']==selected_dish)]

                # 選択されたデータの栄養素を表示
                st.write(selected_row.transpose()[2:])

                # 各栄養素の合計に追加
                total_calories += selected_row['カロリー (kcal)'].values[0]
                total_protein += selected_row['たんぱく質 (g)'].values[0]
                total_vitamin_c += selected_row['ビタミンC (mg)'].values[0]
                total_iron += selected_row['鉄 (mg)'].values[0]

        st.markdown("---")
        st.write("■ 合計 ■")
        st.write(f"カロリー (kcal): {total_calories}, たんぱく質 (g): {total_protein}, ビタミンC (mg): {total_vitamin_c}, 鉄 (mg): {total_iron}")

        labels = ['カロリー', 'たんぱく質', 'ビタミンC', '鉄']
        selected_data = [total_calories, total_protein, total_vitamin_c, total_iron]
        goal_data = [calorie_value, protein_value, vitamin_c_value, iron_value]

        def normalize_data(data, max_values):
            return [d / max_val for d, max_val in zip(data, max_values)]

        # レーダーチャートの描画
        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        data = normalize_data(selected_data, max_values) + [selected_data[0] / max_values[0]]
        goal_data = normalize_data(goal_data, max_values) + [goal_data[0] / max_values[0]]
        angles += angles[:1]

        ax = plt.subplot(111, polar=True)
        ax.fill(angles, data, color='blue', alpha=0.25)
        ax.plot(angles, goal_data, color='red', linewidth=2)  # 目標値を追加
        ax.set_yticklabels([])
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels)

        # タイトルを設定
        ax.set_title('栄養素比較')

        # レーダーチャートを表示
        st.pyplot(plt)

        if button_pressed:
            # ボタンがクリックされた場合の処理をここに追加
            st.write("Button Pressed!")
            st.write("Calorie Value:", calorie_value)
            st.write("Protein Value:", protein_value)
            st.write("Vitamin C Value:", vitamin_c_value)
            st.write("Iron Value:", iron_value)



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
