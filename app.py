import streamlit as st
from solver import solve_shift

st.title("シフト自動作成アプリ")
st.write("ボタンを押すと、かぶり・予定被りのないシフトを自動生成します。")

if st.button("シフトを作成する"):
    df = solve_shift()
    if df is not None:
        st.success("シフトが作成できました！")
        st.dataframe(df)
    else:
        st.error("条件を満たすシフトが見つかりませんでした。")