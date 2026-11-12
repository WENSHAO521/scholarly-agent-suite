"""translation-engine runtime (tre): language and variety facts, glossary,
invariant checks across language pairs, TRANSLATION_REPORT_V1, and the CLI."""
import json
from pathlib import Path

import pytest
from schema_lite import ValidationError, validate_file

from tre import MODES, TRANSLATION_NOTICE
from tre.__main__ import main as cli_main
from tre.glossary import check_glossary, load_glossary, term_candidates
from tre.invariants import check_translation, citation_names, extract
from tre.languages import detect_language, same_script, variety_mismatches
from tre.report import bilingual, build_translation_report, validate_translation_report

ROOT = Path(__file__).resolve().parents[3]
PROTOCOLS = ROOT / "skills" / "scholarly-agent" / "protocols"
MODULE_DIR = ROOT / "skills" / "scholarly-agent" / "modules" / "translation-engine"

ZH = (
    "本研究以臺灣 22 個縣市為樣本，探討數位治理能力對公共服務品質的影響（Lee & Chen, 2021; Wang 等人, 2019）。"
    "結果顯示，數位治理能力可能提升服務品質（β = 0.32, p < .05），但並非所有縣市皆然。\n\n"
    "本文所稱數位治理能力，係指地方政府運用資訊系統整合服務的能力，以下簡稱 DGC。"
    "資料取自 https://data.gov.tw/dataset/123 與 doi:10.1234/abcd.2020.5。\n\n"
    "研究限制在於樣本僅涵蓋 2015 至 2020 年，且 DGC 的測量仍以自評為主。"
)
EN = (
    "Using a sample of 22 municipalities and counties in Taiwan, this study examines how digital governance "
    "capacity affects the quality of public services (Lee & Chen, 2021; Wang et al., 2019). The results show "
    "that digital governance capacity may improve service quality (β = 0.32, p < .05), although this does not "
    "hold for every county.\n\n"
    "In this article, digital governance capacity refers to a local government's ability to integrate services "
    "through information systems (hereafter DGC). Data were drawn from https://data.gov.tw/dataset/123 and "
    "doi:10.1234/abcd.2020.5.\n\n"
    "The study is limited in that the sample covers only 2015 to 2020, and DGC is still measured mainly by "
    "self-assessment."
)
GLOSSARY = [{"source": "數位治理能力", "target": "digital governance capacity"}, {"source": "DGC", "keep": True}]


def test_clean_translation_passes_and_validates_against_schema():
    r = build_translation_report(ZH, EN, "en", "zh-Hant", glossary=GLOSSARY)
    assert r["status"] == "PASS", r["invariants"]
    assert validate_translation_report(r) == []
    validate_file(r, PROTOCOLS / "translation-report.schema.json")
    assert r["notice"] == TRANSLATION_NOTICE
    assert {g["status"] for g in r["glossary"]} == {"kept"}


def test_changed_number_fails():
    r = build_translation_report(ZH, EN.replace("22", "23"), "en", "zh-Hant")
    assert r["status"] == "FAIL"
    assert any("numbers" in f for f in r["invariants"]["failures"])


def test_decimal_comma_and_full_width_digits_match():
    src = "The effect was 12.5% (n = 1,204) in 2020."
    assert check_translation(src, "L'effet était de 12,5 % (n = 1 204) en 2020.", "en", "fr")["status"] != "FAIL"
    assert check_translation("效果為１２．５％。", "The effect was 12.5%.", "zh", "en")["checks"]["numbers"]["missing"] == []


def test_dropped_citation_author_and_year_fail():
    bad = EN.replace("Lee & Chen, 2021; ", "")
    r = check_translation(ZH, bad, "zh", "en")
    assert r["status"] == "FAIL"
    text = " ".join(r["failures"])
    assert "Lee" in text and "citation years" in text


def test_transliterated_name_alone_fails_but_kept_beside_passes():
    src = "This was argued earlier (Smith, 2020)."
    assert check_translation(src, "此點早已有人指出（史密斯，2020）。", "en", "zh")["status"] == "FAIL"
    assert "Smith" not in " ".join(check_translation(src, "此點早已有人指出（史密斯 Smith，2020）。", "en", "zh")["failures"])


def test_numbered_citations_dois_urls_math_and_code_are_exact():
    src = "As shown [3, 5], see https://example.org/x and 10.5555/abc.1 where $x^2$ uses `fit()`."
    ok = "如文獻所示 [3, 5]，見 https://example.org/x 與 10.5555/abc.1，其中 $x^2$ 使用 `fit()`。"
    assert check_translation(src, ok, "en", "zh")["status"] == "PASS"
    e = extract(src)
    assert e["numbered_citations"] == ["[3,5]"] and e["math"] == ["$x^2$"] and e["code"] == ["`fit()`"]
    bad = ok.replace("$x^2$", "x 的平方").replace("[3, 5]", "[3]")
    r = check_translation(src, bad, "en", "zh")
    assert r["status"] == "FAIL"
    assert r["checks"]["math"]["missing"] == ["$x^2$"]


def test_cjk_number_units_downgrade_number_mismatch_to_review():
    r = check_translation("The program served 15,000 students.", "該計畫服務了 1.5 萬名學生。", "en", "zh")
    assert r["status"] == "REVIEW"
    assert not r["failures"]


def test_target_in_wrong_language_fails():
    r = check_translation(EN, EN, "en", "zh")
    assert r["status"] == "FAIL"
    assert any("not the requested" in f for f in r["failures"])


def test_untranslated_source_script_is_flagged_outside_parentheses():
    left = EN.replace("public services", "公共服務品質")
    r = check_translation(ZH, left, "zh", "en")
    assert "公共服務品質" in r["untranslated"]
    glossed = EN.replace("public services", "public services (公共服務)")
    assert check_translation(ZH, glossed, "zh", "en")["untranslated"] == []


def test_untranslated_latin_runs_need_four_words():
    src = "We use a panel design (Smith, 2020). The results hold across all regions studied here."
    tgt = "本研究採用 panel design（Smith, 2020）。The results hold across all regions studied here."
    r = check_translation(src, tgt, "en", "zh")
    assert any("results hold across" in u for u in r["untranslated"])
    assert not any(u.strip() == "panel design" for u in r["untranslated"])


def test_traditional_target_with_simplified_characters_is_flagged():
    assert variety_mismatches("我们的研究這個", "zh-Hant") == ["们"]
    assert set(variety_mismatches("這個學說", "zh-Hans")) == {"這", "個", "學", "說"}
    assert variety_mismatches("這個學說", "pt-BR") == []
    r = check_translation(EN, ZH.replace("數位", "数位"), "en", "zh", variety="zh-Hant")
    assert r["status"] == "REVIEW"
    assert r["checks"]["variety"]["mismatched_characters"] == ["数"]


def test_dropped_hedge_and_negation_are_flagged_per_paragraph():
    strong = EN.replace("may improve", "improves").replace("does not hold", "holds")
    r = check_translation(ZH, strong, "zh", "en")
    joined = " ".join(r["warnings"])
    assert "hedge" in joined and "negation" in joined


def test_paragraph_count_change_is_flagged():
    merged = EN.replace("\n\n", " ", 1)
    r = check_translation(ZH, merged, "zh", "en")
    assert r["paragraphs"]["target"] == 2
    assert any("paragraphs" in w for w in r["warnings"])


def test_glossary_missing_term_fails_report():
    drift = EN.replace("digital governance capacity", "digital administration ability")
    r = build_translation_report(ZH, drift, "en", "zh-Hant", glossary=GLOSSARY)
    assert r["status"] == "FAIL"
    assert [g["status"] for g in r["glossary"]][0] == "missing"
    assert validate_translation_report(r) == []


def test_glossary_count_differs_is_review():
    one = EN.replace("digital governance capacity affects", "it affects", 1)
    res = check_glossary(ZH, one, GLOSSARY)
    assert res[0]["status"] == "count-differs"


def test_glossary_loads_json_and_tsv(tmp_path):
    j = tmp_path / "g.json"
    j.write_text(json.dumps({"治理": "governance", "OECD": "="}), encoding="utf-8")
    t = tmp_path / "g.tsv"
    t.write_text("# comment\n治理\tgovernance\nOECD\t=\nSDG\n", encoding="utf-8")
    assert load_glossary(j) == [{"source": "治理", "target": "governance"}, {"source": "OECD", "keep": True}]
    assert load_glossary(t)[2] == {"source": "SDG", "keep": True}
    with pytest.raises(ValueError):
        load_glossary([{"target": "x"}])


def test_term_candidates_find_acronyms_and_defined_terms():
    terms = {t["term"]: t["kind"] for t in term_candidates(
        "Public value (PV) matters. PV is contested. We call this hereafter policy capacity, and the OECD agrees.")}
    assert terms.get("PV") in ("acronym", "defined")
    assert "OECD" in terms
    zh_terms = [t["term"] for t in term_candidates(ZH, "zh")]
    assert "DGC" in zh_terms and "數位治理能力" in zh_terms


def test_citation_names_skip_non_names():
    assert citation_names("(See Smith & Jones, 2020, p. 4; Lee et al., 2019a) and Brown (2018)") == [
        "Brown", "Jones", "Lee", "Smith"]


def test_report_validator_catches_tampering():
    r = build_translation_report(ZH, EN, "en", "zh-Hant", glossary=GLOSSARY)
    bad = dict(r, status="PASS", invariants=dict(r["invariants"], status="FAIL"))
    assert any("FAIL" in e for e in validate_translation_report(bad))
    assert validate_translation_report(dict(r, notice="Guaranteed accurate.")) != []
    assert validate_translation_report(dict(r, mode="creative")) != []
    assert validate_translation_report(dict(r, notes=[{"kind": "vibe", "note": "x"}])) != []
    assert validate_translation_report(dict(r, source_language="Chinese")) != []
    with pytest.raises(ValidationError):
        validate_file(dict(r, mode="creative"), PROTOCOLS / "translation-report.schema.json")
    with pytest.raises(ValueError):
        build_translation_report(ZH, EN, "en", mode="creative")


def test_notes_and_escalations_round_trip_schema():
    r = build_translation_report(ZH, EN, "en", "zh-Hant", mode="academic", variety=None,
                                 notes=[{"kind": "term", "note": "縣市 rendered as municipalities and counties"}],
                                 escalations=["source gives 22 units but Table 1 lists 21"])
    validate_file(r, PROTOCOLS / "translation-report.schema.json")
    assert r["mode"] in MODES and r["escalations"]


def test_bilingual_view_pairs_paragraphs_and_shows_gaps():
    view = bilingual(ZH, EN.split("\n\n")[0])
    assert view.count("**¶") == 6
    assert "(no paragraph)" in view


def test_language_helpers():
    assert detect_language(ZH) == "zh"
    assert detect_language("Die Rolle der Institutionen ist nicht klar und das ist wichtig.") == "de"
    assert same_script("zh-Hant", "ja") and not same_script("en", "ru")


def test_cli_check_and_terms(tmp_path, capsys):
    s, t, g = tmp_path / "s.txt", tmp_path / "t.txt", tmp_path / "g.tsv"
    s.write_text(ZH, encoding="utf-8")
    t.write_text(EN, encoding="utf-8")
    g.write_text("數位治理能力\tdigital governance capacity\nDGC\t=\n", encoding="utf-8")
    assert cli_main(["check", str(s), str(t), "--to", "en", "--from", "zh-Hant", "--glossary", str(g)]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["protocol"] == "TRANSLATION_REPORT_V1" and out["status"] == "PASS"
    t.write_text(EN.replace("2019", "2018"), encoding="utf-8")
    assert cli_main(["check", str(s), str(t), "--to", "en"]) == 1
    capsys.readouterr()
    assert cli_main(["terms", str(s)]) == 0
    assert any(x["term"] == "DGC" for x in json.loads(capsys.readouterr().out))
    assert cli_main(["bilingual", str(s), str(t)]) == 0


def test_module_page_documents_runtime_and_integrity():
    text = (MODULE_DIR / "MODULE.md").read_text(encoding="utf-8")
    for needle in ("tre.report", "TRANSLATION_REPORT_V1", "python -m tre", "zh-Hant", "disclos"):
        assert needle in text
