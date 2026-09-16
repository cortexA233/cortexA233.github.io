"""Render both 40-second showreel renditions from one interleaved edit.

Requires FFmpeg and the untracked source files documented in assets/video/credits.md.
Use --print-plan to inspect shot order and source/reel timings without encoding.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parent.parent
FPS = 24
FADE_FRAMES = 6

@dataclass(frozen=True)
class Shot:
    project: str
    highlight: str
    source: str
    start: float
    frames: int
    crop: str | None = None


# Two rounds: every project's first highlight, then every second highlight.
CUTS = [
    Shot("exp10sion", "shadow-gates", "Exp10sion on Steam.mp4", 32, 78),
    Shot("element-ballance", "magnetic-gap", "Element_Ballance_new.mp4", 52.5, 90),
    Shot("gacha-seeds", "grow-plants", "indiecade_pv.mp4", 24.5, 84),
    Shot("sea-of-remnants", "sailing", "sea_of_remnants.mp4", 421.75, 96, "1946:1094:0:172"),
    Shot("lifeafter", "camp", "lifeafter-official-season3.mp4", 35.5, 72, "1920:884:0:98"),
    Shot("daddy-gaiden", "crowd-combat", "daddy_gaiden_gdc_footage.mov", 39, 90),
    Shot("exp10sion", "rotating-switches", "Exp10sion on Steam.mp4", 48.9, 78),
    Shot("element-ballance", "lift-platform", "Element_Ballance_new.mp4", 124, 90),
    Shot("gacha-seeds", "clear-plants", "indiecade_pv.mp4", 32.5, 84),
    Shot("sea-of-remnants", "coastal-traversal", "sea_of_remnants.mp4", 136, 84),
    Shot("lifeafter", "camp-defense", "lifeafter-official-gameplay-hd-82s-94s.mp4", 3.9, 90),
    Shot("daddy-gaiden", "boss-combat", "daddy_gaiden_gdc_footage.mov", 73.5, 90),
]


def edit_plan() -> dict:
    cuts, appearances = [], {}
    start_frame = 0
    for shot in CUTS:
        appearances[shot.project] = appearances.get(shot.project, 0) + 1
        end_frame = start_frame + shot.frames
        cuts.append({
            "project": shot.project, "highlight": shot.highlight,
            "round": appearances[shot.project], "source": shot.source,
            "source_in": shot.start, "source_out": round(shot.start + shot.frames / FPS, 3),
            "frames": shot.frames, "crop": shot.crop,
            "reel_in": start_frame / FPS, "reel_out": end_frame / FPS,
        })
        start_frame = end_frame - FADE_FRAMES
    return {"fps": FPS, "duration_seconds": cuts[-1]["reel_out"], "cuts": cuts}


def render(ffmpeg: str, work_dir: Path) -> None:
    for shot in CUTS:
        if not (ROOT / "video" / shot.source).is_file():
            raise FileNotFoundError(ROOT / "video" / shot.source)
    work_dir.mkdir(parents=True, exist_ok=True)
    common = [ffmpeg, "-hide_banner", "-loglevel", "warning", "-nostdin", "-y",
              "-stats", "-stats_period", "5"]
    inputs, filters = [], []
    for index, shot in enumerate(CUTS):
        inputs.extend(["-ss", str(shot.start), "-t", str(shot.frames / FPS + 0.15),
                       "-threads", "2", "-i", str(ROOT / "video" / shot.source)])
        transforms = ["setpts=PTS-STARTPTS", f"fps={FPS}:start_time=0"]
        if shot.crop:
            transforms.append(f"crop={shot.crop}")
        transforms.extend([
            "scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos",
            "crop=1920:1080", "setsar=1", "format=yuv420p",
            "tpad=stop_mode=clone:stop_duration=0.25", f"trim=end_frame={shot.frames}",
            f"settb=1/{FPS}", "setpts=N",
        ])
        filters.append(f"[{index}:v]" + ",".join(transforms) + f"[clip{index}]")

    total_frames = CUTS[0].frames
    previous = "clip0"
    for index, shot in enumerate(CUTS[1:], 1):
        offset = (total_frames - FADE_FRAMES) / FPS
        current = f"mix{index}"
        filters.append(
            f"[{previous}][clip{index}]xfade=transition=fade:"
            f"duration={FADE_FRAMES / FPS}:offset={offset}[{current}]"
        )
        previous = current
        total_frames += shot.frames - FADE_FRAMES
    assert total_frames == 960
    master = work_dir / "showreel-1080p-lossless.mkv"
    subprocess.run(common + ["-filter_complex_threads", "2"] + inputs + [
        "-filter_complex", ";".join(filters), "-map", f"[{previous}]", "-an",
        "-frames:v", str(total_frames), "-c:v", "ffv1", "-level", "3",
        "-pix_fmt", "yuv420p", "-threads", "4", str(master),
    ], check=True)

    for filename, size, level, rate, peak, buffer, budget_mib in [
        ("homepage-showreel-desktop.mp4", "1920:1080", "4.0", "2600k", "4500k", "9000k", 15),
        ("homepage-showreel.mp4", "1280:720", "3.1", "780k", "1500k", "3000k", 4),
    ]:
        output = work_dir / filename
        for pass_number in (1, 2):
            destination = ["-f", "null", os.devnull] if pass_number == 1 else [
                "-movflags", "+faststart", str(output)
            ]
            subprocess.run(common + ["-i", str(master), "-map", "0:v:0", "-an",
                "-map_metadata", "-1", "-vf", f"scale={size}:flags=lanczos",
                "-c:v", "libx264", "-preset", "slow",
                "-profile:v", "high", "-level:v", level, "-pix_fmt", "yuv420p",
                "-b:v", rate, "-maxrate", peak, "-bufsize", buffer,
                "-g", "48", "-threads", "4", "-pass", str(pass_number),
                "-passlogfile", str(work_dir / (output.stem + "-pass")),
            ] + destination, check=True)
        if output.stat().st_size > budget_mib * 1024 * 1024:
            raise ValueError(f"{filename} exceeded the {budget_mib} MiB transfer budget")

    subprocess.run(common + ["-ss", "0.75", "-i", str(master), "-frames:v", "1",
        "-q:v", "3", "-update", "1", str(work_dir / "homepage-showreel-poster.jpg"),
    ], check=True)
    print(f"Rendered desktop/mobile videos and poster in {work_dir}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ffmpeg", default="ffmpeg")
    parser.add_argument("--print-plan", action="store_true",
                        help="Print the edit decision list as JSON without rendering")
    parser.add_argument("--work-dir", type=Path,
                        help="Dedicated directory for the lossless master and encodes")
    options = parser.parse_args()
    if options.print_plan:
        print(json.dumps(edit_plan(), indent=2))
    elif options.work_dir is None:
        parser.error("--work-dir is required when rendering")
    else:
        render(options.ffmpeg, options.work_dir.resolve())
