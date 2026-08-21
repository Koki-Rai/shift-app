import streamlit as st
import pandas as pd
from solver import solve_shift, bands

st.title("シフト自動作成アプリ")

# --- ① バンド順エディタ（ここに足す）---
st.header("1. バンド順を決める")
slots = ["午前", "午後", "夕方"]

band_placement = {}
for slot in slots:
    candidates = ["（なし）"]
    for band in bands:
        if slot not in band["unavailable_slots"]:
            candidates.append(band["band"])
    choice = st.selectbox(f"{slot} に演奏するバンド", candidates)
    band_placement[slot] = choice

band_order_df = pd.DataFrame({
    "時間": slots,
    "バンド": [band_placement[slot] for slot in slots],
})
st.dataframe(band_order_df)



# --- ②シフト作成 ---
st.header("2. シフトを作成する")
if st.button("シフトを作成する"):
    df = solve_shift(band_placement)
    if df is not None:
        st.success("シフトが作成できました！")
        st.dataframe(df)
    else:
        st.error("条件を満たすシフトが見つかりませんでした。")