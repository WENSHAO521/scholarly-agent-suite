import os
import sys
import unittest


from scb.text_normalize import classify_heading, normalize_text

SAMPLE_IMRAD = """Introduction
This paper studies institutional mechanisms in policy diffusion.

We build on prior work in comparative politics.

Literature Review
Scholars have long debated the mechanisms of diffusion.

Methods
We use a mixed-methods design combining interviews and archival data.

Results
We find that coercive mechanisms dominate in centralized systems.

Discussion
These findings extend existing theory in several ways.

Conclusion
We conclude that mechanism-level analysis is essential.

References
Smith, J. (2020). Diffusion theory. Journal of Policy Studies.
Doe, A. (2019). Institutions and change. Comparative Politics Review.
"""

SAMPLE_HUMANITIES = """The Idea of Sovereignty in Early Modern Thought
This essay traces the concept of sovereignty from Bodin to Hobbes.

A Contested Inheritance
Bodin's formulation was contested almost immediately by his successors.

Toward a Modern Synthesis
By the mid-seventeenth century, a recognizably modern account emerges.
"""


class TestClassifyHeading(unittest.TestCase):
    def test_recognized_heading(self):
        self.assertEqual(classify_heading("Introduction"), "introduction")
        self.assertEqual(classify_heading("Methods"), "methods")
        self.assertEqual(classify_heading("1. Introduction"), "introduction")

    def test_unrecognized_heading_is_other_not_forced(self):
        self.assertEqual(classify_heading("A Contested Inheritance"), "other")


class TestNormalizeTextImrad(unittest.TestCase):
    def setUp(self):
        self.doc = normalize_text(SAMPLE_IMRAD, title="T", abstract="A")

    def test_sections_extracted_with_roles(self):
        roles = [s.role for s in self.doc.sections]
        self.assertIn("introduction", roles)
        self.assertIn("methods", roles)
        self.assertIn("results", roles)
        self.assertIn("discussion", roles)
        self.assertIn("conclusion", roles)

    def test_references_extracted_separately_not_lost(self):
        self.assertEqual(len(self.doc.references), 2)
        self.assertIn("Smith, J. (2020). Diffusion theory. Journal of Policy Studies.", self.doc.references)
        # References section itself must not appear in doc.sections
        self.assertNotIn("references", [s.role for s in self.doc.sections])

    def test_methods_section_content_preserved(self):
        methods = self.doc.section_by_role("methods")
        self.assertEqual(len(methods), 1)
        self.assertIn("mixed-methods design", methods[0].text)


class TestNormalizeTextHumanities(unittest.TestCase):
    def test_does_not_force_imrad_labels_on_humanities_headings(self):
        doc = normalize_text(SAMPLE_HUMANITIES)
        roles = [s.role for s in doc.sections]
        # None of these headings map to IMRaD roles — they must stay "other",
        # not be silently coerced into introduction/methods/etc.
        self.assertTrue(all(r in ("front_matter", "other") for r in roles))

    def test_original_heading_text_preserved_verbatim(self):
        doc = normalize_text(SAMPLE_HUMANITIES)
        headings = [s.heading for s in doc.sections if s.heading]
        self.assertIn("A Contested Inheritance", headings)


if __name__ == "__main__":
    unittest.main()
