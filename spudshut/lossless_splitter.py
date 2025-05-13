#!/usr/bin/env python3
"""
chunk_audio.py – split an audio file into fixed‑length chunks (default 4 min).

Why a new version?
------------------
Some users reported "it runs but nothing happens."  This edition adds:
• **Verbose mode** (`-v / --verbose`) to show the exact FFmpeg command and its
  console output.
• Clear fatal‑error messages if FFmpeg fails or no chunks are produced.
• Auto‑creates the output directory next to the input file if `--outdir` isn't
  given.
• Prints a per‑chunk summary so you immediately see work being done.

Dependencies
------------
* Python ≥ 3.8
* [FFmpeg](https://ffmpeg.org) on your PATH

Usage examples
--------------
```bash
python chunk_audio.py recording.m4a               # 4‑minute chunks into ./recording_chunks/
python chunk_audio.py recording.m4a -c 90 -v      # 90‑second chunks, verbose
python chunk_audio.py rec.m4a -o ./out -c 240     # explicit output dir
```
Exit status ≠0 means something went wrong.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from datetime import timedelta
from pathlib import Path
from typing import List, NoReturn

from .utils import fatal, check_ffmpeg, CHUNK_DEFAULT_SECS  # Import from utils


def build_ffmpeg_cmd(
    infile: Path, out_template: Path, chunk: int, verbose: bool
) -> List[str]:
    """Return the FFmpeg *segment* command as a list."""
    return [
        "ffmpeg",
        "-hide_banner",  # always
        *([] if verbose else ["-loglevel", "error"]),  # quiet unless verbose requested
        "-i",
        str(infile),
        "-f",
        "segment",
        "-segment_time",
        str(chunk),
        "-reset_timestamps",
        "1",  # important for MP4/M4A splitting
        "-c",
        "copy",  # lossless & fast
        str(out_template),
    ]


def split_audio(infile: Path, outdir: Path, chunk: int, verbose: bool) -> None:
    if not infile.is_file():
        fatal(f"Input file not found: {infile}")

    outdir.mkdir(parents=True, exist_ok=True)
    template = outdir / f"{infile.stem}_%03d{infile.suffix}"

    cmd = build_ffmpeg_cmd(infile, template, chunk, verbose)
    if verbose:
        print("[ffmpeg]", " ".join(cmd))

    try:
        # Capture output and check for errors
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        # Construct a detailed error message including stderr if available
        error_message = f"FFmpeg command failed (exit code {exc.returncode})."
        error_message += f"\nCommand: {' '.join(exc.cmd)}"
        if exc.stderr:
            error_message += f"\nFFmpeg stderr:\n{exc.stderr.strip()}"
        else:
            error_message += "\nFFmpeg stderr: (No output captured or empty)."
        error_message += (
            "\nTip: Rerun with -v for full FFmpeg log output during execution."
        )
        fatal(error_message)
    except FileNotFoundError:
        # Handle case where ffmpeg command itself is not found
        fatal(
            f"FFmpeg command not found. Ensure FFmpeg is installed and in your PATH. Command: {' '.join(cmd)}"
        )

    # Count produced chunks
    chunks = sorted(outdir.glob(f"{infile.stem}_*{infile.suffix}"))
    if not chunks:
        fatal(
            "No chunks were created – FFmpeg produced no output. Check the codec/format."
        )

    total = timedelta(seconds=len(chunks) * chunk)
    for i, p in enumerate(chunks, 1):
        print(f"  • {p.name}")
    print(f"✅ {len(chunks)} chunk(s) written → {outdir.resolve()} (≈{total})")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Split an M4A (or other FFmpeg‑supported) file into fixed‑length chunks.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("input", type=Path, help="Path to the input file")
    parser.add_argument(
        "-c",
        "--chunk",
        type=int,
        default=CHUNK_DEFAULT_SECS,
        metavar="SECONDS",
        help="Length of each chunk in seconds",
    )
    parser.add_argument(
        "-o",
        "--outdir",
        type=Path,
        help="Directory to save chunks (default: <input>_chunks)",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Show FFmpeg output"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    check_ffmpeg()

    # Default output dir: sibling folder named <stem>_chunks/
    outdir = args.outdir or args.input.with_suffix("").with_name(
        f"{args.input.stem}_chunks"
    )

    split_audio(args.input, outdir, args.chunk, args.verbose)


if __name__ == "__main__":
    main()
