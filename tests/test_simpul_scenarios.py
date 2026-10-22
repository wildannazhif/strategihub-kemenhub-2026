import json
import unittest

import pandas as pd

from scripts.generate_simpul_recommendations import (
    build_recommendations,
    replace_json_fields,
)


def departure(date, name, passengers, armada):
    return {
        "tanggal": date,
        "caturwulan": "T1",
        "moda": "BUS",
        "id_prasarana": name,
        "nama_prasarana": name,
        "provinsi": "Jawa Timur",
        "penumpang_berangkat": passengers,
        "armada_berangkat": armada,
        "penumpang_datang": 0,
        "armada_datang": 0,
    }


def calculate(rows):
    return build_recommendations(pd.DataFrame(rows))


class SimpulScenarioTests(unittest.TestCase):
    def test_data_synchronization_preserves_nested_unrelated_dashboard_data(self):
        original = {
            "chart": {"labels": ["[literal]", "};", 'escaped " quote']},
            "nested": {"simpul_recommendations": [{"retain": "nested value"}]},
            "simpul_recommendations": [{"obsolete": True}],
        }
        prefix = "<script>\nconst DATA = "
        document = prefix + json.dumps(original, indent=2) + ";\n</script>"
        updated = replace_json_fields(
            document,
            {
                "simpul_recommendations": [{"scenarioValid": False, "pctTambah": None}],
                "simpul_scenario_metadata": {"validCount": 0, "thresholds": {"p90": None}},
            },
            len(prefix),
        )
        decoded, _ = json.JSONDecoder().raw_decode(updated, len(prefix))
        self.assertEqual(decoded["chart"], original["chart"])
        self.assertEqual(decoded["nested"], original["nested"])
        self.assertEqual(
            decoded["simpul_recommendations"],
            [{"scenarioValid": False, "pctTambah": None}],
        )
        self.assertEqual(decoded["simpul_scenario_metadata"]["validCount"], 0)
        self.assertIsNone(decoded["simpul_scenario_metadata"]["thresholds"]["p90"])

    def test_no_active_peak_nodes_produces_an_empty_scenario_population(self):
        items, metadata = calculate([
            departure("2026-01-01", "Inactive", 100, 10),
            departure("2026-03-18", "Inactive", 0, 0),
        ])
        self.assertEqual(items, [])
        self.assertEqual(metadata["validCount"], 0)
        self.assertEqual(metadata["insufficientCount"], 0)
        self.assertEqual(metadata["thresholds"], {"p50": None, "p75": None, "p90": None})

    def test_peak_departures_share_passenger_peak_date_and_ceiling_is_exact(self):
        normal = departure("2026-01-01", "Aligned", 7, 10)
        items, _ = calculate([
            normal,
            normal.copy(),
            departure("2026-03-18", "Aligned", 10, 2),
            departure("2026-03-18", "Aligned", 11, 2),
            departure("2026-03-24", "Aligned", 20, 100),
        ])
        item = items[0]
        self.assertEqual(item["pnpBiasa"], 7)
        self.assertEqual(item["armBiasa"], 10)
        self.assertEqual(item["peakDate"], "2026-03-18")
        self.assertEqual(item["pnpPuncak"], 21)
        self.assertEqual(item["armPuncak"], 4)
        # 21 / (7 / 10) is exactly 30; early floating-point division can give 31.
        self.assertEqual(item["requiredArm"], 30)
        self.assertEqual(item["addArm"], 26)
        self.assertEqual(item["totalArm"], 30)
        self.assertEqual(item["pctTambah"], 650)

    def test_fractional_medians_are_not_rounded_before_scenario_calculation(self):
        items, _ = calculate([
            departure("2026-01-01", "Median", 2, 10),
            departure("2026-01-02", "Median", 5, 10),
            departure("2026-03-18", "Median", 7, 5),
        ])
        item = items[0]
        self.assertEqual(item["pnpBiasa"], 3.5)
        self.assertEqual(item["requiredArm"], 20)
        self.assertEqual(item["addArm"], 15)
        self.assertEqual(item["pctTambah"], 300)

    def test_equal_passenger_peaks_choose_earliest_day_not_maximum_armada(self):
        items, _ = calculate([
            departure("2026-01-01", "Tie", 50, 10),
            departure("2026-03-20", "Tie", 100, 10),
            departure("2026-03-18", "Tie", 100, 5),
        ])
        item = items[0]
        self.assertEqual(item["peakDate"], "2026-03-18")
        self.assertEqual(item["armPuncak"], 5)
        self.assertEqual(item["requiredArm"], 20)
        self.assertEqual(item["addArm"], 15)

    def test_no_deficit_means_zero_addition_without_reducing_current_departures(self):
        items, _ = calculate([
            departure("2026-01-01", "Enough", 300, 10),
            departure("2026-03-18", "Enough", 200, 10),
        ])
        item = items[0]
        self.assertTrue(item["scenarioValid"])
        self.assertEqual(item["requiredArm"], 7)
        self.assertEqual(item["addArm"], 0)
        self.assertEqual(item["pctTambah"], 0)
        self.assertEqual(item["totalArm"], 10)

    def test_invalid_normal_or_peak_data_remains_visible_without_fake_scenario(self):
        cases = {
            "zero_normal_passengers": [
                departure("2026-01-01", "Missing", 0, 10),
                departure("2026-03-18", "Missing", 100, 10),
            ],
            "zero_normal_armada": [
                departure("2026-01-01", "Missing", 10, 0),
                departure("2026-03-18", "Missing", 100, 10),
            ],
            "no_normal_observations": [
                departure("2026-03-18", "Missing", 100, 10),
            ],
            "no_armada_on_passenger_peak_day": [
                departure("2026-01-01", "Missing", 10, 1),
                departure("2026-03-18", "Missing", 100, 0),
                departure("2026-03-19", "Missing", 90, 10),
            ],
        }
        for case, rows in cases.items():
            with self.subTest(case=case):
                items, metadata = calculate(rows)
                self.assertEqual(len(items), 1)
                item = items[0]
                self.assertFalse(item["scenarioValid"])
                self.assertEqual(item["statusKey"], "insufficient")
                for field in ["loadRatio", "requiredArm", "addArm", "totalArm", "pctTambah"]:
                    self.assertIsNone(item[field], field)
                self.assertEqual(metadata["validCount"], 0)
                self.assertEqual(metadata["insufficientCount"], 1)
                self.assertEqual(metadata["thresholds"], {"p50": None, "p75": None, "p90": None})
                # The generated bundle must contain JSON nulls, never NaN/Infinity.
                json.dumps({"items": items, "metadata": metadata}, allow_nan=False)

    def test_percentile_groups_do_not_set_scenario_percentages(self):
        rows = []
        for ratio in range(1, 12):
            name = f"Node{ratio}"
            rows.extend([
                departure("2026-01-01", name, 100, 10),
                departure("2026-03-18", name, ratio * 100, 10),
            ])
        rows.extend([
            departure("2026-01-01", "Invalid", 0, 1),
            departure("2026-03-18", "Invalid", 50000, 1),
        ])
        items, metadata = calculate(rows)
        by_name = {item["name"]: item for item in items}
        self.assertEqual(metadata["validCount"], 11)
        self.assertEqual(metadata["insufficientCount"], 1)
        self.assertEqual(metadata["thresholds"]["p50"], 6)
        self.assertEqual(metadata["thresholds"]["p75"], 8.5)
        self.assertEqual(metadata["thresholds"]["p90"], 10)
        self.assertEqual(by_name["Node5"]["statusKey"], "controlled")
        self.assertEqual(by_name["Node6"]["statusKey"], "medium")
        self.assertEqual(by_name["Node9"]["statusKey"], "high")
        self.assertEqual(by_name["Node10"]["statusKey"], "critical")
        self.assertEqual(by_name["Node11"]["statusKey"], "critical")
        self.assertEqual(by_name["Node10"]["pctTambah"], 900)
        self.assertEqual(by_name["Node11"]["pctTambah"], 1000)
        self.assertEqual(by_name["Invalid"]["statusKey"], "insufficient")
        self.assertEqual(sum(metadata["counts"].values()), len(items))

    def test_existing_small_volume_exception_does_not_set_additional_percentage(self):
        items, _ = calculate([
            departure("2026-01-01", "Small", 5, 1),
            departure("2026-03-18", "Small", 50, 1),
            departure("2026-01-01", "Boundary", 10, 1),
            departure("2026-03-18", "Boundary", 100, 1),
        ])
        by_name = {item["name"]: item for item in items}
        self.assertEqual(by_name["Small"]["statusKey"], "controlled")
        self.assertEqual(by_name["Boundary"]["statusKey"], "critical")
        self.assertEqual(by_name["Small"]["pctTambah"], 900)
        self.assertEqual(by_name["Boundary"]["pctTambah"], 900)


if __name__ == "__main__":
    unittest.main()
