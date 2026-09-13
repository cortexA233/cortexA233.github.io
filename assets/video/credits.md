# Homepage showreel sources

Updated on 2026-09-12. Both renditions use the same 40-second edit at 24 fps, with no audio stream. Each transition overlaps by 0.25 seconds (6 frames). Tiled footage is excluded.

| Rendition | File | Resolution | Size | Loading policy |
| --- | --- | --- | --- | --- |
| Desktop | `homepage-showreel-desktop.mp4` | 1920 × 1080 | 12.90 MB | Wider than 900 CSS pixels, unless a lightweight connection is reported |
| Mobile / lightweight | `homepage-showreel.mp4` | 1280 × 720 | 3.92 MB | Narrow screens, Save-Data, or reported slow-2g / 2g / 3g connections |

The browser chooses one rendition when playback first starts; resizing does not trigger a second download. The existing deferred loading, muted loop, reduced-motion preference, and manual play/pause control are retained. The poster is a new 1920 × 1080 frame from the lossless desktop master.

## LifeAfter — official NetEase footage

Both videos are linked directly from the [official LifeAfter Season 3 website](https://www.lifeafter.game/Season3/), retrieved on 2026-09-12. LifeAfter promotional footage: © NetEase, Inc.

- [Season 3 promotional trailer](https://nie.v.netease.com/nie/2020/1106/70237e76f0e38706041a792bdb673cb5.mp4): camp sequence at **00:35.500–00:38.500**. Letterbox bars are cropped before fitting the 16:9 reel.
- [Official gameplay trailer](https://crazynote.v.netease.com/2020/1026/1218f58330209897ab13b4e251334fb6.mp4): third-person camp defense at **01:25.900–01:29.650**. The local editing inputs are excerpts starting at 01:22.000 of that trailer. The desktop rendition uses a newly extracted 1080p excerpt (`lifeafter-official-gameplay-hd-82s-94s.mp4`); the retained mobile edit uses the earlier 720p excerpt.

These excerpts illustrate the game; the author's contributions are described separately on the LifeAfter career page.

## Edit decision list

Source-file times below refer to the local editing inputs. Apart from the two official LifeAfter inputs above, footage was supplied in the repository's local `video/` directory. Input files are not included in the website asset commit.

| Segment | Local input | Input in–out | Reel in–out (including transitions) |
| --- | --- | --- | --- |
| exp10sion | `video/Exp10sion on Steam.mp4` | 00:45.800–00:51.800 | 0.000–6.000 s |
| element-ballance-new | `video/Element_Ballance_new.mp4` | 00:50.250–00:56.750 | 5.750–12.250 s |
| gacha-seeds | `video/indiecade_pv.mp4` | 00:22.500–00:28.500 | 12.000–18.000 s |
| sea-sailing | `video/sea_of_remnants.mp4` | 07:01.000–07:05.500 | 17.750–22.250 s |
| sea-land | `video/sea_of_remnants.mp4` | 02:04.800–02:10.800 | 22.000–28.000 s |
| lifeafter-camp | `video/lifeafter-official-season3.mp4` | 00:35.500–00:38.500 | 27.750–30.750 s |
| lifeafter-combat | `video/lifeafter-official-gameplay-82s-94s.mp4` | 00:03.900–00:07.650 | 30.500–34.250 s |
| daddy-gaiden | `video/daddy_gaiden_gdc_footage.mov` | 00:39.000–00:45.000 | 34.000–40.000 s |

Desktop encoding: original source inputs → 1080p lossless intermediate → two-pass H.264, 2600 kb/s target video bitrate, 4500 kb/s peak limit, 9000 kb buffer, slow preset, yuv420p, 48-frame GOP, MP4 fast-start. It is not an upscale of the compressed mobile reel. Some source clips are natively 720p; those clips retain that source-detail limit.

Mobile encoding is unchanged: two-pass H.264, 780 kb/s target video bitrate, 1500 kb/s peak limit, 3000 kb buffer, slow preset, yuv420p, 48-frame GOP, MP4 fast-start. Neither rendition carries audio, subtitles, or source-recording metadata.

## Desktop framing

The background remains full-width, with the video centered and faded into dark side margins. The visible media box is capped at 1520 pixels and about 2.1:1. The hero is 720 pixels high at a 1920 × 1080 viewport and caps at 760 pixels on taller displays; short windows and mobile layouts scale down. Text uses a stronger left-side shade while the right side retains more image detail.

## Updating the homepage video

To reproduce the desktop video, use `python scripts/render_showreel.py --ffmpeg <ffmpeg-executable> --work-dir <dedicated-temporary-directory>`. It requires the untracked original inputs in `video/`, including the 1080p official gameplay excerpt. It produces the lossless master, final desktop MP4, and poster in the specified temporary directory, without overwriting published assets. Verify the output before copying the desktop MP4 to `assets/video/` and the poster to `assets/img/`.

After replacing either rendition or the poster, run `python build.py` and include the generated homepages in the commit. The builder adds independent content-hash versions to both video URLs and the poster in all three languages: changed content bypasses its previous cache, while unchanged content keeps the same URL. No manual media version bump is needed.
