#!/usr/bin/env python3
"""
chunk_audio.py — split an audio file into fixed‑length chunks *or* join those chunks
back together *and* optionally transcode while splitting.

New in this edition
-------------------
* **Codec inference + re‑encode** while chunking (default FLAC @16 kHz/mono).
* Command‑line knobs mirroring *audio_transcoder_cli.py* (`--codec`, `--sr`, `--ch`, `--bitrate`).
* `split` will fall back to *copy* when `--codec copy` is requested.
* Joined file inherits the extension you give it (codec inferred automatically).

Usage
-----
Split (re‑encode to FLAC chunks):
    python chunk_audio.py split recording.m4a                # FLAC @16 kHz/mono chunks
    python chunk_audio.py split recording.m4a -c 90 -v       # 90‑sec chunks, verbose
    python chunk_audio.py split rec.m4a -c 240 --codec opus  # Opus chunks, 24 kbps

Join:
    python chunk_audio.py join recording_chunks/ merged.flac # assemble back

Exit status ≠0 signals an error.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from datetime import timedelta
from pathlib import Path
from typing import List, NoReturn

from .utils import fatal, check_ffmpeg, CHUNK_DEFAULT_SECS

DEFAULT_SAMPLE_RATE = 16_000
DEFAULT_CHANNELS = 1
CODEC_MAP = {
    "flac": {"codec": "flac", "ext": ".flac"},
    "opus": {"codec": "libopus", "ext": ".opus"},
    "wav": {"codec": "pcm_s16le", "ext": ".wav"},
    "mp3": {"codec": "libmp3lame", "ext": ".mp3"},
    "aac": {"codec": "aac", "ext": ".m4a"},
    "copy": {"codec": "copy", "ext": None},  # keep orig ext
}


# ---------------------------------------------------------------------------
# Split helpers
# ---------------------------------------------------------------------------


def infer_codec(name: str | None) -> dict:
    if not name:
        return CODEC_MAP["flac"]
    if name not in CODEC_MAP:
        fatal(f"Unsupported codec: {name}")
    return CODEC_MAP[name]


def build_ffmpeg_split_cmd(
    infile: Path,
    out_template: Path,
    chunk: int,
    enc: dict,
    sample_rate: int,
    channels: int,
    bitrate: str | None,
    verbose: bool,
) -> List[str]:
    base_cmd = ["ffmpeg", "-hide_banner"]
    if not verbose:
        base_cmd += ["-loglevel", "error"]
    base_cmd += ["-i", str(infile)]

    # Re‑encode unless codec == copy
    if enc["codec"] != "copy":
        base_cmd += [
            "-ac",
            str(channels),
            "-ar",
            str(sample_rate),
            "-c:a",
            enc["codec"],
        ]
        if bitrate:
            base_cmd += ["-b:a", bitrate]
    else:
        base_cmd += ["-c", "copy"]

    # segment muxer options *after* input‑specific flags
    base_cmd += [
        "-f",
        "segment",
        "-segment_time",
        str(chunk),
        "-reset_timestamps",
        "1",
        str(out_template),
    ]
    return base_cmd


def split_audio(
    infile: Path,
    outdir: Path,
    chunk: int,
    codec_name: str | None,
    sample_rate: int,
    channels: int,
    bitrate: str | None,
    verbose: bool,
) -> None:
    if not infile.is_file():
        fatal(f"Input file not found: {infile}")

    enc = infer_codec(codec_name)
    outdir.mkdir(parents=True, exist_ok=True)
    suffix = enc["ext"] or infile.suffix  # copy keeps original extension
    template = outdir / f"{infile.stem}_%03d{suffix}"

    cmd = build_ffmpeg_split_cmd(
        infile,
        template,
        chunk,
        enc,
        sample_rate,
        channels,
        bitrate,
        verbose,
    )
    if verbose:
        print("[ffmpeg]", " ".join(cmd))

    try:
        # Capture output and check for errors
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        # Construct a detailed error message including stderr if available
        error_message = f"FFmpeg command (split) failed (exit code {exc.returncode})."
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

    chunks = sorted(outdir.glob(f"{infile.stem}_*{suffix}"))
    if not chunks:
        fatal(
            "No chunks were created – FFmpeg produced no output. Check the codec/format."
        )

    total = timedelta(seconds=len(chunks) * chunk)
    for p in chunks:
        print(f"  • {p.name}")
    print(f"✅ {len(chunks)} chunk(s) written → {outdir.resolve()} (≈{total})")


# ---------------------------------------------------------------------------
# Join helpers
# ---------------------------------------------------------------------------


def build_ffmpeg_join_cmd(list_file: Path, outfile: Path, verbose: bool) -> List[str]:
    cmd = [
        "ffmpeg",
        "-hide_banner",
        *([] if verbose else ["-loglevel", "error"]),
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(list_file),
        "-c",
        "copy",
        str(outfile),
    ]
    return cmd


def join_audio(indir: Path, outfile: Path, verbose: bool) -> None:
    if not indir.is_dir():
        fatal(f"Input directory not found: {indir}")

    chunks = sorted(p for p in indir.iterdir() if p.is_file())
    if not chunks:
        fatal("No audio chunks found in the specified directory.")

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tf:
        for p in chunks:
            tf.write(f"file '{p.as_posix()}'\n")
        list_path = Path(tf.name)

    cmd = build_ffmpeg_join_cmd(list_path, outfile, verbose)
    if verbose:
        print("[ffmpeg]", " ".join(cmd))

    try:
        # Capture output and check for errors
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        # Construct a detailed error message including stderr if available
        error_message = f"FFmpeg command (join) failed (exit code {exc.returncode})."
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
    finally:
        list_path.unlink(missing_ok=True)

    print(f"✅ Assembled {len(chunks)} chunks → {outfile.resolve()}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="chunk_audio.py",
        description="Split an audio file into chunks or join existing chunks, with optional transcoding during split.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # split
    p_split = sub.add_parser("split", help="Split an audio file into chunks")
    p_split.add_argument("input", type=Path, help="Input audio file")
    p_split.add_argument(
        "-c",
        "--chunk",
        type=int,
        default=CHUNK_DEFAULT_SECS,
        metavar="SECONDS",
        help="Length of each chunk in seconds",
    )
    p_split.add_argument(
        "-o",
        "--outdir",
        type=Path,
        help="Directory to save chunks (default: <input>_chunks)",
    )
    p_split.add_argument(
        "--codec",
        choices=list(CODEC_MAP.keys()),
        help="Output codec for chunks (default: flac)",
    )
    p_split.add_argument(
        "--sr",
        "--sample-rate",
        type=int,
        default=DEFAULT_SAMPLE_RATE,
        help="Sample rate in Hz",
    )
    p_split.add_argument(
        "--ch",
        "--channels",
        type=int,
        default=DEFAULT_CHANNELS,
        help="Number of channels",
    )
    p_split.add_argument("--bitrate", help="Bit‑rate for lossy codecs, e.g. 24k")
    p_split.add_argument(
        "-v", "--verbose", action="store_true", help="Show FFmpeg output"
    )

    # join
    p_join = sub.add_parser("join", help="Join chunks back into a single file")
    p_join.add_argument("indir", type=Path, help="Directory containing chunks")
    p_join.add_argument(
        "output", type=Path, help="Output re‑assembled file (extension ↔ codec)"
    )
    p_join.add_argument(
        "-v", "--verbose", action="store_true", help="Show FFmpeg output"
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    check_ffmpeg()

    if args.command == "split":
        outdir = args.outdir or args.input.with_suffix("").with_name(
            f"{args.input.stem}_chunks"
        )
        split_audio(
            infile=args.input,
            outdir=outdir,
            chunk=args.chunk,
            codec_name=args.codec,
            sample_rate=args.sr,
            channels=args.ch,
            bitrate=args.bitrate,
            verbose=args.verbose,
        )

    elif args.command == "join":
        join_audio(args.indir, args.output, args.verbose)

    else:
        parser.error("Unknown command")


if __name__ == "__main__":
    main()
