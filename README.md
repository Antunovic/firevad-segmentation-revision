# Fire-VAD Segmentation Revision

A desktop tool for a third annotator to review segmentation disagreements in
the Fire-VAD dataset (RGB and thermal/IR). Antonio’s and Mislav’s original
segmentations are bundled and read locally. The videos are not included.

## Start

Clone or download and extract this repository. Download and extract the full
`Antunovic_VAD_rgb_ir_dataset` separately.

Needs Python 3.9+ with **Tk 8.6+**. The launchers pick a suitable Python, install
`numpy` and `pillow` into a private `.venv-segmenter` folder (first run only) and start the tool:

Run these commands from the extracted repository folder:

| System | Command |
|---|---|
| Windows (PowerShell or Command Prompt) | `.\run_windows.bat` |
| Linux | `bash run_linux.sh` |
| macOS | `bash run_mac.command` |

You can also double-click `run_windows.bat` on Windows or `run_mac.command`
on macOS.

Or by hand:

```bash
pip install -r requirements.txt
python segment_gui.py
```

The tool searches for the dataset near the app and asks you to select it if
not found. Select the extracted folder containing `environment_1` through
`environment_6`. If it finds a smaller test dataset, switch to the full dataset
with **Change dataset folder…**. You can also pass `--dataset-root "/path/to/dataset"`
to any launcher.

Supported IR layouts: `IR_delta.npz` (the Antunovic dataset, lossless frame-difference
archive), `IR.npz` and a legacy `IR/` folder of `.npy` files. A scene is decoded once when
you open it (a progress bar is shown, a few seconds for the largest scenes) and then kept in
memory: about 0.4 GB for a typical scene, up to about 1.6 GB for the longest (3298 frames).
The per-frame labels (`annotations.csv`) are never read.

## First start

You are asked for your **full name**. It identifies your files, so always type it the same way.
**Change annotator…** changes it later; **Change dataset folder…** changes the folder with the videos.

Your work is saved next to the tool, separately from the original annotations:

```
annotator_config.json                              saved name and videos location
annotations/<your_name>/environment_<X>/<Y>.json   one file per video
reference_annotations/                            read-only input to the app
```

Each file holds `video_id`, `environment`, `annotator_id` and the list of segments with
`segment_id`, `start_frame`, `end_frame`, `temp_min_c` and `temp_max_c`
(the IR temperature range of the segment, filled in automatically).
The videos and original annotations are never modified.

## Reviewing scenes

All 183 scenes are listed when using the full dataset. The 23 red scenes are
the ones to review. A scene is red if a pair of boundaries differs by **more
than 10 frames**, the number of segments differs, or the video frame counts
do not agree. An offset of exactly 10 frames is accepted. Red indicates a
disagreement in the originals, so it stays red after saving; **Your progress**
shows which scenes you have saved.

1. Select a scene and press **Open scene**. Three synchronized panels open:
   **RGB**, **IR – relative** (contrast stretched per frame) and
   **IR – absolute** (fixed temperature scale: type the range or press **Video range**).
   Hovering over an IR panel shows the exact temperature in °C.
   **Show Antonio and Mislav’s segments** is unchecked each time a scene
   opens. Check it to show Antonio’s blue track and Mislav’s orange track
   under your timeline. Click either track to seek, or click a boundary to
   jump exactly to its start. Showing or hiding the tracks does not change
   your revision.
2. Pause at the frame where a new segment starts and press **B**. A new segment
   starts when something appears or disappears, or when a person changes their action.
   Segments are consecutive and cover the whole video. A video in which nothing
   changes is one segment.
   A segment of **40 frames or fewer** is almost certainly a mistake: it is marked in red
   in the list and on the timeline, a warning asks you to delete one of its boundaries,
   and saving asks for confirmation.
3. Select a segment in the list to jump to its start. **Move start ◀ -1 / +1 ▶**
   shifts its start by one frame; **Remove start boundary** merges it into the previous segment.
4. Save with **Ctrl+S** (macOS: **Cmd+S**). You can stop at any time and continue later.
5. When you are done, click **Export all my annotations**. It writes
   `combined_export.json` into your annotation folder.

| Key | Action |
|---|---|
| Space | play / pause |
| ← / → | one frame back / forward |
| ↑ / ↓ | 10 frames back / forward |
| Home / End | first / last frame |
| B | a new segment starts at the current frame |
| Delete | remove the start boundary of the selected segment |
| F1 | help |

## Checks (developers)

```bash
python -m unittest test_reference_segments
python segment_gui.py --selftest --dataset-root /path/to/Antunovic_VAD_rgb_ir_dataset
python segment_gui.py --guitest --dataset-root /path/to/Antunovic_VAD_rgb_ir_dataset
```
