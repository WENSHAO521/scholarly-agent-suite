# Journal Profile

## Purpose

Learn the observable writing architecture of a target journal from a sampled
corpus of its articles. This is an **empirical profile of sampled articles**,
never a claim about the journal's mandatory style — see the Journal
Instructions vs Observed Corpus distinction in `SKILL.md`.

## Sampling rules

- Default window: last 2–3 years, adapted to publication volume, field
  stability, and user request. Always record the actual sampling period used.
- Default size: 20–50 articles. A small, diversified corpus is usually more
  useful than hundreds of undifferentiated papers.
- Diversify by: year, article type, subfield/topic, methods, issue, and
  author. Avoid overrepresenting one special issue, one prolific author, one
  laboratory, or one article genre.
- **Article type discipline**: a special issue is not the whole journal, an
  editorial is not an empirical article, and a review article is not original
  research. Sample within a clearly recorded article-type scope, and record
  that scope in the manifest.

## Extractable characteristics

```text
title length
abstract architecture and length
introduction structure
literature placement
contribution placement
section naming
methods visibility
results/discussion separation
policy-implication frequency
first-person usage
sentence variation
citation density
limitations placement
```

## Schema

```json
{
  "journal": "",
  "issn": [],
  "sample_window": "",
  "sample_size": 0,
  "article_types": [],
  "profile_generated_at": "",
  "source_provenance": [],
  "abstract": {
    "typical_structure": [],
    "contribution_position": ""
  },
  "introduction": {
    "dominant_architecture": "",
    "literature_density": "",
    "contribution_position": ""
  },
  "prose": {
    "sentence_length": "",
    "sentence_variation": "",
    "first_person": "",
    "rhetorical_intensity": "",
    "qualification_density": ""
  },
  "citations": {
    "density": "",
    "dominant_placement": ""
  },
  "sections": {
    "common_patterns": []
  },
  "limitations": [],
  "confidence": "medium"
}
```

## Example output

```text
Target: Journal X
Corpus: 32 original research articles, 2024-2026

Observed profile:
- Contribution typically appears in the first third of the introduction.
- Literature review is integrated rather than fully separated.
- First-person plural is moderately common.
- Discussion sections frequently distinguish empirical findings from policy
  implications.

Limitations:
- Open-access sample overrepresented.
- Special issues excluded.
```

## Freshness

Refresh approximately every 6–12 months; 3–6 months for fast-moving
computing/AI venues where current style materially matters. See
`refresh-policy.md` for the Corpus Selection Gate and incremental refresh.

## Do not

- Present observed patterns as formal submission requirements.
- Infer that a higher-impact journal has "better" prose — this skill is
  descriptive, not evaluative.
- Rebuild the corpus from scratch on every request when a `CURRENT` cached
  profile already exists.
