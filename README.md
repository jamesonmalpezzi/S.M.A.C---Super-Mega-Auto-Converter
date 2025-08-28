# S.M.A.C - Super Mega Auto Converter

A Python-based GUI tool for transcoding video files using HandBrakeCLI.

<p align="center">
<img src="https://github.com/jamesonmalpezzi/S.M.A.C---Super-Mega-Auto-Converter/blob/main/images/screenshot.jpg">
</p>

## Features
- Converts video files (MKV, AVI, MOV, M4V, WMV) to MP4 with x265 10-bit encoding.<br>
- Deletes original file after encoding of new file is complete to save you clean-up time!
- User-friendly interface with a log window and sound effects.
- .mp4 source files are skipped, as they are the current output type, to avoid re-encoding previously encoded files.
- Current version is for 1080p media with the following encoder options for best compression/quality balance:

> **Encoding Settings**
>
> - `--format av_mp4`
> - `--encoder x265_10bit`
> - `--encoder-profile main10`
> - `--encoder-level 5.1`
> - `--quality 24`
> - `--keep-display-aspect`
> - `--decomb`
> - `--aencoder eac3`
> - `--ab 448`
> - `--mixdown stereo`
> - `--arate 48`
> - `--audio-lang-list eng`
> - `--subtitle-burned`

## Requirements
- Python 3.x
- HandBrakeCLI (at C:\Program Files\HandBrake\HandBrakeCLI.exe)
- Dependencies: tkinter, PIL, pygame, rich

## Usage
- Update directory file paths for media to your personal path
- Run `transcode_gui.py` or build with `.\build_transcode.ps1` in powershell to create an executable.

## Verison Notes
- Version: v0.5
- Suppressed Terminal Windows: Added creationflags=subprocess.CREATE_NO_WINDOW to subprocess.run calls in process_video function to prevent HandBrakeCLI from opening terminal windows during video encoding on Windows, ensuring processes run silently in the background.
- Window Height Adjustment: Reduced application window height from 700 pixels to 650 pixels (self.root.geometry("600x650")) to provide a tighter layout with balanced top and bottom padding, improving visual aesthetics.
- Progress Bar Animation: Progressbar in determinate mode that fills from 0% (left) to 100% (right) and resets in a loop for each file being encoded. The animation starts at the beginning of each file’s processing in process_video and stops when the file is done, enhancing visual feedback per file.
