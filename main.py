"""Entry point: draw the 25 November 2026 front page to /output/entry.png.

Deterministic by construction: render.py uses fixed fonts, geometry and
colours, reads only stories.json, and takes no clock, random or network
input, so two runs write byte-identical PNGs.
"""
import os

from render import main

if __name__ == "__main__":
    main()
