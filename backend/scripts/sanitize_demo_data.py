#!/usr/bin/env python3
"""Apply Chinese-to-English translations to backend/sample_data/demo_seed.json.

The output is the public-safe seed file used by `seed_demo.py`.

Approach:
- Hand-authored translation table for artist / album / song names + the two
  Chinese album_comments observed in the current extract.
- Apply name substitutions inside reason/risk/nearest_neighbors_json fields
  (longest-first to avoid greedy substring collisions).
- Replace the taste_profile.profile_text with a hand-rewritten English-only
  version that preserves meaning.

Safe to re-run (idempotent on already-translated content because the
substring searches stop matching once Chinese is gone).
"""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SEED_FILE = REPO / "backend" / "sample_data" / "demo_seed.json"

# Translation tables. Keys are the exact Chinese strings; values the English
# replacements. Album/artist/song names use widely-known transliterations or
# official English titles where they exist.

ARTIST_NAMES = {
    "周杰伦": "Jay Chou",
    "陈奕迅": "Eason Chan",
    "张雨生": "Chang Yu-Sheng",
    "陈粒": "Chen Li",
    "오진우": "Oh Jin-woo",
}

ALBUM_NAMES = {
    "我很忙": "On the Run!",
    "명랑소녀 성공기 O.S.T": "Cheerful Sassy Girl OST",
    "跨时代": "The Era",
    "惊叹号": "Exclamation Mark",
    "短歌": "Short Songs",
    "反正是我": "Anyway, It's Me",
    "还是朋友": "Still Friends",
    "依然范特西": "Still Fantasy",
    "七里香": "Common Jasmine Orange",
    "叶惠美": "Yeh Hui-Mei",
    "范特西": "Fantasy",
    "哎呦，不错哦": "Aiyo, Not Bad",  # appears in neighbors_json
    "Mellon Collie": "Mellon Collie",  # passthrough
}

SONG_NAMES = {
    "牛仔很忙": "The Cowboy Is Busy",
    "彩虹": "Rainbow",
    "青花瓷": "Blue and White Porcelain",
    "跨时代": "The Era",
    "说了再见": "Said Goodbye",
    "烟花易冷": "Fireworks Cool Easily",
    "惊叹号": "Exclamation Mark",
    "迷魂曲": "Soul Lullaby",
    "短歌": "Short Song",
    "全世界失眠": "The Whole World Is Insomniac",
    "还是朋友": "Still Friends",
    "夜的第七章": "Chapter Seven of the Night",
    "听妈妈的话": "Listen to Mom",
    "千里之外": "Faraway",
    "我的地盘": "My Territory",
    "七里香": "Common Jasmine Orange",
    "借口": "Excuse",
    "以父之名": "In the Name of the Father",
    "懦夫": "Coward",
    "晴天": "Sunny Day",
    "爱在西元前": "Love Before BC",
    "爸 我回来了": "Dad, I'm Home",
    "简单爱": "Simple Love",
}

# Inline phrases used in reason / risk / taste profile.
INLINE_PHRASES = {
    "口水": "saccharine",
    "流行": "too pop",
    "浪费听众的时间": "a waste of the listener's time",
    "春天的感觉": "feel of spring",
}

# Additional Chinese song-comment phrases observed.
EXTRA_SONG_COMMENTS = {
    "怎么一直在我跳?": "Why does this keep skipping for me?",
    "一直autotone": "lots of autotune",
}

# Field passthrough metadata that is Chinese in the source but should read in
# English on the demo cards.
CATEGORY_NAMES = {
    "录音室专辑": "Studio Album",
    "EP、单曲": "EP / Single",
    "原声带、影视音乐": "Soundtrack",
    "现场专辑": "Live Album",
    "精选集": "Compilation",
}

LANGUAGE_NAMES = {
    "国语": "Mandarin",
    "粤语": "Cantonese",
    "英语": "English",
    "韩语": "Korean",
    "日语": "Japanese",
}

# Album comments observed in the current extract.
ALBUM_COMMENT_TRANSLATIONS = {
    "快速跳过，最出名的一张其实不是那么喜欢，说来我为什么要大老远去西雅图看他们演出啊":
        "Skimmed through; their most famous record but I don't actually love it. Why did I trek all the way to Seattle to see them live again?",
    "多了些奇怪的感觉，粗旷的吉他演奏少了好多":
        "A stranger feel overall; much less of the raw, rugged guitar work.",
}

# Hand-rewritten English-only taste profile (preserves the same content as
# the original cached profile, with all Chinese names transliterated and
# Chinese phrases replaced with their English glosses).
SANITIZED_TASTE_PROFILE = (
    "This listener gravitates toward Mandarin pop and Chinese singer-songwriter "
    "work (Jay Chou dominates positively), blended with selective 1990s–2000s "
    "alt-rock touchstones: The Smashing Pumpkins' *Mellon Collie* essentials, "
    "Stereophonics' Britpop-leaning catalogue, and The White Stripes / Black "
    "Keys blues-garage rawness when riffs and melody remain present. Within "
    "rock, they favour clean hookiness and restraint over pure noise—\"Seven "
    "Nation Army\" (rated 5★), Stereophonics' \"Have a Nice Day\" (5★), and "
    "The Black Keys' \"Psychotic Girl\" (5★) exemplify approachable alt-rock "
    "with structural clarity. However, they exhibit stark internal contradictions: "
    "both artist and genre weights show strong negative signals (Jay Chou "
    "−16.8, Alternative Rock −17.5 alongside positive counterparts), "
    "reflecting track-level volatility—Jay Chou's later work often scores "
    "1–2★ with comments tagged as \"saccharine\" or \"too pop,\" while his "
    "early albums (*Yeh Hui-Mei*, *Common Jasmine Orange*) sustain 5★ ratings. "
    "Similarly, they prize Stereophonics' *Just Enough Education to Perform* "
    "(5★ tracks, \"feel of spring\") yet downrate much of *Performance and "
    "Cocktails*. They explicitly dislike experimental excess (Childish Gambino's "
    "*\"Awaken, My Love!\"* marked chaotic; *Because the Internet* called \"a waste "
    "of the listener's time\"), excessive auto-tune / artifice (Jay Chou's *The "
    "Era*, *Exclamation Mark*), and prolonged instrumental passages that obscure "
    "melody. Sade and neo-soul smooth surfaces become dismissed as \"background "
    "music\" unfit for active listening. Their taste demands immediate melodic "
    "engagement and songcraft clarity over artistic obscurity."
)


def apply_substitutions(text: str, table: dict) -> str:
    """Replace all occurrences of each key in `table` with its value.

    Replaces longest keys first to avoid clobbering substrings.
    """
    if not text:
        return text
    for key in sorted(table.keys(), key=len, reverse=True):
        if key in text:
            text = text.replace(key, table[key])
    return text


def translate_name_field(value: str, primary_table: dict, *fallbacks: dict) -> str:
    """Try exact translation from primary table first; otherwise fall back."""
    if value in primary_table:
        return primary_table[value]
    for tbl in fallbacks:
        if value in tbl:
            return tbl[value]
    return value


def sanitize_artists(rows):
    for r in rows:
        r["name"] = translate_name_field(r["name"], ARTIST_NAMES)


def sanitize_albums(rows):
    for r in rows:
        r["name"] = translate_name_field(r["name"], ALBUM_NAMES)
        r["album_category"] = translate_name_field(r["album_category"], CATEGORY_NAMES)
        r["album_lan"] = translate_name_field(r["album_lan"], LANGUAGE_NAMES)


def sanitize_songs(rows):
    for r in rows:
        r["name"] = translate_name_field(r["name"], SONG_NAMES)


def sanitize_album_comments(rows):
    for r in rows:
        c = r.get("comment") or ""
        if c in ALBUM_COMMENT_TRANSLATIONS:
            r["comment"] = ALBUM_COMMENT_TRANSLATIONS[c]
        else:
            r["comment"] = apply_substitutions(c, INLINE_PHRASES)


def sanitize_song_comments(rows):
    """Most are already 'Rated X/5 on track Y'; only catch any stray Chinese."""
    inline = {**EXTRA_SONG_COMMENTS, **INLINE_PHRASES, **SONG_NAMES, **ALBUM_NAMES, **ARTIST_NAMES}
    for r in rows:
        c = r.get("comment") or ""
        if c in EXTRA_SONG_COMMENTS:
            r["comment"] = EXTRA_SONG_COMMENTS[c]
        else:
            r["comment"] = apply_substitutions(c, inline)


def strip_bilingual_label(label: str) -> str:
    """Catalog style/genre names are stored as 'Chinese English' bilingual
    pairs like '国语流行 Mandarin Pop'. Keep only the English half."""
    if not label:
        return label
    # find the first ASCII letter after a Chinese chunk
    for i, ch in enumerate(label):
        if ch.isascii() and ch.isalpha():
            return label[i:].strip()
    return label  # nothing to strip


def sanitize_genres(rows):
    for r in rows:
        r["name"] = strip_bilingual_label(r["name"])


def sanitize_taste_profile(tp):
    if tp is None:
        return
    tp["profile_text"] = SANITIZED_TASTE_PROFILE


def sanitize_recommendation_items(rows):
    """Replace Chinese names in artist_name, album_name, reason, risk, and
    the JSON-encoded styles_json + nearest_neighbors_json fields."""
    # Order matters: do longest-first across the merged dict so e.g.
    # "依然范特西" (album) gets replaced before "范特西" (album).
    inline = {**INLINE_PHRASES, **ALBUM_NAMES, **ARTIST_NAMES, **SONG_NAMES}
    for r in rows:
        r["artist_name"] = translate_name_field(r["artist_name"], ARTIST_NAMES)
        r["album_name"] = translate_name_field(r["album_name"], ALBUM_NAMES)
        r["reason"] = apply_substitutions(r.get("reason") or "", inline)
        r["risk"] = apply_substitutions(r.get("risk") or "", inline) or None
        # nearest_neighbors_json is JSON-encoded text; parse, swap, re-encode
        nj = r.get("nearest_neighbors_json")
        if nj:
            try:
                neighbors = json.loads(nj)
                for n in neighbors:
                    n["artistName"] = translate_name_field(n.get("artistName") or "", ARTIST_NAMES)
                    n["albumName"] = translate_name_field(n.get("albumName") or "", ALBUM_NAMES)
                r["nearest_neighbors_json"] = json.dumps(neighbors, ensure_ascii=False)
            except json.JSONDecodeError:
                r["nearest_neighbors_json"] = apply_substitutions(nj, inline)
        # styles_json is JSON-encoded List[str] of bilingual style labels;
        # keep only the English half.
        sj = r.get("styles_json")
        if sj:
            try:
                styles = json.loads(sj)
                r["styles_json"] = json.dumps(
                    [strip_bilingual_label(s) for s in styles], ensure_ascii=False
                )
            except json.JSONDecodeError:
                pass


def main() -> int:
    data = json.loads(SEED_FILE.read_text(encoding="utf-8"))

    sanitize_artists(data.get("artists") or [])
    sanitize_albums(data.get("albums") or [])
    sanitize_songs(data.get("songs") or [])
    sanitize_genres(data.get("genres") or [])
    sanitize_album_comments(data.get("album_comments") or [])
    sanitize_song_comments(data.get("song_comments") or [])
    sanitize_taste_profile(data.get("taste_profile"))
    sanitize_recommendation_items(data.get("recommendation_items") or [])

    SEED_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"sanitized {SEED_FILE}")

    # Spot-check Chinese leftovers
    leftover = []
    text = SEED_FILE.read_text(encoding="utf-8")
    for ch in text:
        if "一" <= ch <= "鿿" or "가" <= ch <= "힯":
            leftover.append(ch)
    if leftover:
        unique = sorted(set(leftover))
        print(f"  warning: {len(leftover)} CJK chars still present (unique: {len(unique)})")
        print(f"  sample uniques: {''.join(unique[:30])}")
    else:
        print("  no CJK characters remain")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
