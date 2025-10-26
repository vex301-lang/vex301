# -*- coding: utf-8 -*-
from __future__ import annotations
import json, random, textwrap
from typing import Dict, List

CHAR_JOBS = ["과학자","마법사","탐험가","요리사","발명가","화가","음악가","이야기꾼","정원사","로봇"]
FEELINGS = ["기쁨","슬픔","웃음","놀람","꿈","희망","용기","두려움","비밀","상상"]
MATERIALS = ["별빛","바람","돌","나무","물","불","구름","눈","모래","빛"]
PLACES   = ["숲","바다","하늘섬","달나라","별의 마을","모래성","눈산","무지개 들판","호수마을","시간의 정원"]
ADJS     = ["반짝이는","조용한","신비한","달콤한","빛나는","깊은","따뜻한","작은","커다란","용감한"]
SYL      = ["라","리","루","로","나","니","누","노","미","무","바","보","소","수","사","토","타","루"]

def make_name() -> str:
    return (random.choice(SYL) + random.choice(SYL) + random.choice(SYL)).capitalize()

def make_character() -> Dict[str,str]:
    name = make_name()
    job = random.choice(CHAR_JOBS)
    feeling = random.choice(FEELINGS)
    material = random.choice(MATERIALS)
    adj = random.choice(ADJS)
    story = (f"{name}는 {adj} {job}예요. {name}는(은) {feeling}의 힘으로 {material}을(를) 다룰 수 있어요. "
             f"언젠가 {random.choice(PLACES)}로 모험을 떠날 계획이에요!")
    return {"type":"character","이름":name,"직업":job,"특징":adj,"이야기":story}

def make_place() -> Dict[str,str]:
    adj = random.choice(ADJS)
    place = random.choice(PLACES)
    material = random.choice(MATERIALS)
    feeling = random.choice(FEELINGS)
    story = f"{adj} {place}은(는) {material}으로 가득 차 있고, 들어가면 {feeling}을(를) 느낄 수 있어요."
    return {"type":"place","장소":f"{adj} {place}","설명":story}

def generate(mode: str="both", count: int=3, seed: int|None=None) -> List[Dict[str,str]]:
    if seed is not None:
        random.seed(seed)
    out: List[Dict[str,str]] = []
    for _ in range(count):
        if mode in ("character","both"):
            out.append(make_character())
        if mode in ("place","both"):
            out.append(make_place())
    return out

def fmt_markdown(items: List[Dict[str,str]]) -> str:
    parts = ["## 결과 ✨"]
    for it in items:
        if it.get("type")=="character":
            parts.append(f"### 👤 인물: {it['이름']}")
            parts.append(f"- 직업: {it['직업']}  |  특징: {it['특징']}")
            parts.append(f"{it['이야기']}")
        else:
            parts.append(f"### 🏞️ 장소: {it['장소']}")
            parts.append(f"{it['설명']}")
        parts.append("")
    return "\n".join(parts)

if __name__ == "__main__":
    import unittest
    class T(unittest.TestCase):
        def test_make_name_len(self):
            random.seed(1); self.assertGreaterEqual(len(make_name()),3)
        def test_character_keys(self):
            random.seed(2); self.assertTrue({"이름","직업","특징","이야기"}.issubset(make_character().keys()))
        def test_place_keys(self):
            random.seed(3); self.assertTrue({"장소","설명"}.issubset(make_place().keys()))
        def test_seed_repro(self):
            a=generate("both",2,seed=42); b=generate("both",2,seed=42); self.assertEqual(a,b)
        def test_vocab(self):
            random.seed(4); s=json.dumps(generate("both",1),ensure_ascii=False); self.assertTrue(any(w in s for w in ("과학자","마법사","탐험가","숲","바다")))
    unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(T))