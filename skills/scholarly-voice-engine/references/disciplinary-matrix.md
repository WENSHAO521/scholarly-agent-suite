# Disciplinary Matrix

Routing table from a user's stated or implied field to the discipline module(s) in
`disciplines/`. Load only what the task needs.

| Family | Example fields | Module |
|---|---|---|
| Natural sciences | Physics, chemistry, biology, earth science, environmental science, astronomy, materials science, neuroscience, ecology, evolutionary biology | `disciplines/natural-sciences.md` |
| Mathematics & formal sciences | Pure/applied mathematics, statistics, logic, operations research, theoretical CS, information theory | `disciplines/mathematics-formal.md` |
| Engineering & computing | Computer science, AI, software engineering, electrical/mechanical/civil/chemical/biomedical engineering, robotics, systems engineering, data science | `disciplines/engineering-computing.md` |
| Medicine & health sciences | Clinical medicine, public health, epidemiology, nursing, pharmacy, dentistry, biomedical sciences, health policy, digital health, medical AI, psychiatry | `disciplines/medicine-health.md` |
| Social sciences | Political science, public administration, public policy, economics, sociology, psychology, anthropology, IR, communication, criminology, human geography, demography, social policy | `disciplines/social-sciences.md` |
| Business & management | Management, organization studies, strategy, marketing, finance, accounting, entrepreneurship, HRM, operations management, innovation studies | `disciplines/business-management.md` |
| Law | Public/private law, international law, comparative law, constitutional/administrative/criminal law, legal theory, law and society | `disciplines/law.md` |
| Humanities | Philosophy, history, literature, linguistics, religious studies, classics, art history, cultural studies, intellectual history, ethics, political thought | `disciplines/humanities.md` |
| Education | Education policy, curriculum studies, higher education, educational psychology, pedagogy, comparative education, teacher education, ed-tech | `disciplines/education.md` |
| Arts & practice-based research | Music, performance studies, fine arts, design research, architecture, film studies, theatre, creative practice research | `disciplines/arts-design.md` |
| Interdisciplinary | STS, digital humanities, computational social science, environmental humanities, bioethics, health humanities, urban studies, development studies, sustainability studies, complexity science, AI governance | `disciplines/interdisciplinary.md` + each contributing home discipline |

**Economics, philosophy, and history** are grouped into `social-sciences.md`
and `humanities.md` respectively for routing (they share those families'
citation/evidence infrastructure), but each has distinctive-enough
conventions to warrant a dedicated subsection within its family file —
see the "Economics" heading in `disciplines/social-sciences.md` and the
"Philosophy" / "History" headings in `disciplines/humanities.md`. Route to
the family file as usual, then to the matching subsection.

## Inference procedure

1. If the user states a field or journal, map it to a row above.
2. If unstated, infer from content cues: notation and proofs → mathematics; wet-lab
   or clinical data → natural sciences/medicine; case law and statutes → law;
   close reading of texts → humanities; institutional/survey data → social science;
   firm-level strategy questions → business.
3. If two families are both clearly present (e.g., a bioethics piece mixing
   philosophy and medicine), treat it as interdisciplinary: pick a **home**
   discipline (the one whose evidentiary standard governs) and a **secondary**
   discipline, and load `interdisciplinary-writing.md` alongside both modules.
4. If genuinely ambiguous and the choice would materially change claim style or
   citation behavior, ask rather than guess.

## Adding a discipline without rewriting the core Skill

`SKILL.md` never enumerates discipline files by name in its control flow — it
loads "the matching file in `disciplines/`." To add a new discipline family:

1. Add a row to the table above.
2. Add `disciplines/<name>.md` using the schema documented at the top of any
   existing discipline file.
3. Add 2–3 cases to `evals/discipline-cases.jsonl`.

No other file needs to change.
