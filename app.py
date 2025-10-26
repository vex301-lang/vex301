# -*- coding: utf-8 -*-
import streamlit as st
from metaphor_lib import generate, fmt_markdown

st.set_page_config(page_title="은유 기계 (초등용)", page_icon="✨")
st.title("✨ 쉬운 은유 기계 ✨")
st.write("이 프로그램은 상상력을 자극하는 인물과 장소를 만들어 줘요!")

mode_label = st.radio("무엇을 만들까요?", ["인물", "장소", "둘 다"], index=2, horizontal=True)
mode_map = {"인물": "character", "장소": "place", "둘 다": "both"}
count = st.slider("몇 개 만들까요?", 1, 10, 3)
seed = st.number_input("시드(같은 결과 재생산)", min_value=0, value=0, step=1)

if st.button("생성하기 ✨"):
    seed_val = seed if seed != 0 else None
    items = generate(mode_map[mode_label], count, seed=seed_val)
    st.markdown(fmt_markdown(items))
    st.download_button("📥 결과 저장 (markdown)", data=fmt_markdown(items), file_name="metaphor_output.md")

st.info("💡 팁: 아이들이 만든 인물과 장소를 이어서 동화로 발전시켜 보세요!")