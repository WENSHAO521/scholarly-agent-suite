"""Per-language facts the diagnosis and the invariant check need.

Every language is supported. Languages with a phrase catalog in
ppe.patterns get phrase-level findings, hedge and negation counts, and a
connective list for the paragraph-opener check. Any other language
(identified by its ISO 639-1 code) still gets the structural checks, the
protection of citations, numbers, quotations, and formulas, and the
polishing procedure itself; the polisher applies the categories in
references/pattern-catalog.md using its own knowledge of that language
(references/other-languages.md).
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional

# Languages with a phrase catalog (ppe.patterns.CATALOG).
CATALOG_LANGUAGES = ["en", "zh", "ja", "ko", "es", "fr", "de", "pt", "ru"]

_HAN = r"㐀-鿿豈-﫿"
_KANA = r"぀-ヿ"
SCRIPTS = [
    ("ko", re.compile(r"[가-힯ᄀ-ᇿ]")),
    ("ja", re.compile("[" + _KANA + "]")),
    ("zh", re.compile("[" + _HAN + "]")),
    ("ar", re.compile(r"[؀-ۿ]")),
    ("he", re.compile(r"[֐-׿]")),
    ("el", re.compile(r"[Ͱ-Ͽ]")),
    ("th", re.compile(r"[฀-๿]")),
    ("hi", re.compile(r"[ऀ-ॿ]")),
    ("ru", re.compile(r"[Ѐ-ӿ]")),
    ("latin", re.compile(r"[A-Za-zÀ-ɏ]")),
]
_UK_LETTERS = re.compile(r"[іїєґІЇЄҐ]")
_HAN_RE = re.compile("[" + _HAN + "]")
_KANA_RE = re.compile("[" + _KANA + "]")

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

# Languages written without spaces between words: length is counted in characters.
CHAR_UNIT_LANGUAGES = {"zh", "ja", "th"}
# Latin- and Cyrillic-script languages where a sentence starts with a capital.
_CASED = {"en", "es", "fr", "de", "pt", "it", "nl", "id", "ru", "uk", "el"}

HEDGES: Dict[str, str] = {
    "en": r"\b(may|might|could|perhaps|possibly|likely|unlikely|probably|suggests?|suggested|appears?|seems?|tentative(?:ly)?)\b",
    "zh": r"可能|或許|或许|也許|也许|似乎|大概|推測|推测|傾向於|倾向于|初步",
    "ja": r"かもしれ|可能性|と考えられ|と思われ|示唆|であろう|だろう",
    "ko": r"수 있|가능성|것으로 보|추정|시사",
    "es": r"\b(puede|pueden|podría|podrían|quizás?|posiblemente|probablemente|sugiere|sugieren|parece|parecen)\b",
    "fr": r"\b(peut|peuvent|pourrait|pourraient|peut-être|probablement|semble|semblent|suggère|suggèrent)\b",
    "de": r"\b(kann|können|könnte|könnten|möglicherweise|vermutlich|wahrscheinlich|scheint|scheinen|deutet|deuten)\b",
    "pt": r"\b(pode|podem|poderia|poderiam|talvez|possivelmente|provavelmente|sugere|sugerem|parece|parecem)\b",
    "ru": r"(?<![\w-])(может|могут|могла? бы|могли бы|возможно|вероятно|по-видимому|предположительно|свидетельству\w+)(?![\w-])",
}
NEGATIONS: Dict[str, str] = {
    "en": r"\b(not|no|never|neither|nor|none|without|cannot)\b|n't\b",
    "zh": r"並不|并不|不是|不能|不會|不会|不應|不应|不宜|未(?=[一-鿿])|沒有|没有|無法|无法|並非|并非",
    "ja": r"ない|ません|ず[、。]|ではな",
    "ko": r"않|없|못 |아니",
    "es": r"\b(no|nunca|ni|sin|ningún|ninguna|tampoco)\b",
    "fr": r"\b(ne|pas|jamais|aucun|aucune|sans|ni)\b|\bn'",
    "de": r"\b(nicht|kein|keine|keinen|keiner|keinem|keines|nie|niemals|ohne|weder)\b",
    "pt": r"\b(não|nunca|nem|sem|nenhum|nenhuma)\b",
    "ru": r"(?<![\w-])(не|нет|ни|никогда|без)(?![\w-])",
}

CONNECTIVE_OPENERS: Dict[str, set] = {
    "en": {"furthermore", "moreover", "additionally", "however", "in addition", "notably", "importantly",
           "overall", "thus", "therefore", "consequently", "similarly", "finally"},
    "zh": {"此外", "另外", "同時", "同时", "與此同時", "与此同时", "然而", "因此", "總之", "总之",
           "綜上所述", "综上所述", "首先", "其次", "最後", "最后", "其中"},
    "ja": {"さらに", "また", "加えて", "しかし", "そのため", "したがって", "一方", "まとめると"},
    "ko": {"또한", "더불어", "그러나", "따라서", "그러므로", "한편", "결론적으로"},
    "es": {"además", "asimismo", "sin embargo", "por lo tanto", "por otro", "en conclusión", "finalmente"},
    "fr": {"de plus", "en outre", "par ailleurs", "cependant", "ainsi", "en conclusion", "enfin"},
    "de": {"darüber", "außerdem", "zudem", "jedoch", "daher", "insgesamt", "schließlich"},
    "pt": {"além", "ademais", "no entanto", "portanto", "assim", "em conclusão", "por fim"},
    "ru": {"кроме", "более", "однако", "таким", "следовательно", "также", "в заключение"},
}
CONJUNCTION_AND = {"en": "and", "es": "y", "fr": "et", "de": "und", "pt": "e", "it": "e", "nl": "en", "ru": "и"}


def detect_language(text: str) -> str:
    """Best guess at the text's language as an ISO 639-1 code.

    Script decides first (Hangul -> ko, kana -> ja, Han -> zh, Cyrillic -> ru
    or uk, Arabic, Hebrew, Greek, Thai, Devanagari); Latin-script text is
    told apart by common function words. Pass the language explicitly when
    the guess matters (e.g. Serbian Cyrillic, Persian, Malay)."""
    counts = {name: len(rx.findall(text)) for name, rx in SCRIPTS}
    letters = sum(counts.values())
    if not letters:
        return "en"
    han, kana = len(_HAN_RE.findall(text)), len(_KANA_RE.findall(text))
    if counts["ko"] / letters >= 0.2:
        return "ko"
    if kana and (kana + han) / letters >= 0.3 and kana / max(1, kana + han) >= 0.1:
        return "ja"
    if han / letters >= 0.3:
        return "zh"
    script = max((n for n in counts if n not in ("ko", "ja", "zh")), key=lambda n: counts[n])
    if script == "ru":
        return "uk" if _UK_LETTERS.search(text) else "ru"
    if script != "latin":
        return script
    words = re.findall(r"[a-zà-ÿ]+", text.lower())
    scores = {lang: sum(1 for w in words if w in stops) for lang, stops in LATIN_STOPWORDS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] else "en"


def has_catalog(lang: str) -> bool:
    return lang in CATALOG_LANGUAGES


def uses_char_units(lang: str) -> bool:
    return lang in CHAR_UNIT_LANGUAGES


def sentence_splitter(lang: str) -> "re.Pattern[str]":
    if lang in ("zh", "ja"):
        return re.compile(r"(?<=[。！？!?])")
    if lang in _CASED:
        return re.compile(r"(?<=[.!?])[\"”’»)]?\s+(?=[\"“‘«(¿¡0-9A-ZÀ-ÞА-ЯЁІЇЄҐΑ-Ω])")
    return re.compile(r"(?<=[.!?؟।။።。！？])\s*")


def triplet_regex(lang: str) -> Optional["re.Pattern[str]"]:
    if lang in ("zh", "ja"):
        return re.compile(r"[぀-ヿ一-鿿]{1,8}、[぀-ヿ一-鿿]{1,8}"
                          r"(?:、|和|與|与|及|や|と)[぀-ヿ一-鿿]{1,8}")
    conj = CONJUNCTION_AND.get(lang)
    if not conj:
        return None
    w = r"[^\W\d_][\w-]*"
    return re.compile(r"\b%s(?: %s){0,2}, %s(?: %s){0,2},? %s %s" % (w, w, w, w, conj, w))


def hedge_regex(lang: str) -> Optional[str]:
    return HEDGES.get(lang)


def negation_regex(lang: str) -> Optional[str]:
    return NEGATIONS.get(lang)


def supported_note(lang: str) -> List[str]:
    """Limitations to record when ``lang`` has no phrase catalog."""
    if has_catalog(lang):
        return []
    return ["no phrase catalog for %r: structural checks and protected-item checks ran; phrase-level "
            "polishing followed references/other-languages.md; hedges and negations were not counted" % lang]
