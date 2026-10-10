"""Regression checks for the declared code systems in legacy unit exports."""

from pathlib import Path
import re
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
NAMESPACE = "{http://aurora.regenstrief.org/UCUM}"


def definitions(text):
    for line in text.splitlines():
        if " = " not in line:
            continue
        code, remainder = line.split(" = ", 1)
        definition = re.split(r" (?:nonmetric|metric)\s", remainder, maxsplit=1)[0]
        yield code, definition.strip()


class LegacyExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.exports = {}
        with tempfile.TemporaryDirectory() as directory:
            for mode in ("sensitive", "insensitive"):
                output = Path(directory) / (mode + ".units")
                subprocess.run(
                    ["java", "-jar", str(ROOT / "build/saxon8.jar"), "-o", str(output),
                     str(ROOT / "ucum-source.xml"), str(ROOT / "build/ucum-oldfile.xsl"),
                     "case=" + mode],
                    check=True, capture_output=True, text=True,
                )
                cls.exports[mode] = output.read_bytes()

    def test_mho_refers_to_conductance(self):
        insensitive = dict(definitions(self.exports["insensitive"].decode()))
        # S is seconds in this code system; SIE denotes siemens.
        self.assertEqual(insensitive["MHO"], "1 SIE")

    def test_year_refers_to_julian_year(self):
        insensitive = dict(definitions(self.exports["insensitive"].decode()))
        self.assertEqual(insensitive["ANN"], "1 ANN_J")

    def test_ordinary_references_resolve_in_each_code_system(self):
        source = ET.parse(ROOT / "ucum-source.xml").getroot()
        atoms = source.findall(".//" + NAMESPACE + "base-unit") + source.findall(".//" + NAMESPACE + "unit")
        prefixes = source.findall(".//" + NAMESPACE + "prefix")
        for mode, attribute in (("sensitive", "Code"), ("insensitive", "CODE")):
            normalize = str.upper if mode == "insensitive" else str
            candidates = {normalize(atom.get(attribute)) for atom in atoms}
            for atom in atoms:
                if atom.tag == NAMESPACE + "base-unit" or atom.get("isMetric") == "yes":
                    candidates.update(normalize(prefix.get(attribute) + atom.get(attribute)) for prefix in prefixes)
            special = {normalize(atom.get(attribute)) for atom in atoms
                       if atom.find("value/function") is not None}
            for code, definition in definitions(self.exports[mode].decode()):
                if normalize(code) in special:
                    continue
                # The legacy format separates the scalar from the unit expression.
                expression = normalize(definition.split(maxsplit=1)[1])
                for token in re.findall(r"(?:\[[^\]]*\]|\{[^}]*\}|[^./()])+", expression):
                    token = re.sub(r"\{[^}]*\}", "", token)
                    if not token or token.isdigit():
                        continue
                    with self.subTest(mode=mode, code=code, token=token):
                        self.assertTrue(any(
                            token.startswith(candidate) and
                            (token == candidate or re.fullmatch(r"[+-]?\d+", token[len(candidate):]))
                            for candidate in candidates
                        ), f"Unresolved reference in {definition}")

    def test_sensitive_export_is_unchanged(self):
        self.assertEqual(self.exports["sensitive"], (ROOT / "ucum-cs.units").read_bytes())

    def test_insensitive_definitions_retain_unit_references(self):
        """Translate atom identities, catching references to valid but wrong units."""
        source = ET.parse(ROOT / "ucum-source.xml").getroot()
        atoms = source.findall(".//" + NAMESPACE + "base-unit") + source.findall(".//" + NAMESPACE + "unit")
        prefixes = source.findall(".//" + NAMESPACE + "prefix")
        translations = {atom.get("Code"): atom.get("CODE") for atom in atoms}
        for atom in atoms:
            if atom.tag == NAMESPACE + "base-unit" or atom.get("isMetric") == "yes":
                for prefix in prefixes:
                    translations.setdefault(prefix.get("Code") + atom.get("Code"),
                                            prefix.get("CODE") + atom.get("CODE"))
        candidates = sorted(translations, key=len, reverse=True)

        def translate(match):
            token = match.group()
            if token.startswith("{") or token.isdigit():
                return token
            for candidate in candidates:
                exponent = token[len(candidate):]
                if token.startswith(candidate) and (not exponent or re.fullmatch(r"[+-]?\d+", exponent)):
                    return translations[candidate] + exponent
            raise AssertionError(f"Unrecognized case-sensitive reference: {token}")

        exports = dict(definitions(self.exports["insensitive"].decode()))
        for atom in source.findall(".//" + NAMESPACE + "unit"):
            value = atom.find("value")
            if value.find("function") is not None:
                continue
            expression = value.get("Unit")
            expected = re.sub(r"\{[^}]*\}|(?:\[[^\]]*\]|[^./(){}])+", translate, expression)
            actual = exports[atom.get("CODE")].split(maxsplit=1)[1]
            # Duplicate case-insensitive aliases have the same atom identity,
            # but can refer to the other spelling instead of its definition.
            if sum(other.get("CODE") == atom.get("CODE") for other in atoms) > 1:
                continue
            with self.subTest(code=atom.get("CODE")):
                self.assertEqual(actual.upper(), expected.upper())


if __name__ == "__main__":
    unittest.main()
