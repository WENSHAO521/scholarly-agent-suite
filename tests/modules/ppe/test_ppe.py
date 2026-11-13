"""prose-polish-engine runtime (ppe): pattern catalogs, language detection,
diagnosis in any language, invariant checks, and POLISH_REPORT_V1."""
import json
from pathlib import Path

import pytest
from schema_lite import ValidationError, validate_file

import ppe
from ppe import CATEGORIES, POLISH_NOTICE
from ppe.__main__ import main as cli_main
from ppe.diagnose import diagnose
from ppe.invariants import check_invariants, extract
from ppe.languages import CATALOG_LANGUAGES, detect_language
from ppe.patterns import ALL_PATTERNS, CATALOG, patterns_for
from ppe.report import build_polish_report, validate_polish_report

ROOT = Path(__file__).resolve().parents[3]
PROTOCOLS = ROOT / "skills" / "scholarly-agent" / "protocols"
MODULE_DIR = ROOT / "skills" / "scholarly-agent" / "modules" / "prose-polish-engine"

EN = (
    "Certainly! Here is the revised paragraph.\n\n"
    "In today's rapidly evolving world, social media plays a crucial role in political participation "
    "(Smith, 2020; Lee et al., 2019). Furthermore, it is important to note that young voters delve into "
    "online news. The effect was 12.5% larger in 2021 (p < .05)."
)
EN_POLISHED = (
    "Young voters now get most of their political news from social media (Smith, 2020; Lee et al., 2019). "
    "They read it online rather than in print. The effect was 12.5% larger in 2021 (p < .05)."
)
ZH = (
    "隨著人工智慧技術的快速發展，生成式模型在教育領域起著至關重要的作用（王，2021）。"
    "值得注意的是，研究者對1200名學生進行了深入的分析。此外，教師也可能或許會受到影響。"
)
ZH_POLISHED = "生成式模型正在改變課堂上的寫作作業（王，2021）。研究者分析了1200名學生。教師也可能受到影響。"

SAMPLES = {
    "ja": "近年、人工知能の急速な発展に伴い、教育において重要な役割を果たしている。本研究の目的は作文の分析を行うことである。",
    "ko": "최근 인공지능의 급속한 발전에 따라 교육에서 중요한 역할을 한다. 결론적으로, 새로운 시사점을 제공한다.",
    "es": "En el mundo actual, la inteligencia artificial desempeña un papel crucial en la educación. Además, cabe destacar que el estudio es nuevo.",
    "fr": "Dans le monde actuel, l'intelligence artificielle joue un rôle crucial dans l'éducation. De plus, il convient de noter que cette étude est nouvelle.",
    "de": "In der heutigen Welt spielt künstliche Intelligenz eine entscheidende Rolle in der Bildung. Darüber hinaus ist es wichtig zu betonen, dass die Studie neu ist.",
    "pt": "No mundo atual, a inteligência artificial desempenha um papel crucial na educação. Além disso, vale ressaltar que o estudo é novo.",
    "ru": "В современном мире искусственный интеллект играет ключевую роль в образовании. Кроме того, важно отметить, что исследование новое.",
}


# --- catalogs -------------------------------------------------------------

def test_catalog_ids_unique_and_categories_known():
    ids = [p.id for p in ALL_PATTERNS]
    assert len(ids) == len(set(ids))
    for p in ALL_PATTERNS:
        assert p.category in CATEGORIES, p.id
        assert p.severity in ppe.SEVERITIES, p.id
        assert p.id.startswith(p.lang + "-"), p.id
        p.compiled()


def test_every_catalog_language_has_residue_and_core_categories():
    assert sorted(CATALOG) == sorted(CATALOG_LANGUAGES) == sorted(ppe.CATALOG_LANGUAGES)
    for lang in CATALOG_LANGUAGES:
        cats = {p.category for p in patterns_for(lang)}
        for needed in ("chat-residue", "stock-connective", "empty-emphasis", "formulaic-frame", "hedge-stack"):
            assert needed in cats, (lang, needed)


def test_language_without_catalog_returns_empty_list():
    assert patterns_for("it") == []
    assert patterns_for("ar") == []


# --- language detection ---------------------------------------------------

@pytest.mark.parametrize("lang,text", list(SAMPLES.items()) + [("en", EN), ("zh", ZH)])
def test_detect_catalog_languages(lang, text):
    assert detect_language(text) == lang


@pytest.mark.parametrize("lang,text", [
    ("ar", "في عالم اليوم، يلعب الذكاء الاصطناعي دورًا حاسمًا في التعليم."),
    ("el", "Στον σημερινό κόσμο η τεχνητή νοημοσύνη παίζει κρίσιμο ρόλο."),
    ("he", "בעולם של היום לבינה מלאכותית יש תפקיד מכריע בחינוך."),
    ("hi", "आज की दुनिया में कृत्रिम बुद्धिमत्ता शिक्षा में महत्वपूर्ण भूमिका निभाती है।"),
    ("th", "ในโลกปัจจุบันปัญญาประดิษฐ์มีบทบาทสำคัญในการศึกษา"),
    ("uk", "У сучасному світі штучний інтелект відіграє ключову роль у освіті."),
    ("it", "Nel mondo di oggi, l'intelligenza artificiale svolge un ruolo cruciale nella scuola e per gli studenti."),
])
def test_detect_languages_without_catalog(lang, text):
    assert detect_language(text) == lang


# --- diagnosis ------------------------------------------------------------

def test_english_findings_and_load():
    d = diagnose(EN)
    ids = {f["id"] for f in d["findings"]}
    assert {"en-residue-certainly", "en-residue-here-is", "en-frame-todays-world", "en-emph-crucial-role",
            "en-emph-important-to-note", "en-vocab-delve"} <= ids
    assert d["must_remove"] == 2
    assert d["pattern_load"] == "high"
    assert d["catalog"] is True and d["unit"] == "words"


def test_chinese_findings_traditional():
    d = diagnose(ZH)
    ids = {f["id"] for f in d["findings"]}
    assert {"zh-frame-suizhe", "zh-emph-zuoyong", "zh-conn-zhide", "zh-nominal-jinxing", "zh-hedge-stack"} <= ids
    assert d["unit"] == "chars"


def test_chinese_findings_simplified():
    d = diagnose("随着人工智能技术的快速发展，该模型发挥着重要作用。综上所述，本研究具有重要的理论意义和实践意义。")
    ids = {f["id"] for f in d["findings"]}
    assert {"zh-frame-suizhe", "zh-emph-zuoyong", "zh-sum-zongshang", "zh-frame-lilun-shijian"} <= ids


@pytest.mark.parametrize("lang,text", list(SAMPLES.items()))
def test_each_catalog_language_flags_its_templates(lang, text):
    d = diagnose(text)
    assert d["language"] == lang
    cats = {f["category"] for f in d["findings"]}
    assert "empty-emphasis" in cats and "formulaic-frame" in cats, (lang, d["findings"])


def test_language_without_catalog_still_gets_structural_checks():
    para = "Questo studio analizza il caso. " * 6
    text = para + "\n\n" + para
    d = diagnose(text, "it")
    assert d["catalog"] is False
    cats = {f["category"] for f in d["findings"]}
    assert "uniform-rhythm" in cats and "repeated-opener" in cats


def test_quoted_and_cited_text_is_never_flagged():
    text = 'As one respondent put it, "Furthermore, it is important to note that we delve into it." (Ng, 2020)'
    d = diagnose(text, "en")
    assert d["findings"] == []


def test_good_prose_is_low_load():
    text = ("Turnout fell in districts that lost their polling stations (Table 2). The drop was largest "
            "where the nearest station moved more than ten kilometres. We cannot rule out that other "
            "changes in those districts explain part of it, so the next section tests two alternatives.")
    d = diagnose(text)
    assert d["pattern_load"] == "low" and d["must_remove"] == 0


def test_repeated_paragraph_connective_opener():
    text = "Moreover, a is b.\n\nMoreover, c is d.\n\nMoreover, e is f."
    d = diagnose(text, "en")
    openers = [f for f in d["findings"] if f["id"] == "struct-paragraph-opener"]
    assert len(openers) == 2


# --- invariants -----------------------------------------------------------

def test_extract_protected_items():
    items = extract('See (Smith, 2020) and [3-5], doi 10.1234/abc.5 at https://x.org/a. "Quoted words" $x^2$ 12.5%')
    assert items["citations"] == ["(Smith, 2020)", "[3-5]"]
    assert items["dois"] == ["10.1234/abc.5"]
    assert items["quotations"] == ['"Quoted words"']
    assert items["math"] == ["$x^2$"]
    assert "12.5%" in items["numbers"]


def test_extract_quotes_in_other_scripts():
    items = extract("Il a dit « bien sûr ». Er sagte „ja“. 他說「好」。")
    assert sorted(items["quotations"]) == sorted(["« bien sûr »", "„ja“", "「好」"])


def test_invariants_pass_and_review():
    res = check_invariants(EN, EN_POLISHED, "en")
    assert res["failures"] == []
    res = check_invariants(ZH, ZH_POLISHED, "zh")
    assert res["status"] == "REVIEW"  # 「可能或許」 -> 「可能」 changes the hedge count
    assert any("hedges" in w for w in res["warnings"])


def test_invariants_fail_on_dropped_citation_number_or_term():
    res = check_invariants(EN, EN_POLISHED.replace("(Smith, 2020; Lee et al., 2019)", ""), "en")
    assert res["status"] == "FAIL"
    res = check_invariants(EN, EN_POLISHED.replace("12.5%", "13%"), "en")
    assert res["status"] == "FAIL"
    res = check_invariants("Social capital matters.", "Networks matter.", "en", ["Social capital"])
    assert res["status"] == "FAIL"


def test_negation_loss_is_flagged():
    res = check_invariants("The effect is not causal.", "The effect is causal.", "en")
    assert res["status"] == "REVIEW"
    res = check_invariants("Der Effekt ist nicht kausal.", "Der Effekt ist kausal.", "de")
    assert res["status"] == "REVIEW"


def test_invariants_for_language_without_lists_still_check_numbers():
    res = check_invariants("Il campione è di 120 persone (Rossi, 2019).", "Il campione conta 120 persone.", "it")
    assert res["status"] == "FAIL"
    assert "hedges" not in res["checks"]


# --- report ---------------------------------------------------------------

def test_report_validates_against_schema_and_rules():
    r = build_polish_report(ZH, ZH_POLISHED, "standard",
                            changes=[{"category": "hedge-stack", "before": "可能或許", "after": "可能"}])
    assert validate_polish_report(r) == []
    validate_file(r, PROTOCOLS / "polish-report.schema.json")
    assert r["status"] == "REVIEW" and r["notice"] == POLISH_NOTICE
    assert r["before"]["pattern_load"] == "high" and r["after"]["pattern_load"] == "low"


def test_report_fails_when_residue_survives():
    r = build_polish_report(EN, "Certainly! " + EN_POLISHED, "light")
    assert r["status"] == "FAIL"
    assert any(f["category"] == "chat-residue" for f in r["remaining"])


def test_report_for_uncatalogued_language_records_limitation():
    text = "في عالم اليوم، يلعب الذكاء الاصطناعي دورًا حاسمًا في التعليم (سميث، 2020)."
    r = build_polish_report(text, text, "light")
    assert r["language"] == "ar" and r["catalog"] is False
    assert r["limitations"] and "no phrase catalog" in r["limitations"][0]
    assert validate_polish_report(r) == []
    validate_file(r, PROTOCOLS / "polish-report.schema.json")


def test_validator_rejects_softened_status_and_edited_notice():
    r = build_polish_report(EN, EN_POLISHED.replace("12.5%", "13%"), "standard")
    assert r["status"] == "FAIL"
    bad = dict(r, status="PASS")
    assert any("FAIL" in e for e in validate_polish_report(bad))
    bad = dict(r, notice="Now passes AI detectors.")
    assert any("notice" in e for e in validate_polish_report(bad))
    bad = dict(r, changes=[{"category": "made-up", "before": "a", "after": "b"}])
    assert any("unknown category" in e for e in validate_polish_report(bad))


def test_schema_rejects_unknown_level():
    r = build_polish_report(EN, EN_POLISHED, "deep")
    r["level"] = "aggressive"
    with pytest.raises(ValidationError):
        validate_file(r, PROTOCOLS / "polish-report.schema.json")


def test_cli_check_exit_code(tmp_path, capsys):
    a, b = tmp_path / "a.txt", tmp_path / "b.txt"
    a.write_text(EN, encoding="utf-8")
    b.write_text(EN_POLISHED, encoding="utf-8")
    assert cli_main(["check", str(a), str(b)]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["protocol"] == "POLISH_REPORT_V1"
    b.write_text(EN_POLISHED.replace("2021", "2022"), encoding="utf-8")
    assert cli_main(["check", str(a), str(b)]) == 1


# --- integrity wording ----------------------------------------------------

def test_module_states_no_detector_evasion_and_disclosure():
    text = (MODULE_DIR / "MODULE.md").read_text(encoding="utf-8")
    assert "never runs or loops against an\n  AI-text detector" in text or "never runs or loops against an AI-text detector" in text
    assert "Disclosure stays with the author" in text
    assert "rule 14" in text


def test_runtime_has_no_detector_scoring():
    src = "\n".join(p.read_text(encoding="utf-8") for p in (MODULE_DIR / "ppe").glob("*.py")).lower()
    for word in ("ai_probability", "humanness", "detector_score", "perplexity", "zero-width", "\\u200b"):
        assert word not in src, word


# --- defensive writing (v2.5.0) -------------------------------------------

DEFENSIVE_PHRASE_CATEGORIES = ("defensive-hedge", "preemptive-caveat", "disclaimer", "apologetic-framing",
                               "over-justification")

EN_DEFENSIVE = (
    "While this study has some limitations, it could be argued that peer feedback may possibly suggest "
    "a potential benefit (Lee, 2020). These findings should be interpreted with caution. It is reasonable "
    "to assume that further research is needed. This modest attempt is by no means exhaustive, and we "
    "humbly suggest that it was carefully designed for the sake of rigour."
)
ZH_DEFENSIVE = (
    "本研究也存在一些不足，結果應謹慎看待。從某種意義上說，這或可認為是一種拋磚引玉的嘗試，"
    "不當之處在所難免，敬請讀者批評指正。限於篇幅，本文無意窮盡所有案例。"
    "為了保證研究的嚴謹性，我們有理由認為此結論成立。"
)
DEFENSIVE_SAMPLES = {
    "ja": "本研究には限界がある。浅学非才の筆者による拙稿であり、網羅的なものではない。厳密を期すため、と言えなくもない。",
    "ko": "본 연구는 여러 한계를 가진다. 부족한 점이 많지만 지면의 한계로 어느 정도는 타당하다고 볼 수 있다.",
    "es": "Si bien este estudio presenta limitaciones, podría decirse que es una modesta contribución que no pretende ser exhaustiva. Es razonable suponer que sí.",
    "fr": "Bien que cette étude présente certaines limites, on pourrait dire que cette modeste contribution ne prétend pas à l'exhaustivité. Il est raisonnable de supposer que oui.",
    "de": "Obwohl diese Studie gewisse Grenzen hat, könnte man sagen, dass dieser bescheidene Beitrag keinen Anspruch auf Vollständigkeit erhebt. Es ist daher vernünftig anzunehmen, dass er hilft.",
    "pt": "Embora este estudo tenha algumas limitações, pode-se dizer que esta modesta contribuição não pretende ser exaustiva. É razoável supor que sim.",
    "ru": "Хотя данное исследование имеет ряд ограничений, можно сказать, что этот скромный вклад не претендует на полноту. Представляется разумным предположить, что это так.",
}


def test_every_catalog_language_covers_defensive_writing():
    assert set(ppe.DEFENSIVE_CATEGORIES) <= set(CATEGORIES)
    for lang in CATALOG_LANGUAGES:
        cats = {p.category for p in patterns_for(lang)}
        for needed in DEFENSIVE_PHRASE_CATEGORIES:
            assert needed in cats, (lang, needed)


def test_english_defensive_writing_is_found():
    d = diagnose(EN_DEFENSIVE, "en")
    cats = {f["category"] for f in d["findings"]}
    assert set(DEFENSIVE_PHRASE_CATEGORIES) <= cats
    assert {"en-cav-limitations-opener", "en-def-could-be-argued", "en-cav-interpret-caution",
            "en-cav-further-research", "en-disc-not-exhaustive", "en-apol-humble",
            "en-apol-modest-attempt", "en-just-reasonable", "en-just-for-the-sake"} <= {f["id"] for f in d["findings"]}
    assert d["defensive"] >= 10


@pytest.mark.parametrize("text", [ZH_DEFENSIVE, "限于篇幅，本文无意穷尽。抛砖引玉，不当之处在所难免，敬请批评指正。为了确保研究的严谨性，学界普遍认为如此。"])
def test_chinese_defensive_writing_traditional_and_simplified(text):
    d = diagnose(text, "zh")
    cats = {f["category"] for f in d["findings"]}
    assert {"disclaimer", "apologetic-framing", "over-justification"} <= cats


def test_chinese_defensive_ids():
    ids = {f["id"] for f in diagnose(ZH_DEFENSIVE, "zh")["findings"]}
    assert {"zh-cav-buzu", "zh-cav-jinshen", "zh-def-mouzhong", "zh-def-huoke", "zh-apol-paozhuan",
            "zh-apol-zhizheng", "zh-disc-pianfu", "zh-disc-wuyi", "zh-just-yanjin", "zh-just-youliyou"} <= ids


@pytest.mark.parametrize("lang,text", list(DEFENSIVE_SAMPLES.items()))
def test_each_catalog_language_flags_defensive_writing(lang, text):
    d = diagnose(text, lang)
    cats = {f["category"] for f in d["findings"]}
    assert {"preemptive-caveat", "apologetic-framing", "disclaimer"} <= cats, (lang, d["findings"])
    assert d["defensive"] >= 3


def test_warranted_uncertainty_is_not_flagged_as_defensive():
    text = ("In this cohort, exposure is associated with a 12% higher risk (95% CI 3-21%) (Lee, 2020). "
            "The design is observational, so the estimate may still reflect confounding by income. "
            "Self-reported smoking usually understates exposure, which would bias the estimate towards zero.")
    d = diagnose(text, "en")
    assert d["defensive"] == 0, d["findings"]


def test_hedge_pileup_and_blanket():
    pileup = "The results may perhaps suggest that the effect could possibly be larger than expected."
    ids = {f["id"] for f in diagnose(pileup, "en")["findings"]}
    assert "struct-hedge-pileup" in ids
    blanket = ("The effect may be larger in cities. Rural areas might show less change. "
               "Older voters could respond differently. Turnout probably fell overall.")
    d = diagnose(blanket, "en")
    assert any(f["id"] == "struct-hedge-blanket" for f in d["findings"])
    assert d["hedge_rate"] == 1.0
    plain = ("The effect is larger in cities (Table 2). Rural areas show less change. "
             "Older voters respond the same way. Turnout may have fallen overall.")
    d = diagnose(plain, "en")
    assert not any(f["category"] == "hedge-blanket" for f in d["findings"])
    assert d["hedge_rate"] == 0.25


def test_hedge_rate_is_none_without_a_hedge_list():
    d = diagnose("Questo studio analizza il caso. Forse il caso è raro. Forse no.", "it")
    assert d["hedge_rate"] is None
    assert not any(f["category"] == "hedge-blanket" for f in d["findings"])


def test_quoted_defensive_phrasing_is_not_flagged():
    text = 'The minister said, "It could be argued that further research is needed." (Ng, 2020)'
    assert diagnose(text, "en")["defensive"] == 0


EN_DEFENSIVE_POLISHED = (
    "Students who received peer feedback revised more (Lee, 2020). The courses were not randomized, "
    "so this is an association. The review covers two courses."
)


def test_report_rejects_silently_dropped_hedges():
    r = build_polish_report(EN_DEFENSIVE, EN_DEFENSIVE_POLISHED, "standard")
    assert r["invariants"]["hedges"]["polished"] < r["invariants"]["hedges"]["original"]
    assert any("hedges fell" in e for e in validate_polish_report(r))


def test_report_accepts_hedges_dropped_with_calibration():
    ledger = [
        {"before": "may possibly suggest a potential benefit", "after": "revised more",
         "decision": "scoped", "warrant": "non-randomized courses: association only, stated once"},
        {"before": "These findings should be interpreted with caution.", "after": "",
         "decision": "consolidated", "warrant": "same limitation as the randomization sentence"},
    ]
    r = build_polish_report(EN_DEFENSIVE, EN_DEFENSIVE_POLISHED, "standard", calibration=ledger)
    assert validate_polish_report(r) == []
    validate_file(r, PROTOCOLS / "polish-report.schema.json")
    assert r["before"]["defensive"] > r["after"]["defensive"] == 0
    # a logged change in a defensive category also accounts for the drop
    r = build_polish_report(EN_DEFENSIVE, EN_DEFENSIVE_POLISHED, "standard",
                            changes=[{"category": "defensive-hedge", "before": "it could be argued that", "after": ""}])
    assert validate_polish_report(r) == []


def test_calibration_entries_are_checked():
    bad = [{"before": "a", "after": "b", "decision": "deleted", "warrant": "x"},
           {"before": "a", "after": "b", "decision": "removed", "warrant": "  "},
           {"before": "a", "decision": "kept"}]
    r = build_polish_report(EN_DEFENSIVE, EN_DEFENSIVE_POLISHED, "standard", calibration=bad)
    errors = validate_polish_report(r)
    assert any("unknown decision" in e for e in errors)
    assert any("needs a warrant" in e for e in errors)
    assert any("calibration[2] missing" in e for e in errors)
    with pytest.raises(ValidationError):
        validate_file(r, PROTOCOLS / "polish-report.schema.json")


def test_cli_diagnose_defensive_only(tmp_path, capsys):
    f = tmp_path / "t.txt"
    f.write_text("Furthermore, " + EN_DEFENSIVE, encoding="utf-8")
    assert cli_main(["diagnose", str(f), "--defensive"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["findings"] and all(x["category"] in ppe.DEFENSIVE_CATEGORIES for x in out["findings"])


def test_defensive_writing_reference_keeps_warranted_uncertainty():
    text = (MODULE_DIR / "references" / "defensive-writing.md").read_text(encoding="utf-8")
    assert "never licenses a stronger claim" in text
    assert "warrant test" in text.lower()
    for cat in ppe.DEFENSIVE_CATEGORIES:
        if cat != "hedge-stack":
            assert "`%s`" % cat in text, cat
