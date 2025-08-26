# S.M.A.C - Super Mega Auto Converter
A Python-based GUI tool for transcoding video files using HandBrakeCLI.

## Features
- Converts video files (MKV, AVI, MOV, M4V, WMV) to MP4 with x265 10-bit encoding.
- User-friendly interface with a log window and sound effects.
- Version: v0.1
- Current version is for 1080p media with the following encoder options for best compression/quality balance:
> ### Encoding Settings
> <small>
> &nbsp;&nbsp;• --format av_mp4  
> &nbsp;&nbsp;• --encoder x265_10bit  
> &nbsp;&nbsp;• --encoder-profile main10  
> &nbsp;&nbsp;• --encoder-level 5.1  
> &nbsp;&nbsp;• --quality 24  
> &nbsp;&nbsp;• --cfr  
> &nbsp;&nbsp;• --keep-display-aspect  
> &nbsp;&nbsp;• --crop 0:0:0:0  
> &nbsp;&nbsp;• --decomb  
> &nbsp;&nbsp;• --aencoder eac3  
> &nbsp;&nbsp;• --ab 448  
> &nbsp;&nbsp;• --mixdown stereo  
> &nbsp;&nbsp;• --arate 48  
> &nbsp;&nbsp;• --audio-lang-list eng  
> &nbsp;&nbsp;• --subtitle-burned  
> &nbsp;&nbsp;• --no-markers  
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
