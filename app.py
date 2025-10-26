# -*- coding: utf-8 -*-
import io
import re
from typing import List, Tuple

import streamlit as st
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(page_title="한신 초등 8컷 은유 만화", page_icon="✨")
st.title("✨ 한신 초등학교 친구들의 이야기 실력을 볼까요?")
st.caption("좋아하는 단어 3개와 8단 이야기로 나만의 만화를 만들어 보자! (2·4·6은 자동으로 이어줘요)")

# -----------------------------
# 금칙어 필터
# -----------------------------
BANNED_PATTERNS = [
    r"살인", r"죽이", r"폭력", r"피바다", r"학대", r"총", r"칼", r"폭탄",
    r"kill", r"murder", r"gun", r"knife", r"blood", r"assault", r"bomb",
    r"성\s*행위", r"야동", r"포르노", r"음란", r"가슴", r"성기", r"자위",
    r"porn", r"sex", r"xxx", r"nude", r"naked",
]
BAN_RE = re.compile("|".join(BANNED_PATTERNS), re.IGNORECASE)

# 조사를 붙이는 간단 유틸 (을/를, 와/과)
HANGUL_BASE = 0xAC00
JUNGSUNG = 28
def has_jong(ch: str) -> bool:
    if not ch: return False
    code = ord(ch)
    if not (0xAC00 <= code <= 0xD7A3): return False
    return ((code - HANGUL_BASE) % JUNGSUNG) != 0

def eulreul(word: str) -> str:
    return "을" if has_jong(word[-1:]) else "를"
def wagwa(word: str) -> str:
    return "과" if has_jong(word[-1:]) else "와"

# -----------------------------
# 입력 폼 (2,4,6은 자동 생성)
# -----------------------------
with st.form("input_form", clear_on_submit=False):
    st.subheader("1) 좋아하는 단어 3개")
    c1, c2, c3 = st.columns(3)
    w1 = c1.text_input("단어 1", max_chars=12)
    w2 = c2.text_input("단어 2", max_chars=12)
    w3 = c3.text_input("단어 3", max_chars=12)

    st.subheader("2) 8단 이야기 쓰기 ✍️ (2·4·6은 자동으로 채워져요)")
    labels = [
        "옛날에", "그리고 매일", "그러던 어느 날",
        "그래서", "그래서", "그래서",
        "마침내", "그날 이후",
    ]
    # 아이들이 직접 쓰는 칸: 1,3,5,7,8
    s1 = st.text_area(labels[0], height=70, key="story_1")
    st.text_input(labels[1] + " (자동 작성)", value="", disabled=True, key="story_2_auto_placeholder")
    s3 = st.text_area(labels[2], height=70, key="story_3")
    st.text_input(labels[3] + " (자동 작성)", value="", disabled=True, key="story_4_auto_placeholder")
    s5 = st.text_area(labels[4], height=70, key="story_5")
    st.text_input(labels[5] + " (자동 작성)", value="", disabled=True, key="story_6_auto_placeholder")
    s7 = st.text_area(labels[6], height=70, key="story_7")
    s8 = st.text_area(labels[7], height=70, key="story_8")

    submitted = st.form_submit_button("8컷 만화 만들기 ✨")

# -----------------------------
# 유효성 검사
# -----------------------------
def words_valid(words: List[str]) -> Tuple[bool, str]:
    for w in words:
        if not w:
            return False, "단어 3개를 모두 입력해 주세요."
        if BAN_RE.search(w):
            return False, "적절하지 않은 단어입니다. 다시 입력해 주세요"
    return True, "OK"

# -----------------------------
# 자동 생성 문장 (초3 수준, 이전 문맥+단어 사용)
# -----------------------------
def gen_auto_sentences(user_texts: List[str], words: List[str]) -> List[str]:
    # user_texts = [s1, s3, s5, s7, s8]  -> 1,3,5,7,8
    w1, w2, w3 = words
    auto2 = f"그리고 매일, 주인공은 {w1}{eulreul(w1)} 떠올리며 작은 연습을 했어요."
    auto4 = f"그래서 주인공은 {w2}{wagwa(w2)} 함께 쉬운 방법을 찾아 보기로 했어요."
    auto6 = f"그래서 주인공은 {w3}{eulreul(w3)} 천천히 해 보며 실수를 줄였어요."
    # 앞 문장이 있으면 조금 더 자연스럽게 잇기
    if user_texts[0].strip():
        auto2 = "그리고 매일, " + auto2.split(", ", 1)[-1]
    if user_texts[1].strip():
        auto4 = "그래서, " + auto4.split(", ", 1)[-1]
    if user_texts[2].strip():
        auto6 = "그래서, " + auto6.split(", ", 1)[-1]
    return [auto2, auto4, auto6]

# -----------------------------
# 만화 렌더링
# -----------------------------
PALETTE = [
    (255, 239, 213), (224, 255, 255), (255, 245, 238), (240, 255, 240),
    (255, 250, 205), (230, 230, 250), (250, 240, 230), (245, 255, 250),
]
BORDER = (60, 60, 60); TEXT = (40, 40, 40)
H, W = 900, 1600; PAD = 20; COLS, ROWS = 4, 2

def draw_centered_text(draw: ImageDraw.ImageDraw, box, text: str, font, fill, wrap=16):
    lines, line = [], ""
    for ch in text:
        if ch == "\n":
            lines.append(line); line = ""; continue
        if len(line) >= wrap and ch != " ":
            lines.append(line); line = ch
        else:
            line += ch
    if line: lines.append(line)
    x0, y0, x1, y1 = box; Wb, Hb = x1-x0, y1-y0
    h = sum(font.getbbox(ln)[3] for ln in lines) + (len(lines)-1)*4
    y = y0 + (Hb - h)//2
    for ln in lines:
        w = font.getbbox(ln)[2]; x = x0 + (Wb - w)//2
        draw.text((x, y), ln, fill=fill, font=font)
        y += font.getbbox(ln)[3] + 4

def make_face(seed_words: List[str], size=(220, 220)):
    img = Image.new("RGBA", size, (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    w, h = size; cx, cy = w//2, h//2
    d.ellipse([cx-100, cy-100, cx+100, cy+100], fill=(255,224,189,255), outline=BORDER, width=4)
    d.ellipse([cx-45, cy-35, cx-20, cy-10], fill=(0,0,0,255))
    d.ellipse([cx+20, cy-35, cx+45, cy-10], fill=(0,0,0,255))
    d.arc([cx-40, cy-5, cx+40, cy+45], start=200, end=340, fill=(0,0,0,255), width=4)
    glyphs = ["★","♥","◆"]; colors = [(255,105,180,200),(135,206,250,200),(144,238,144,200)]
    for i, _ in enumerate(seed_words):
        d.text((10 + i*70, 10), glyphs[i % len(glyphs)], fill=colors[i % len(colors)])
    return img

def render_comic(all_texts: List[str], seed_words: List[str]) -> Image.Image:
    canvas = Image.new("RGB", (W, H), (255, 255, 255)); draw = ImageDraw.Draw(canvas)
    try:
        title_font = ImageFont.truetype("DejaVuSans.ttf", 26); body_font = ImageFont.truetype("DejaVuSans.ttf", 20)
    except Exception:
        title_font = ImageFont.load_default(); body_font = ImageFont.load_default()
    panel_w = (W - PAD*(COLS+1)) // COLS; panel_h = (H - PAD*(ROWS+1)) // ROWS
    titles = ["옛날에","그리고 매일","그러던 어느 날","그래서","그래서","그래서","마침내","그날 이후"]
    face = make_face(seed_words, size=(200, 200))
    for i in range(8):
        r, c = divmod(i, COLS)
        x0 = PAD + c*(panel_w + PAD); y0 = PAD + r*(panel_h + PAD)
        x1, y1 = x0 + panel_w, y0 + panel_h
        draw.rounded_rectangle([x0,y0,x1,y1], radius=18, fill=PALETTE[i%len(PALETTE)], outline=BORDER, width=2)
        canvas.paste(face, (x0+12, y0+12), face)
        draw.text((x0 + 230, y0 + 16), titles[i], fill=TEXT, font=title_font)
        box = (x0 + 230, y0 + 56, x1 - 14, y1 - 14)
        draw_centered_text(draw, box, all_texts[i][:160], body_font, TEXT, wrap=16)
    return canvas

# -----------------------------
# 제출 처리
# -----------------------------
if submitted:
    words = [w1.strip(), w2.strip(), w3.strip()]
    ok, msg = words_valid(words)
    if not ok:
        st.error(msg)
    else:
        # 아이들이 직접 쓴 칸(1,3,5,7,8) 검사
        user_texts = [s1, s3, s5, s7, s8]
        if any(len(x.strip()) == 0 for x in user_texts):
            st.warning("1, 3, 5, 7, 8 칸을 모두 채워 주세요!")
        else:
            auto2, auto4, auto6 = gen_auto_sentences(user_texts, words)
            all_texts = [
                s1.strip(), auto2.strip(), s3.strip(), auto4.strip(),
                s5.strip(), auto6.strip(), s7.strip(), s8.strip(),
            ]
            img = render_comic(all_texts, words)
            st.success("완성! 아래 이미지를 저장하거나 공유해 보세요 ✨")
            st.image(img, caption="나만의 8컷 은유 만화", use_column_width=True)

            buf = io.BytesIO(); img.save(buf, format="PNG"); buf.seek(0)
            st.download_button("📥 PNG로 저장", data=buf, file_name="hanshin_8cut_comic.png", mime="image/png")
            st.info("TIP: 인쇄하려면 PNG를 다운받아 A4 가로 인쇄로 설정하세요!")
