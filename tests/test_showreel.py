import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent.parent


def test_showreel_plan_interleaves_distinct_highlights_in_two_rounds():
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "render_showreel.py"), "--print-plan"],
        capture_output=True, text=True, check=True,
    )
    plan = json.loads(result.stdout)
    cuts = plan["cuts"]
    project_order = ["exp10sion", "element-ballance", "gacha-seeds",
                     "sea-of-remnants", "lifeafter", "daddy-gaiden"]

    assert [cut["project"] for cut in cuts] == project_order * 2
    assert [cut["round"] for cut in cuts] == [1] * 6 + [2] * 6
    assert plan["fps"] == 24
    assert plan["duration_seconds"] == 40
    assert cuts[0]["reel_in"] == 0
    assert cuts[-1]["reel_out"] == 40
    assert 19 <= cuts[6]["reel_in"] <= 21
    for first, second in zip(cuts[:6], cuts[6:]):
        assert first["highlight"] != second["highlight"]
        if first["source"] == second["source"]:
            assert (first["source_out"] <= second["source_in"] or
                    second["source_out"] <= first["source_in"])
    for previous, current in zip(cuts, cuts[1:]):
        assert previous["project"] != current["project"]
        assert previous["reel_out"] - current["reel_in"] == 0.25
    assert not any("tiled" in cut["source"].lower() for cut in cuts)
    assert not any("Element_Ballance_pv" in cut["source"] for cut in cuts)
