"""Check definition order for sequential consumers, not normative conformance."""

from pathlib import Path
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
DEPENDENCIES = {
    "Code": (("gon", "deg"), ("eV", "[e]"), ("[lbf_av]", "[lb_av]")),
    "CODE": (("GON", "DEG"), ("EV", "[E]"), ("[LBF_AV]", "[LB_AV]")),
}


class DefinitionOrderTests(unittest.TestCase):
    def assert_dependencies_precede_units(self, codes, attribute):
        for unit, dependency in DEPENDENCIES[attribute]:
            with self.subTest(unit=unit, dependency=dependency):
                self.assertEqual(codes.count(unit), 1)
                self.assertEqual(codes.count(dependency), 1)
                self.assertLess(codes.index(dependency), codes.index(unit))

    def test_source_and_essence_definition_order(self):
        for name in ("ucum-source.xml", "ucum-essence.xml"):
            table = ET.parse(ROOT / name).getroot()
            units = [element for element in table.iter()
                     if element.tag.rsplit("}", 1)[-1] == "unit"]
            for attribute in DEPENDENCIES:
                with self.subTest(artifact=name, attribute=attribute):
                    self.assert_dependencies_precede_units(
                        [unit.get(attribute) for unit in units], attribute)

    def test_legacy_export_definition_order(self):
        for name, attribute in (("ucum-cs.units", "Code"), ("ucum-ci.units", "CODE")):
            codes = [line.split(" = ", 1)[0]
                     for line in (ROOT / name).read_text().splitlines() if " = " in line]
            with self.subTest(artifact=name):
                self.assert_dependencies_precede_units(codes, attribute)


if __name__ == "__main__":
    unittest.main()
