"""Check angle-function metadata against the specification's documented formula.

This small reference calculation exercises the definition metadata; it is not a
UCUM parser or a test of an external converter implementation.
"""

import math
from pathlib import Path
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]


class SpecialAngleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tables = {"source": ET.parse(ROOT / "ucum-source.xml").getroot()}
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "ucum-essence.xml"
            subprocess.run(
                ["java", "-jar", str(ROOT / "build/saxon8.jar"), "-o", str(output),
                 str(ROOT / "ucum-source.xml"), str(ROOT / "build/ucum-winnow.xsl")],
                check=True, capture_output=True, text=True,
            )
            cls.essence = output.read_bytes()
            cls.tables["rebuilt essence"] = ET.fromstring(cls.essence)

    def parameters(self, table, code):
        unit = next(unit for unit in table.iter() if unit.get("Code") == code)
        value = unit.find("{*}value")
        function = value.find("{*}function")
        # The documented function is f(angle) = 100 * tan(angle).
        self.assertEqual(function.get("name"), "100tan")
        self.assertIn(function.get("Unit"), ("rad", "deg"))
        angle_scale = {"rad": 1, "deg": math.pi / 180}[function.get("Unit")]
        return float(function.get("value")), angle_scale

    def test_special_values_to_radians(self):
        # A rise equal to the horizontal run is a 45-degree angle.
        for label, table in self.tables.items():
            for code in ("%[slope]", "[p'diop]"):
                for special, expected in ((100, math.pi / 4), (-100, -math.pi / 4), (0, 0)):
                    with self.subTest(table=label, code=code, special=special):
                        factor, scale = self.parameters(table, code)
                        radians = math.atan(special * factor / 100) * scale
                        self.assertAlmostEqual(radians, expected, delta=1e-12)

    def test_radians_to_special_values(self):
        for label, table in self.tables.items():
            for code in ("%[slope]", "[p'diop]"):
                for radians, expected in ((math.pi / 4, 100), (-math.pi / 4, -100), (0, 0)):
                    with self.subTest(table=label, code=code, radians=radians):
                        factor, scale = self.parameters(table, code)
                        special = 100 * math.tan(radians / scale) / factor
                        self.assertAlmostEqual(special, expected, delta=1e-12)

    def test_committed_essence_matches_rebuild(self):
        self.assertEqual(self.essence, (ROOT / "ucum-essence.xml").read_bytes())


if __name__ == "__main__":
    unittest.main()
