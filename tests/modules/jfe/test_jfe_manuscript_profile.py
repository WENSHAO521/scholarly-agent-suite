import unittest

from jfe.manuscript_profile import ManuscriptProfile, ProfileError


class ManuscriptProfileTests(unittest.TestCase):
    def test_defaults_are_all_unknown(self):
        profile = ManuscriptProfile()
        self.assertIsNone(profile.discipline)
        self.assertEqual(profile.methods, [])
        self.assertEqual(profile.validate(), [])

    def test_from_dict_rejects_unknown_field(self):
        with self.assertRaises(ProfileError):
            ManuscriptProfile.from_dict({"discipline": "sociology", "made_up": True})

    def test_from_dict_valid(self):
        profile = ManuscriptProfile.from_dict({
            "discipline": "public administration",
            "topic": "policy diffusion",
            "article_type": "original-research",
        })
        self.assertEqual(profile.discipline, "public administration")
        self.assertEqual(profile.article_type, "original-research")

    def test_invalid_article_type_rejected(self):
        with self.assertRaises(ProfileError):
            ManuscriptProfile.from_dict({"article_type": "not-a-real-type"})

    def test_negative_word_count_rejected(self):
        profile = ManuscriptProfile(word_count=-5)
        errors = profile.validate()
        self.assertTrue(any("word_count" in e for e in errors))

    def test_keywords_extracted_from_free_text_fields(self):
        profile = ManuscriptProfile(
            discipline="public administration",
            topic="policy diffusion across states",
            theory="institutional isomorphism",
        )
        keywords = profile.keywords()
        self.assertIn("public", keywords)
        self.assertIn("administration", keywords)
        self.assertIn("diffusion", keywords)
        self.assertIn("isomorphism", keywords)

    def test_keywords_drop_short_tokens(self):
        profile = ManuscriptProfile(topic="an api of it")
        keywords = profile.keywords()
        self.assertNotIn("an", keywords)
        self.assertNotIn("of", keywords)
        self.assertNotIn("it", keywords)
        self.assertIn("api", keywords)  # length 3, kept

    def test_keywords_empty_when_no_text_fields_set(self):
        self.assertEqual(ManuscriptProfile().keywords(), [])

    def test_keywords_drop_stopwords(self):
        # "and" is 3 characters and would otherwise pass the length filter,
        # then show up as fake "topic overlap" evidence against any journal
        # topic name containing "and" (e.g. "Policy and Administration").
        profile = ManuscriptProfile(topic="policy and administration studies")
        keywords = profile.keywords()
        self.assertNotIn("and", keywords)
        self.assertIn("policy", keywords)
        self.assertIn("administration", keywords)


if __name__ == "__main__":
    unittest.main()
