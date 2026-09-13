from pathlib import Path

import pytest


ASSETS = Path(__file__).resolve().parent.parent / "assets"


@pytest.mark.parametrize("filename, budget_mib", [
    ("homepage-showreel.mp4", 4),
    ("homepage-showreel-desktop.mp4", 15),
])
def test_homepage_background_video_stays_within_transfer_budget(filename, budget_mib):
    video = ASSETS / "video" / filename

    assert video.is_file(), f"missing homepage video rendition: {filename}"
    assert video.stat().st_size <= budget_mib * 1024 * 1024, (
        f"{filename} must stay within its {budget_mib} MiB transfer budget"
    )
