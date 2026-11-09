# Shared discipline taxonomy

One set of discipline families for every module. A module that keeps
per-discipline guidance keeps exactly one file per family, named by the
**slug** below, in its own `disciplines/` directory:

- `modules/scholarly-voice-engine/disciplines/` -- writing conventions
  (claim style, argument structure, citation behavior, voice).
- `modules/journal-fit-engine/disciplines/` -- venue-fit emphasis (which fit
  dimensions weigh most when matching a manuscript to journals).

The two directories answer different questions about the same field, so
their content differs; their file names must not. `tests/test_disciplines.py`
enforces that both directories match this table exactly. Inside YAML and JSON
(for example `discipline_family:` in the voice files), use the **id**
column, which is the slug with `_` instead of `-`.

| Slug | Id | Covers |
|---|---|---|
| `natural-sciences` | `natural_sciences` | Physics, chemistry, biology, astronomy, earth and environmental sciences, ecology, materials science, neuroscience |
| `mathematics-formal` | `mathematics_formal` | Pure and applied mathematics, statistics, logic, operations research, information theory, theoretical computer science |
| `engineering-computing` | `engineering_computing` | Computer science, AI/ML, software, electrical, mechanical, civil, and chemical engineering |
| `medicine-health` | `medicine_health` | Clinical medicine, biomedical sciences, epidemiology, public health, nursing, pharmacy, health policy |
| `social-sciences` | `social_sciences` | Political science, public administration and policy, economics, sociology, psychology, anthropology, international relations, communication |
| `business-management` | `business_management` | Management, organization studies, strategy, marketing, finance, accounting, entrepreneurship, operations |
| `law` | `law` | Constitutional, administrative, international, comparative, criminal, and private law; legal theory; law and society |
| `humanities` | `humanities` | Philosophy, history, literature, linguistics, religious studies, classics, cultural studies, intellectual history |
| `arts-design` | `arts_design` | Music, performance, fine arts, design research, architecture, film, theatre, practice-based research |
| `education` | `education` | Education policy, higher education, curriculum, pedagogy, teacher education, educational psychology and technology |
| `interdisciplinary` | `interdisciplinary` | Work whose contribution depends on combining families (STS, sustainability, AI governance, digital humanities, bioethics) |

## Rules

- A manuscript or profile names its **primary** family; secondary families
  go in `subdisciplines` or the interdisciplinary file's guidance, never as a
  second primary.
- Subfields (for example "public administration") map to their family;
  do not add a family for a subfield. Add a family only when both modules
  need distinct guidance for it, and add both files in the same change.
- Free-text `discipline` fields in protocols (for example
  `MANUSCRIPT_PROFILE_V1.discipline`) stay free text; the family is how a
  module picks its guidance file, not a validation vocabulary.
