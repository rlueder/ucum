"""Regression checks for image references in the publishing transforms.

Run with: python3 -m unittest discover -s tests
Requires Java and the repository's bundled Saxon processor.
"""

from html.parser import HTMLParser
from pathlib import Path
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]


def transform(source, stylesheet, output):
    subprocess.run(
        ["java", "-jar", str(ROOT / "build/saxon8.jar"), "-o", str(output),
         str(source), str(ROOT / "build" / stylesheet)],
        check=True, capture_output=True, text=True,
    )


class ImageSources(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sources = []

    def handle_starttag(self, tag, attrs):
        if tag == "img":
            self.sources.append(dict(attrs).get("src"))


class GraphicsTests(unittest.TestCase):
    def test_image_reference_forms(self):
        cases = [
            ("https://example.org/diagram.gif", "https://example.org/diagram.gif"),
            ("http://example.org/diagram.gif", "http://example.org/diagram.gif"),
            ("//example.org/diagram.gif", "//example.org/diagram.gif"),
            ("/assets/diagram.gif", "/assets/diagram.gif"),
            ("diagram.gif", "graphics/diagram.gif"),
            ("subdir/diagram.gif", "graphics/subdir/diagram.gif"),
        ]
        source = ET.Element("spec")
        for tag in ("figure", "uml"):
            for reference, expected in cases:
                figure = ET.SubElement(source, tag)
                ET.SubElement(figure, "pixmap", source=reference)
                ET.SubElement(figure, "caption").text = "Diagram caption"
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            input_file, output_file = directory / "input.xml", directory / "output.xml"
            ET.ElementTree(source).write(input_file, encoding="utf-8")
            transform(input_file, "v3dt-v3pub.xsl", output_file)
            graphics = ET.parse(output_file).getroot().findall("graphic")
        self.assertEqual(len(graphics), len(cases) * 2)
        for graphic, (reference, expected) in zip(graphics, cases * 2):
            with self.subTest(reference=reference):
                self.assertEqual(graphic.get("source"), expected)
                self.assertEqual(graphic.get("alt"), "Diagram caption")

    def test_specification_html_image(self):
        """A complete rebuild must retain the source specification's HTTPS URL."""
        reference = ET.parse(ROOT / "ucum-source.xml").find(".//figure/pixmap").get("source")
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            intermediate, html = directory / "ucum.xml", directory / "ucum.html"
            transform(ROOT / "ucum-source.xml", "v3dt-v3pub.xsl", intermediate)
            transform(intermediate, "V3mLayoutHTML20.xsl", html)
            parser = ImageSources()
            parser.feed(html.read_text(encoding="utf-8"))
        self.assertIn(reference, parser.sources)


if __name__ == "__main__":
    unittest.main()
