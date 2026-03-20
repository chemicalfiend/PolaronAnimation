#!/bin/bash
set -e
cd "$(dirname "$0")"
rm -rf media/
manim -qm electron_phonon.py Diffusion
cd media/videos/electron_phonon/720p30
ffmpeg -y -i Diffusion.mp4 -vf "fps=15,scale=960:-1,palettegen=stats_mode=full" palette.png
ffmpeg -y -i Diffusion.mp4 -i palette.png -lavfi "fps=15,scale=960:-1[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=5" ../../../../Diffusion.gif
