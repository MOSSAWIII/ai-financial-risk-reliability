"""Contrôles négatifs G3A indépendants des deux fichiers de marché privés."""
import math
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from g3_learning_value import (
    START, INITIAL_END, EVAL_START, EVAL_END, TERMINAL, COST,
    FIELDS, csv_write, estimate, samples, simulate, verify_inputs, sha256
)
from sequentiality_test import default_model, solve_dynamic_program


def fixture():
    """Clôtures hebdomadaires synthétiques, jamais des cours observés."""
    d = date(2007, 5, 28)
    spy, bil, index = 100., 100., 0
    rows = []
    while d <= EVAL_END:
        day = START if index == 0 else INITIAL_END if d == date(2024, 5, 27) else d
        spy *= math.exp(.018 if (index // 4) % 2 == 0 else -.012)
        bil *= math.exp(.0002)
        rows.append((day, spy, bil))
        d += timedelta(days=7)
        index += 1
    rows.append((TERMINAL, spy*math.exp(.01), bil*math.exp(.0001)))
    return rows


class G3Tests(unittest.TestCase):
    def test_prespecified_calendar_and_strict_training_cutoff(self):
        weekly = fixture()
        self.assertTrue({START, INITIAL_END, EVAL_START, EVAL_END, TERMINAL}
                        <= {row[0] for row in weekly})
        _, params = estimate(weekly, samples(weekly), EVAL_START)
        self.assertLess(date.fromisoformat(params["latest_training_outcome"]),
                        EVAL_START)

    def test_frozen_solver_unchanged(self):
        expected = solve_dynamic_program(default_model(horizon=12), COST)
        reproduced = solve_dynamic_program(default_model(horizon=12), COST)
        self.assertEqual(expected.actions, reproduced.actions)
        self.assertEqual(1.0, reproduced.actions[(0, "RISK_ON", 0.5)])
        self.assertEqual(0.0, reproduced.actions[(0, "RISK_OFF", 0.5)])

    def test_future_terminal_shock_does_not_change_any_past_action(self):
        first = simulate(fixture())
        future = fixture()
        terminal, spy, bil = future[-1]
        future[-1] = (terminal, spy*1.8, bil)
        second = simulate(future)
        for a, b in zip(first["policy_decisions.csv"],
                        second["policy_decisions.csv"]):
            self.assertEqual((a["date"], a["policy"], a["target_weight"]),
                             (b["date"], b["policy"], b["target_weight"]))

    def test_interior_future_shock_cannot_rewrite_past_decisions(self):
        before = simulate(fixture())
        altered = fixture()
        affected = date(2025, 9, 1)
        self.assertIn(affected, {r[0] for r in altered})
        altered = [(day, spy*1.25 if day == affected else spy, bil)
                   for day, spy, bil in altered]
        after = simulate(altered)
        left = [(r["date"], r["policy"], r["target_weight"])
                for r in before["policy_decisions.csv"]
                if date.fromisoformat(r["date"]) < affected]
        right = [(r["date"], r["policy"], r["target_weight"])
                 for r in after["policy_decisions.csv"]
                 if date.fromisoformat(r["date"]) < affected]
        self.assertEqual(left, right)

    def test_warmup_and_matched_policy_calendars(self):
        rows = simulate(fixture())["policy_decisions.csv"]
        self.assertEqual({.5}, {row["target_weight"] for row in rows[:12]})
        self.assertEqual(0, len(rows) % 3)
        for i in range(0, len(rows), 3):
            group = rows[i:i+3]
            self.assertEqual(1, len({r["date"] for r in group}))
            self.assertEqual(1, len({r["next_close"] for r in group}))
            self.assertEqual(1, len({r["log_return_spy"] for r in group}))
            self.assertEqual(1, len({r["log_return_bil"] for r in group}))

    def test_byte_reproducibility(self):
        result = simulate(fixture())
        with TemporaryDirectory() as left, TemporaryDirectory() as right:
            for filename, columns in FIELDS.items():
                csv_write(Path(left)/filename, columns, result[filename])
                csv_write(Path(right)/filename, columns, result[filename])
                self.assertEqual(sha256(Path(left)/filename),
                                 sha256(Path(right)/filename))

    def test_documentary_block_on_missing_sources(self):
        with TemporaryDirectory() as folder:
            self.assertEqual("DOCUMENTARY_BLOCK",
                             verify_inputs(Path(folder))["verdict"])


if __name__ == "__main__":
    unittest.main()
