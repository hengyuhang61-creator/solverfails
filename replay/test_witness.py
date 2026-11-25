import json
import math
import unittest

import witness as w

class ReplayTests(unittest.TestCase):
    def test_observed_limits(self):
        old, repaired = list(w.grid_rows(1e-6))[:2]
        self.assertEqual((old["baseline"], old["revised"], old["truth"]), ("PASS","FAIL","FAIL"))
        self.assertTrue(math.isclose(repaired["candidate"],w.OBS["repair_limit"],abs_tol=1e-14))
        self.assertEqual((repaired["revised"],repaired["truth"]), ("PASS","PASS"))

    def test_alias_and_abstention_are_preserved(self):
        rows={r["name"]:r for r in w.grid_rows(1e-6)}
        self.assertEqual(rows["trapezoid/cosine=1/fine"]["revised"],"PASS")
        self.assertEqual(rows["trapezoid/cosine=1/fine"]["truth"],"FAIL")
        self.assertEqual(rows["missing fourth level"]["revised"],"UNKNOWN")

    def test_survey_scope(self):
        rows={r["name"]:r for r in w.survey_rows()}
        self.assertEqual(rows["eval/results-4b.json"]["revised"],"FAIL")
        self.assertEqual(rows["scope-preserving repair"]["revised"],"PASS")
        self.assertEqual(rows["target left implicit"]["revised"],"UNKNOWN")
        self.assertEqual(rows["n=7/k=2/missing=0/exact"]["revised"],"PASS")

    def test_skill_matches_enumerated_population_counts(self):
        from survey_bounds import evaluate
        from fractions import Fraction
        for n in (4, 7):
            for affected in range(n+1):
                for missing in (0, 1, 3):
                    total = n + missing
                    actual = [Fraction(k,total) for k in range(affected,affected+missing+1)]
                    for low,high in [(0,1), (Fraction(1,2),Fraction(1,2)), (0,Fraction(1,3))]:
                        matches = [low <= value <= high for value in actual]
                        expected = "ENTAILED" if all(matches) else "UNDERDETERMINED" if any(matches) else "CONTRADICTED"
                        self.assertEqual(evaluate(affected,n,total,(low,high))["status"],expected)

    def test_download_matches_classifications(self):
        downloaded=json.loads((w.HERE.parent/"site/witness-results.json").read_text(encoding="utf8"))
        computed=w.report()
        # Some libm implementations straddle an exact order boundary. Compare the
        # frozen download internally, and verify the decisive observed labels live.
        self.assertEqual(w.summarize(downloaded["rows"]),downloaded["summary"])
        observed=lambda data:[(r["name"],r["truth"],r["baseline"],r["revised"]) for r in data["rows"] if r["split"]=="observed"]
        self.assertEqual(observed(downloaded),observed(computed))

if __name__=="__main__":
    unittest.main()
