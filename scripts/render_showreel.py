"""Render the approved 40-second desktop reel from original editing inputs.

Requires FFmpeg and the untracked source files documented in assets/video/credits.md.
The existing 720p mobile rendition is intentionally left untouched.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parent.parent
FPS = 24
FADE_FRAMES = 6
# Source filename, source in-point, output frames, optional source crop.
CUTS = [
    ("Exp10sion on Steam.mp4", 45.8, 144, None),
    ("Element_Ballance_new.mp4", 50.25, 156, None),
    ("indiecade_pv.mp4", 22.5, 144, None),
    ("sea_of_remnants.mp4", 421, 108, "1946:1094:0:172"),
    ("sea_of_remnants.mp4", 124.8, 144, None),
    ("lifeafter-official-season3.mp4", 35.5, 72, "1920:884:0:98"),
    ("lifeafter-official-gameplay-hd-82s-94s.mp4", 3.9, 90, None),
    ("daddy_gaiden_gdc_footage.mov", 39, 144, None),
]


def render(ffmpeg: str, work_dir: Path) -> None:
    for filename, *_ in CUTS:
        if not (ROOT / "video" / filename).is_file():
            raise FileNotFoundError(ROOT / "video" / filename)
    work_dir.mkdir(parents=True, exist_ok=True)
    common = [ffmpeg, "-hide_banner", "-loglevel", "warning", "-nostdin", "-y",
              "-stats", "-stats_period", "5"]
    inputs, filters = [], []
    for index, (filename, start, frames, crop) in enumerate(CUTS):
        inputs.extend(["-ss", str(start), "-t", str(frames / FPS + 0.15),
                       "-threads", "2", "-i", str(ROOT / "video" / filename)])
        transforms = ["setpts=PTS-STARTPTS", f"fps={FPS}:start_time=0"]
        if crop:
            transforms.append(f"crop={crop}")
        transforms.extend([
            "scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos",
            "crop=1920:1080", "setsar=1", "format=yuv420p",
            "tpad=stop_mode=clone:stop_duration=0.25", f"trim=end_frame={frames}",
            f"settb=1/{FPS}", "setpts=N",
        ])
        filters.append(f"[{index}:v]" + ",".join(transforms) + f"[clip{index}]")

    total_frames = CUTS[0][2]
    previous = "clip0"
    for index, (_, _, frames, _) in enumerate(CUTS[1:], 1):
        offset = (total_frames - FADE_FRAMES) / FPS
        current = f"mix{index}"
        filters.append(
            f"[{previous}][clip{index}]xfade=transition=fade:"
            f"duration={FADE_FRAMES / FPS}:offset={offset}[{current}]"
        )
        previous = current
        total_frames += frames - FADE_FRAMES
    assert total_frames == 960
    master = work_dir / "showreel-1080p-lossless.mkv"
    subprocess.run(common + ["-filter_complex_threads", "2"] + inputs + [
        "-filter_complex", ";".join(filters), "-map", f"[{previous}]", "-an",
        "-frames:v", str(total_frames), "-c:v", "ffv1", "-level", "3",
        "-pix_fmt", "yuv420p", "-threads", "4", str(master),
    ], check=True)

    output = work_dir / "homepage-showreel-desktop.mp4"
    for pass_number in (1, 2):
        destination = ["-f", "null", os.devnull] if pass_number == 1 else [
            "-movflags", "+faststart", str(output)
        ]
        subprocess.run(common + ["-i", str(master), "-map", "0:v:0", "-an",
            "-map_metadata", "-1", "-c:v", "libx264", "-preset", "slow",
            "-profile:v", "high", "-level:v", "4.0", "-pix_fmt", "yuv420p",
            "-b:v", "2600k", "-maxrate", "4500k", "-bufsize", "9000k",
            "-g", "48", "-threads", "4", "-pass", str(pass_number),
            "-passlogfile", str(work_dir / "desktop-pass"),
        ] + destination, check=True)
    if output.stat().st_size > 15 * 1024 * 1024:
        raise ValueError("Desktop encode exceeded the 15 MiB transfer budget")

    subprocess.run(common + ["-ss", "0.75", "-i", str(master), "-frames:v", "1",
        "-q:v", "3", "-update", "1", str(work_dir / "homepage-showreel-poster.jpg"),
    ], check=True)
    print(f"Rendered desktop video and poster in {work_dir}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ffmpeg", default="ffmpeg")
    parser.add_argument("--work-dir", type=Path, required=True,
                        help="Dedicated directory for the lossless master and encodes")
    options = parser.parse_args()
    render(options.ffmpeg, options.work_dir.resolve())
