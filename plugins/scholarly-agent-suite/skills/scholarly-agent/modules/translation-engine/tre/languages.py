"""Language, script, and variety facts the translation checks need.

Every language is supported: the checks that matter most (citations,
numbers, DOIs, URLs, formulas, paragraph alignment, glossary terms) do not
depend on the language at all. Script detection tells whether a target is
in the requested language and whether source-script text was left
untranslated. Hedge and negation lists exist for nine languages and let the
check flag a paragraph whose hedge or negation disappeared in translation.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional

_HAN = "㐀-鿿豈-﫿"
_KANA = "぀-ヿ"
_HANGUL = "가-힯ᄀ-ᇿ"

SCRIPT_RANGES: Dict[str, str] = {
    "hangul": _HANGUL,
    "kana": _KANA,
    "han": _HAN,
    "cyrillic": "Ѐ-ӿ",
    "arabic": "؀-ۿ",
    "hebrew": "֐-׿",
    "greek": "Ͱ-Ͽ",
    "thai": "฀-๿",
    "devanagari": "ऀ-ॿ",
    "latin": "A-Za-zÀ-ɏ",
}
_SCRIPT_RE = {name: re.compile("[" + rng + "]") for name, rng in SCRIPT_RANGES.items()}

# Main script of a language (ISO 639-1). Unlisted languages are taken to be
# Latin-script; pass the language explicitly for anything else.
LANGUAGE_SCRIPT: Dict[str, str] = {
    "zh": "han", "ja": "han+kana", "ko": "hangul",
    "ru": "cyrillic", "uk": "cyrillic", "bg": "cyrillic", "sr": "cyrillic", "mk": "cyrillic",
    "kk": "cyrillic", "mn": "cyrillic", "be": "cyrillic",
    "ar": "arabic", "fa": "arabic", "ur": "arabic",
    "he": "hebrew", "el": "greek", "th": "thai", "hi": "devanagari", "mr": "devanagari", "ne": "devanagari",
}

LATIN_STOPWORDS = {
    "en": "the and of to is in that with for are this as be by",
    "es": "el la los las de que y en es por una con del se para",
    "fr": "le la les des et est une dans que pour du avec sur pas au aux l d qu il qui ce cette sont",
    "de": "der die das und ist nicht mit den ein eine zu von im auf sich",
    "pt": "o os as de que e em um uma não para com do da dos",
    "it": "il lo gli di che per una con del non della sono anche",
    "nl": "de het een en van is dat niet op te voor met zijn",
    "id": "yang dan di ini itu dengan untuk dari tidak pada adalah",
}
LATIN_STOPWORDS = {k: set(v.split()) for k, v in LATIN_STOPWORDS.items()}

HEDGES: Dict[str, str] = {
    "en": r"\b(may|might|could|perhaps|possibly|likely|unlikely|probably|suggests?|suggested|appears?|seems?|tentative(?:ly)?)\b",
    "zh": r"可能|或許|或许|也許|也许|似乎|大概|推測|推测|傾向於|倾向于|初步|顯示出|显示出",
    "ja": r"かもしれ|可能性|と考えられ|と思われ|示唆|であろう|だろう",
    "ko": r"수 있|가능성|것으로 보|추정|시사",
    "es": r"\b(puede|pueden|podría|podrían|quizás?|posiblemente|probablemente|sugiere|sugieren|parece|parecen)\b",
    "fr": r"\b(peut|peuvent|pourrait|pourraient|peut-être|probablement|semble|semblent|suggère|suggèrent)\b",
    "de": r"\b(kann|können|könnte|könnten|möglicherweise|vermutlich|wahrscheinlich|scheint|scheinen|deutet|deuten)\b",
    "pt": r"\b(pode|podem|poderia|poderiam|talvez|possivelmente|provavelmente|sugere|sugerem|parece|parecem)\b",
    "ru": r"(?<![\w-])(может|могут|могла? бы|могли бы|возможно|вероятно|по-видимому|предположительно)(?![\w-])",
}
NEGATIONS: Dict[str, str] = {
    "en": r"\b(not|no|never|neither|nor|none|without|cannot|lack|lacks)\b|n't\b",
    "zh": r"不|未(?=[一-鿿])|沒有|没有|無法|无法|並非|并非|非(?=[一-鿿])|無(?=[一-鿿])|无(?=[一-鿿])",
    "ja": r"ない|ません|ず[、。]|ではな|なかった",
    "ko": r"않|없|못 |아니",
    "es": r"\b(no|nunca|ni|sin|ningún|ninguna|tampoco)\b",
    "fr": r"\b(ne|pas|jamais|aucun|aucune|sans|ni)\b|\bn'",
    "de": r"\b(nicht|kein|keine|keinen|keiner|keinem|keines|nie|niemals|ohne|weder)\b",
    "pt": r"\b(não|nunca|nem|sem|nenhum|nenhuma)\b",
    "ru": r"(?<![\w-])(не|нет|ни|никогда|без)(?![\w-])",
}

# Languages written without spaces between words.
CHAR_UNIT_LANGUAGES = {"zh", "ja", "th"}

# Characters whose form differs between Simplified and Traditional Chinese,
# common in academic prose. A Traditional target containing a Simplified-only
# form (or the reverse) has a conversion slip. Pairs are (simplified, traditional).
_ZH_PAIRS = (
    "们們 这這 为為 发發 说說 学學 国國 会會 对對 时時 来來 经經 与與 实實 问問 题題 关關 应應 现現 "
    "进進 动動 过過 还還 种種 体體 证證 产產 业業 东東 两兩 个個 论論 结結 构構 认認 识識 难難 显顯 "
    "响響 变變 级級 资資 计計 设設 质質 样樣 观觀 务務 区區 华華 环環 历歷 层層 义義 当當 机機 "
    "数數 据據 统統 调調 验驗 测測 试試 将將 让讓 从從 众眾 却卻 虽雖 并並 则則 达達 "
    "节節 处處 场場 报報 农農 战戰 权權 规規 标標 献獻 读讀 写寫 语語 词詞 释釋 "
    "运運 营營 组組 织織 价價 综綜 际際 联聯 网網 络絡 视視 图圖 书書 类類 选選 择擇"
)
_PAIRS = [(p[0], p[1]) for p in _ZH_PAIRS.split() if len(p) == 2 and p[0] != p[1]]
SIMPLIFIED_ONLY = {s for s, _ in _PAIRS}
TRADITIONAL_ONLY = {t for _, t in _PAIRS}
TRADITIONAL_VARIETIES = {"zh-Hant", "zh-TW", "zh-HK"}
SIMPLIFIED_VARIETIES = {"zh-Hans", "zh-CN"}


def script_counts(text: str) -> Dict[str, int]:
    return {name: len(rx.findall(text)) for name, rx in _SCRIPT_RE.items()}


def detect_language(text: str) -> str:
    """Best guess at the text's language as an ISO 639-1 code (script
    first, then Latin function words). Pass the language explicitly when
    the guess matters."""
    c = script_counts(text)
    letters = sum(c.values())
    if not letters:
        return "en"
    if c["hangul"] / letters >= 0.2:
        return "ko"
    if c["kana"] and (c["kana"] + c["han"]) / letters >= 0.3 and c["kana"] / max(1, c["kana"] + c["han"]) >= 0.1:
        return "ja"
    if c["han"] / letters >= 0.3:
        return "zh"
    script = max((n for n in c if n not in ("hangul", "kana", "han")), key=lambda n: c[n])
    if script != "latin":
        return {"cyrillic": "ru", "arabic": "ar", "hebrew": "he", "greek": "el", "thai": "th",
                "devanagari": "hi"}[script]
    words = re.findall(r"[a-zà-ÿ]+", text.lower())
    scores = {lang: sum(1 for w in words if w in stops) for lang, stops in LATIN_STOPWORDS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] else "en"


def base_language(code: str) -> str:
    """"zh-Hant" -> "zh", "pt-BR" -> "pt"."""
    return code.split("-")[0].lower()


def script_of(lang: str) -> str:
    return LANGUAGE_SCRIPT.get(base_language(lang), "latin")


def script_regex(lang: str) -> "re.Pattern[str]":
    """Characters of ``lang``'s own script (Han and kana together for ja)."""
    script = script_of(lang)
    ranges = "".join(SCRIPT_RANGES[s] for s in script.split("+"))
    return re.compile("[" + ranges + "]")


def same_script(a: str, b: str) -> bool:
    sa, sb = set(script_of(a).split("+")), set(script_of(b).split("+"))
    return bool(sa & sb)


def uses_char_units(lang: str) -> bool:
    return base_language(lang) in CHAR_UNIT_LANGUAGES


def hedge_regex(lang: str) -> Optional[str]:
    return HEDGES.get(base_language(lang))


def negation_regex(lang: str) -> Optional[str]:
    return NEGATIONS.get(base_language(lang))


def variety_mismatches(text: str, variety: Optional[str]) -> List[str]:
    """Characters in ``text`` that belong to the other Chinese script than
    ``variety`` asks for, most frequent first. Empty for any other variety."""
    if variety in TRADITIONAL_VARIETIES:
        wrong = SIMPLIFIED_ONLY
    elif variety in SIMPLIFIED_VARIETIES:
        wrong = TRADITIONAL_ONLY
    else:
        return []
    counts: Dict[str, int] = {}
    for ch in text:
        if ch in wrong:
            counts[ch] = counts.get(ch, 0) + 1
    return sorted(counts, key=lambda ch: (-counts[ch], ch))


def paragraphs(text: str) -> List[str]:
    """Paragraphs separated by blank lines, stripped, empty ones dropped."""
    return [p.strip() for p in re.split(r"\n\s*\n", text.strip()) if p.strip()]


def units(text: str, lang: str) -> int:
    """Length in words, or in characters for languages without spaces."""
    if uses_char_units(lang):
        return len(re.findall(r"\S", text))
    return len(re.findall(r"[^\W_]+(?:[-'’][^\W_]+)*", text))
