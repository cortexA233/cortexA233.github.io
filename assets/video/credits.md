# Homepage showreel sources

Updated on 2026-09-16. Both renditions use the same 40-second edit at 24 fps, with no audio stream. Twelve independent highlights are arranged in two rounds: every project's first highlight, then every project's second highlight. Each transition overlaps by 0.25 seconds (6 frames). Tiled footage is excluded.

| Rendition | File | Resolution | Size | Loading policy |
| --- | --- | --- | --- | --- |
| Desktop | `homepage-showreel-desktop.mp4` | 1920 × 1080 | 12.87 MB | Wider than 900 CSS pixels, unless a lightweight connection is reported |
| Mobile / lightweight | `homepage-showreel.mp4` | 1280 × 720 | 3.95 MB | Narrow screens, Save-Data, or reported slow-2g / 2g / 3g connections |

The browser chooses one rendition when playback first starts; resizing does not trigger a second download. The existing deferred loading, muted loop, reduced-motion preference, and manual play/pause control are retained. The poster is a new 1920 × 1080 frame from the lossless desktop master.

## LifeAfter — official NetEase footage

Both videos are linked directly from the [official LifeAfter Season 3 website](https://www.lifeafter.game/Season3/), retrieved on 2026-09-12. LifeAfter promotional footage: © NetEase, Inc.

- [Season 3 promotional trailer](https://nie.v.netease.com/nie/2020/1106/70237e76f0e38706041a792bdb673cb5.mp4): camp sequence at **00:35.500–00:38.500**. Letterbox bars are cropped before fitting the 16:9 reel.
- [Official gameplay trailer](https://crazynote.v.netease.com/2020/1026/1218f58330209897ab13b4e251334fb6.mp4): third-person camp defense at **01:25.900–01:29.650**. Both renditions now use the 1080p local excerpt (`lifeafter-official-gameplay-hd-82s-94s.mp4`), which starts at 01:22.000 of that trailer.

These excerpts illustrate the game; the author's contributions are described separately on the LifeAfter career page.

## Edit decision list

Source-file times below refer to the local editing inputs. Apart from the two official LifeAfter inputs above, footage was supplied in the repository's local `video/` directory. Input files are not included in the website asset commit.

Both rounds follow: Exp10sion → Element Ballance → Gacha Seeds → Sea of Remnants → LifeAfter → Daddy Gaiden. The second round starts at 19.750 seconds (the boundary crossfade ends at 20.000 seconds). Each project returns with a different mechanic, scene, or encounter rather than a repeated excerpt.

| Round | Highlight | Local input | Input in–out | Reel in–out (including transitions) |
| --- | --- | --- | --- | --- |
| 1 | Exp10sion — shadow / gate puzzle | `video/Exp10sion on Steam.mp4` | 00:32.000–00:35.250 | 0.000–3.250 s |
| 1 | Element Ballance — magnetic gap crossing | `video/Element_Ballance_new.mp4` | 00:52.500–00:56.250 | 3.000–6.750 s |
| 1 | Gacha Seeds — growing plants | `video/indiecade_pv.mp4` | 00:24.500–00:28.000 | 6.500–10.000 s |
| 1 | Sea of Remnants — sailing | `video/sea_of_remnants.mp4` | 07:01.750–07:05.750 | 9.750–13.750 s |
| 1 | LifeAfter — camp | `video/lifeafter-official-season3.mp4` | 00:35.500–00:38.500 | 13.500–16.500 s |
| 1 | Daddy Gaiden — crowd combat | `video/daddy_gaiden_gdc_footage.mov` | 00:39.000–00:42.750 | 16.250–20.000 s |
| 2 | Exp10sion — rotating switches | `video/Exp10sion on Steam.mp4` | 00:48.900–00:52.150 | 19.750–23.000 s |
| 2 | Element Ballance — lift platform | `video/Element_Ballance_new.mp4` | 02:04.000–02:07.750 | 22.750–26.500 s |
| 2 | Gacha Seeds — clearing harmful plants | `video/indiecade_pv.mp4` | 00:32.500–00:36.000 | 26.250–29.750 s |
| 2 | Sea of Remnants — third-person coastal traversal | `video/sea_of_remnants.mp4` | 02:16.000–02:19.500 | 29.500–33.000 s |
| 2 | LifeAfter — camp defense | `video/lifeafter-official-gameplay-hd-82s-94s.mp4` | 00:03.900–00:07.650 | 32.750–36.500 s |
| 2 | Daddy Gaiden — boss combat | `video/daddy_gaiden_gdc_footage.mov` | 01:13.500–01:17.250 | 36.250–40.000 s |

Desktop encoding: original source inputs → 1080p lossless intermediate → two-pass H.264, 2600 kb/s target video bitrate, 4500 kb/s peak limit, 9000 kb buffer, slow preset, yuv420p, 48-frame GOP, MP4 fast-start. It is not an upscale of the compressed mobile reel. Some source clips are natively 720p; those clips retain that source-detail limit.

Mobile encoding uses the same lossless edit master, downscaled to 720p: two-pass H.264, 780 kb/s target video bitrate, 1500 kb/s peak limit, 3000 kb buffer, slow preset, yuv420p, 48-frame GOP, MP4 fast-start. Neither rendition carries audio, subtitles, or source-recording metadata.

## Desktop framing

The background remains full-width, with the video centered and faded into dark side margins. The visible media box is capped at 1520 pixels and about 2.1:1. The hero is 720 pixels high at a 1920 × 1080 viewport and caps at 760 pixels on taller displays; short windows and mobile layouts scale down. Text uses a stronger left-side shade while the right side retains more image detail.

## Updating the homepage video

To reproduce both renditions, use `python scripts/render_showreel.py --ffmpeg <ffmpeg-executable> --work-dir <dedicated-temporary-directory>`. It requires the untracked original inputs in `video/`, including the 1080p official gameplay excerpt. It produces the lossless master, desktop and mobile MP4s, and poster in the specified temporary directory, without overwriting published assets. Verify the output before copying both MP4s to `assets/video/` and the poster to `assets/img/`.

Use `python scripts/render_showreel.py --print-plan` to inspect the shared edit decision list and exact source/reel timings without encoding. The regression test checks the two-round order, distinct excerpts, quarter-second transitions, 40-second duration, and exclusion of Tiled and the old Element Ballance PV.

After replacing either rendition or the poster, run `python build.py` and include the generated homepages in the commit. The builder adds independent content-hash versions to both video URLs and the poster in all three languages: changed content bypasses its previous cache, while unchanged content keeps the same URL. No manual media version bump is needed.
