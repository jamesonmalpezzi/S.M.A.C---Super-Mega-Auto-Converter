# S.M.A.C - Super Mega Auto Converter
A Python-based GUI tool for transcoding video files using HandBrakeCLI.

## Features
- Converts video files (MKV, AVI, MOV, M4V, WMV) to MP4 with x265 10-bit encoding.
- User-friendly interface with a log window and sound effects.
- Version: v0.1
- Current version is for 1080p media with the following encoder options for best compression/quality balance:
> **Encoding Settings**
>
> <small>
> * --format av_mp4<br>
> * --encoder x265_10bit<br>
> * --encoder-profile main10<br>
> * --encoder-level 5.1<br>
> * --quality 24<br>
> * --cfr<br>
> * --keep-display-aspect<br>
> * --crop 0:0:0:0<br>
> * --decomb<br>
> * --aencoder eac3<br>
> * --ab 448<br>
> * --mixdown stereo<br>
> * --arate 48<br>
> * --audio-lang-list eng<br>
> * --subtitle-burned<br>
> * --no-markers
> </small>


## Requirements
- Python 3.x
- HandBrakeCLI (at C:\Program Files\HandBrake\HandBrakeCLI.exe)
- Dependencies: tkinter, PIL, pygame, rich

## Usage
- Update directory file paths for media to your personal path
- Run `transcode_gui.py` or build with `build_transcode.ps1` to create an executable.

<br>
<p align="center">
<img src="https://github.com/jamesonmalpezzi/S.M.A.C---Super-Mega-Auto-Converter/blob/main/screenshot.jpg">
</p>
