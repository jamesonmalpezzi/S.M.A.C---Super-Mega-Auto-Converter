# S.M.A.C - Super Mega Auto Converter

A Python-based GUI tool for transcoding video files using HandBrakeCLI.

<p align="center">
<img src="https://github.com/jamesonmalpezzi/S.M.A.C---Super-Mega-Auto-Converter/blob/main/screenshot.jpg">
</p>

## Features
- Converts video files (MKV, AVI, MOV, M4V, WMV) to MP4 with x265 10-bit encoding.<br>
  (.mp4 is skipped as that is the current output type to avoid re-encoded previsouly encoded files)
- User-friendly interface with a log window and sound effects.
- Version: v0.1
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
- Run `transcode_gui.py` or build with `build_transcode.ps1` to create an executable.
