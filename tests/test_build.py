"""Build, artifact-consistency and dependency checks; not UCUM conformance tests."""

from html.parser import HTMLParser
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
NAMESPACE = "{http://unitsofmeasure.org/ucum-essence}"
SOURCE_NAMESPACE = "{http://aurora.regenstrief.org/UCUM}"
ARTIFACTS = ("ucum.xml", "ucum.html", "ucum-essence.xml", "ucum-cs.units", "ucum-ci.units")


class HTMLSnapshot(HTMLParser):
    """Compare markup and text while ignoring serialization whitespace."""

    def __init__(self, path):
        super().__init__()
        self.tokens = []
        self.resources = []
        self.feed(path.read_text(encoding="utf-8"))

    def handle_starttag(self, tag, attrs):
        self.tokens.append((tag, tuple(sorted(attrs))))
        attrs = dict(attrs)
        reference = attrs.get("src") if tag in ("img", "script") else attrs.get("href") if tag == "link" else None
        if reference:
            self.resources.append(reference)

    def handle_endtag(self, tag):
        self.tokens.append(("/" + tag,))

    def handle_data(self, data):
        self.tokens.extend(data.split())


class BuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="ucum-build-")
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.build = Path(cls.temporary.name)
        for directory in ("build", "assets"):
            shutil.copytree(ROOT / directory, cls.build / directory)
        for name in ("Makefile", "ucum-source.xml"):
            shutil.copy2(ROOT / name, cls.build / name)
        subprocess.run(["make", "-B", "all"], cwd=cls.build, check=True,
                       capture_output=True, text=True)

    def test_xml_and_definition_inventory(self):
        for path in list(ROOT.glob("*.xml")) + list((ROOT / "build").glob("*.xsl")):
            with self.subTest(path=path.name):
                ET.parse(path)
        source = ET.parse(ROOT / "ucum-source.xml").getroot()
        essence = ET.parse(self.build / "ucum-essence.xml").getroot()
        self.assertEqual(essence.tag, NAMESPACE + "root")
        for kind in ("prefix", "base-unit", "unit"):
            originals = source.findall(".//" + SOURCE_NAMESPACE + kind)
            generated = essence.findall(NAMESPACE + kind)
            self.assertTrue(originals, kind)
            for attribute in ("Code", "CODE"):
                self.assertEqual(sorted(item.get(attribute) for item in originals),
                                 sorted(item.get(attribute) for item in generated),
                                 (kind, attribute))

    def test_committed_artifacts_match_rebuild(self):
        for name in ARTIFACTS:
            with self.subTest(artifact=name):
                if name.endswith(".html"):
                    self.assertEqual(HTMLSnapshot(ROOT / name).tokens,
                                     HTMLSnapshot(self.build / name).tokens)
                else:
                    self.assertEqual((ROOT / name).read_bytes(), (self.build / name).read_bytes())

    def test_local_html_resources_exist(self):
        for directory in (ROOT, self.build):
            for reference in HTMLSnapshot(directory / "ucum.html").resources:
                with self.subTest(directory=directory.name, reference=reference):
                    url = urlsplit(reference)
                    if not url.scheme and not url.netloc:
                        self.assertTrue((directory / unquote(url.path).lstrip("/")).is_file())

    def test_incremental_build_dependencies(self):
        specification_outputs = ("ucum.xml", "ucum.html")
        dependencies = {
            "build/xml-verbatim.xsl": specification_outputs,
            "build/v3dt-schema.xsl": specification_outputs,
            "build/v3pub-locations.ent": specification_outputs,
            "build/v3m00.ent": ("ucum.html",),
            "build/largegraphics.xml": ("ucum.html",),
            "build/ucum-winnow.xsl": ("ucum-essence.xml",),
            "build/ucum-oldfile.xsl": ("ucum-cs.units", "ucum-ci.units"),
            "build/saxon8.jar": ARTIFACTS,
        }
        newer = max((self.build / name).stat().st_mtime for name in ARTIFACTS) + 2
        for dependency, expected in dependencies.items():
            with self.subTest(dependency=dependency):
                path = self.build / dependency
                original = path.stat()
                try:
                    os.utime(path, (newer, newer))
                    plan = subprocess.check_output(["make", "-n", "all"], cwd=self.build, text=True)
                    scheduled = {name for name in ARTIFACTS if "-o " + name + " " in plan}
                    self.assertEqual(scheduled, set(expected), plan)
                finally:
                    os.utime(path, ns=(original.st_atime_ns, original.st_mtime_ns))


if __name__ == "__main__":
    unittest.main()
