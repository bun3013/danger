import streamlit as st
import pandas as pd
import time
import datetime
import plotly.express as px

# 背景色を白にするカスタムCSS
st.markdown(
    """
    <style>
        body {
            background-color: #ffffff;
            color: #000000;
        }
        .stButton > button {
            background-color: #007BFF;
            color: white;
            border-radius: 10px;
            padding: 10px;
            width: 100%;
        }
        .stButton > button:hover {
            background-color: #0056b3;
        }
        .stSlider {
            padding-top: 10px;
        }
        .stDownloadButton > button {
            background-color: #28a745;
            color: white;
            border-radius: 10px;
            padding: 10px;
            width: 100%;
        }
        .stDownloadButton > button:hover {
            background-color: #1e7e34;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# タイトル
st.title("🚗 危険度評価アプリ")

# 名前の入力（1回だけ記録）
if "user_name" not in st.session_state:
    st.session_state.user_name = ""

user_name = st.text_input("📝 名前を入力してください", value=st.session_state.user_name)
if user_name and st.session_state.user_name == "":
    st.session_state.user_name = user_name  # 1回だけ保存

# 運転経験の選択（1回だけ記録）
if "driving_experience" not in st.session_state:
    st.session_state.driving_experience = ""

driving_experience = st.radio(
    "🚘 運転経験を選択してください",
    ("①運転免許持ち・普段から運転する", "②運転免許は持っているが、日常的に運転はしない", "③免許を持っていない"),
    index=None  # 最初は選択なしにする
)
if driving_experience and st.session_state.driving_experience == "":
    st.session_state.driving_experience = driving_experience  # 1回だけ保存

# 事前に埋め込むMP4ファイル（5本）
video_paths = [
    "20240706091330A_0000.mp4",
    "20240609135358A_0g00.mp4",
    "20240610201047A_0000.mp4",
    "20240830151034A_dg00.mp4",
    "20240527211101A_dg00.mp4"
]

st.warning("🔇 動画の音声は自動的にオフになっています。")
st.info("📢 **動画は再生してから10秒後に開始されます**")
st.info("🔴 **記録開始ボタンを押してからスライダーを動かしてください**")

# 記録用の辞書
if "data" not in st.session_state:
    st.session_state.data = {f"video_{i}": [] for i in range(len(video_paths))}

# 記録状態を管理するフラグと開始時間
if "recording" not in st.session_state:
    st.session_state.recording = {f"video_{i}": False for i in range(len(video_paths))}
if "start_time" not in st.session_state:
    st.session_state.start_time = {f"video_{i}": None for i in range(len(video_paths))}

# 各動画ごとにスライダーと測定ボタンを追加
for i, video_path in enumerate(video_paths):
    st.write(f"## 🎥 動画 {i+1}")

    col1, col2 = st.columns([2, 1])
    with col1:
        st.video(video_path)

    with col2:
        st.write("### ⚠️ 危険度を評価してください")
        st.write("1 = 安全（余程のことがない限り事故は起きない）")
        st.write("5 = 極めて危険（事故につながる可能性が高い）")
        danger_level = st.slider("スライダーをクリックしたまま動かしてください", 1, 5, 3, 1, key=f"slider_{i}")

    col3, col4 = st.columns(2)
    with col3:
        if st.button(f"▶️ 記録開始（動画 {i+1}）", key=f"start_{i}"):
            st.session_state.recording[f"video_{i}"] = True
            st.session_state.start_time[f"video_{i}"] = time.time()

    with col4:
        if st.button(f"⏹ 記録停止（動画 {i+1}）", key=f"stop_{i}"):
            st.session_state.recording[f"video_{i}"] = False

    if st.session_state.recording[f"video_{i}"]:
        elapsed_time = round(time.time() - st.session_state.start_time[f"video_{i}"], 2)
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        st.session_state.data[f"video_{i}"].append({
            "user_name": st.session_state.user_name,
            "driving_experience": st.session_state.driving_experience,
            "video": f"動画 {i+1}",
            "time": elapsed_time,
            "real_time": current_time,
            "danger_level": danger_level
        })

# 記録データをまとめる
all_data = []
for key in st.session_state.data:
    all_data.extend(st.session_state.data[key])

# データフレームを表示
if len(all_data) > 0:
    df = pd.DataFrame(all_data)
    st.write("📊 記録データ:")
    st.dataframe(df)

    # CSVに保存（encoding="utf-8-sig" を指定）
    csv_data = df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")

    # ダウンロードボタン
    st.download_button(label="💾 データをダウンロード", data=csv_data, file_name="danger_data.csv", mime="text/csv")

    # グラフ描画（時間ごとの危険度変化）
    st.write("📈 危険度の時間変化（動画別）")
    fig = px.line(df, x="time", y="danger_level", color="video",
                  labels={"time": "時間 (秒)", "danger_level": "危険度", "video": "動画"})
    st.plotly_chart(fig)
