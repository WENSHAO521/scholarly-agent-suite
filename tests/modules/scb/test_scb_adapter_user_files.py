import io
import os
import shutil
import sys
import tempfile
import unittest
import zipfile


from scb.adapters.user_files import ExtractionUnavailable, UnsupportedFileType, UserFileAdapter

_DOCX_DOCUMENT_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p><w:r><w:t>First paragraph of the manuscript.</w:t></w:r></w:p>
    <w:p><w:r><w:t>Second paragraph, with a claim and evidence.</w:t></w:r></w:p>
  </w:body>
</w:document>
"""


def _make_docx(path):
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("word/document.xml", _DOCX_DOCUMENT_XML)


class TestUserFileAdapter(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="scb-userfiles-")
        self.adapter = UserFileAdapter()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _write(self, name, content, mode="w", encoding="utf-8"):
        path = os.path.join(self.tmp, name)
        if mode == "w":
            with open(path, "w", encoding=encoding) as f:
                f.write(content)
        else:
            with open(path, "wb") as f:
                f.write(content)
        return path

    def test_txt_extraction(self):
        path = self._write("a.txt", "Hello scholarly world.")
        doc = self.adapter.extract_text(path)
        self.assertEqual(doc.text, "Hello scholarly world.")
        self.assertEqual(doc.source_format, "text")

    def test_markdown_extraction(self):
        path = self._write("a.md", "# Title\n\nSome body text.")
        doc = self.adapter.extract_text(path)
        self.assertIn("Some body text.", doc.text)
        self.assertEqual(doc.source_format, "markdown")

    def test_html_extraction_strips_tags_and_scripts(self):
        html = "<html><head><style>.x{}</style></head><body><h1>Title</h1><p>Body text.</p><script>evil()</script></body></html>"
        path = self._write("a.html", html)
        doc = self.adapter.extract_text(path)
        self.assertIn("Body text.", doc.text)
        self.assertNotIn("evil()", doc.text)

    def test_xml_extraction(self):
        xml = "<doc><title>T</title><para>Body content.</para></doc>"
        path = self._write("a.xml", xml)
        doc = self.adapter.extract_text(path)
        self.assertIn("Body content.", doc.text)

    def test_docx_extraction(self):
        path = os.path.join(self.tmp, "a.docx")
        _make_docx(path)
        doc = self.adapter.extract_text(path)
        self.assertIn("First paragraph of the manuscript.", doc.text)
        self.assertIn("Second paragraph, with a claim and evidence.", doc.text)

    def test_pdf_without_extractor_raises_extraction_unavailable(self):
        path = self._write("a.pdf", b"%PDF-1.4 fake", mode="wb")
        with self.assertRaises(ExtractionUnavailable):
            self.adapter.extract_text(path)

    def test_pdf_with_injected_extractor_succeeds(self):
        path = self._write("a.pdf", b"%PDF-1.4 fake", mode="wb")
        adapter = UserFileAdapter(pdf_extractor=lambda raw: "extracted pdf text")
        doc = adapter.extract_text(path)
        self.assertEqual(doc.text, "extracted pdf text")

    def test_unsupported_extension_raises(self):
        path = self._write("a.exe", b"binary", mode="wb")
        with self.assertRaises(UnsupportedFileType):
            self.adapter.extract_text(path)

    def test_capabilities_declares_lookup_only(self):
        caps = self.adapter.capabilities.as_list()
        self.assertEqual(caps, ["lookup"])


if __name__ == "__main__":
    unittest.main()
