import os
import sys
import unittest


from scb.versions import (
    ACCEPTED_MANUSCRIPT,
    PREPRINT,
    REPOSITORY_COPY,
    VERSION_OF_RECORD,
    VersionEntry,
    resolve_versions,
    to_dict,
)


class TestVersionResolution(unittest.TestCase):
    def test_version_of_record_is_bibliographic_authority(self):
        entries = [
            VersionEntry(kind=PREPRINT, is_open=True, url="http://arxiv.org/abs/1"),
            VersionEntry(kind=VERSION_OF_RECORD, is_open=False, url="http://publisher.example/1"),
        ]
        resolution = resolve_versions(entries)
        self.assertEqual(resolution.bibliographic_authority.kind, VERSION_OF_RECORD)

    def test_open_repository_copy_preferred_for_access_when_vor_closed(self):
        entries = [
            VersionEntry(kind=VERSION_OF_RECORD, is_open=False, url="http://publisher.example/1"),
            VersionEntry(kind=REPOSITORY_COPY, is_open=True, url="http://repo.example/1"),
        ]
        resolution = resolve_versions(entries)
        self.assertEqual(resolution.bibliographic_authority.kind, VERSION_OF_RECORD)
        self.assertEqual(resolution.best_lawful_access.kind, REPOSITORY_COPY)

    def test_no_open_version_means_no_lawful_access(self):
        entries = [VersionEntry(kind=VERSION_OF_RECORD, is_open=False)]
        resolution = resolve_versions(entries)
        self.assertIsNone(resolution.best_lawful_access)

    def test_authority_never_overwritten_by_access_preference(self):
        entries = [
            VersionEntry(kind=ACCEPTED_MANUSCRIPT, is_open=True),
            VersionEntry(kind=VERSION_OF_RECORD, is_open=False),
        ]
        resolution = resolve_versions(entries)
        # VoR still wins bibliographic authority even though it is closed.
        self.assertEqual(resolution.bibliographic_authority.kind, VERSION_OF_RECORD)
        self.assertEqual(resolution.best_lawful_access.kind, ACCEPTED_MANUSCRIPT)

    def test_empty_input(self):
        resolution = resolve_versions([])
        self.assertIsNone(resolution.bibliographic_authority)
        self.assertIsNone(resolution.best_lawful_access)

    def test_to_dict_serializes(self):
        entries = [VersionEntry(kind=VERSION_OF_RECORD, is_open=True, url="http://x")]
        d = to_dict(resolve_versions(entries))
        self.assertEqual(d["bibliographic_authority"]["kind"], VERSION_OF_RECORD)


if __name__ == "__main__":
    unittest.main()
