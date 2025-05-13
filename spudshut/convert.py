#!/usr/bin/env python3
"""
voice_convert_chunks.py — batch‑convert a folder of audio chunks into a new voice
using the ElevenLabs *Voice Changer* (speech‑to‑speech) API.

Features
########
* Reads all audio files in <input_dir> (alphabetical order).
* Converts each file to the target **voice** (voice *name* or *ID*).
* Saves output files with **identical basenames** (new extension inferred from
  --output-format) in <output_dir> to avoid name clashes.
* Provides **--list-voices** utility to print all available voice names/IDs.
* Mirrors naming/flag style of `chunk_audio.py`.

Install deps:
    pip install elevenlabs python-dotenv tqdm

Environment:
    ELEVENLABS_API_KEY  (or pass --api-key)

Examples
========
```bash
# Show voices
python voice_convert_chunks.py --list-voices

# Convert folder to Rachel's voice, opus output @48 kHz (≈64 kbps)
python voice_convert_chunks.py chunks/ rachel_chunks/ \
    --voice "Rachel" --output-format opus_48000_64 --model eleven_multilingual_sts_v2
```
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import List, NoReturn

from tqdm import tqdm  # progress bar
from elevenlabs.client import ElevenLabs
from elevenlabs import save
import dotenv

from .utils import fatal  # Import from utils

dotenv.load_dotenv()

DEFAULT_MODEL = "eleven_multilingual_sts_v2"
DEFAULT_OUTPUT_FORMAT = (
    "wav"  # ElevenLabs short‑codes, e.g. wav, mp3_44100_128, opus_48000_64
)


def resolve_voice_id(client: ElevenLabs, ident: str) -> str:
    """
    Resolves a voice identifier (name or ID) to a valid voice ID.

    Args:
        client (ElevenLabs): The ElevenLabs client instance.
        ident (str): The voice identifier (can be a name or an ID).

    Returns:
        str: The resolved voice ID.

    Raises:
        SystemExit: If the voice name is not found.
    """
    id_like = re.fullmatch(r"[A-Za-z0-9]{10,}", ident)
    if id_like:
        return ident  # assume already an ID

    # otherwise search by name (case‑insensitive)
    voices = client.voices.get_all().voices  # type: ignore[attr-defined]
    for v in voices:
        if v.name.lower() == ident.lower():
            return v.voice_id  # type: ignore[attr-defined]
    names = ", ".join(sorted(v.name for v in voices))
    fatal(f"Voice name '{ident}' not found. Available voices: {names}")


# ---------------------------------------------------------------------------
# Conversion
# ---------------------------------------------------------------------------


def ext_from_output_format(fmt: str) -> str:
    """
    Determines the appropriate file extension based on the ElevenLabs output format string.

    Args:
        fmt (str): The ElevenLabs output format string (e.g., 'mp3_44100_128', 'wav', 'opus_48000_64').

    Returns:
        str: The corresponding file extension (e.g., '.mp3', '.wav', '.opus').
    """
    root = fmt.split("_")[0].lower()
    mapping = {"mp3": ".mp3", "wav": ".wav", "opus": ".opus", "ulaw": ".wav"}
    return mapping.get(root, ".wav")


def convert_file(
    client: ElevenLabs,
    voice_id: str,
    in_path: Path,
    out_path: Path,
    model_id: str,
    output_format: str,
):
    """
    Converts a single audio file to a different voice using ElevenLabs speech-to-speech.

    Args:
        client (ElevenLabs): The ElevenLabs client instance.
        voice_id (str): The ID of the target voice.
        in_path (Path): Path to the input audio file.
        out_path (Path): Path to save the converted audio file.
        model_id (str): The ID of the speech-to-speech model to use.
        output_format (str): The desired output format string for the converted audio.

    Returns:
        None
    """
    with in_path.open("rb") as f:
        audio_stream = client.speech_to_speech.convert(  # type: ignore[attr-defined]
            voice_id=voice_id,
            audio=f,
            model_id=model_id,
            output_format=output_format,
        )
        # `audio_stream` can be bytes or an iterator; `save` handles both
        save(audio_stream, out_path.as_posix())


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    """
    Builds and returns the command-line argument parser for the script.

    Args:
        None

    Returns:
        argparse.ArgumentParser: The configured argument parser.
    """
    p = argparse.ArgumentParser(
        prog="voice_convert_chunks.py",
        description="Batch‑convert audio files in a folder to a different voice via ElevenLabs Voice Changer API.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    # Directories are now optional flags, required only for conversion mode
    p.add_argument("--input-dir", type=Path, help="Directory containing source chunks")
    p.add_argument(
        "--output-dir", type=Path, help="Directory to write converted chunks"
    )
    p.add_argument("--voice", "-v", required=False, help="Target voice name or ID")
    p.add_argument("--model", default=DEFAULT_MODEL, help="Model ID to use")
    p.add_argument(
        "--output-format",
        default=DEFAULT_OUTPUT_FORMAT,
        help="ElevenLabs output_format string",
    )
    p.add_argument(
        "--api-key", help="Explicit ElevenLabs API key (else env ELEVENLABS_API_KEY)"
    )
    p.add_argument(
        "--list-voices", action="store_true", help="List available voices and exit"
    )
    p.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files in output_dir",
    )
    return p


def main() -> None:
    """
    Main function to handle argument parsing, voice listing, and file conversion.

    Reads command-line arguments, lists voices if requested, or performs batch
    conversion of audio files in the input directory to the specified voice,
    saving them to the output directory.

    Args:
        None

    Returns:
        None

    Raises:
        SystemExit: If required arguments are missing or directories are invalid.
    """
    args = build_parser().parse_args()

    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        if not args.api_key:
            fatal("ELEVENLABS_API_KEY is not set")
        api_key = args.api_key

    client = ElevenLabs(api_key=api_key)

    # Handle --list-voices mode first, as it doesn't need other args
    if args.list_voices:
        voices = client.voices.get_all().voices  # type: ignore[attr-defined]
        print("Available ElevenLabs Voices:")
        print("----------------------------")
        for v in voices:
            print(f"{v.voice_id}\\t{v.name}")  # id \\t name
        print("----------------------------")
        return

    # --- Conversion Mode ---
    # These arguments are required if not listing voices
    if not args.input_dir:
        fatal("--input-dir is required for conversion mode.")
    if not args.output_dir:
        fatal("--output-dir is required for conversion mode.")
    if not args.voice:
        fatal("--voice is required for conversion mode.")

    if not args.input_dir.is_dir():
        fatal(f"Input directory not found: {args.input_dir}")

    args.output_dir.mkdir(parents=True, exist_ok=True)

    voice_id = resolve_voice_id(client, args.voice)
    ext = ext_from_output_format(args.output_format)

    # Get all potential input files
    all_input_files = sorted(p for p in args.input_dir.iterdir() if p.is_file())
    if not all_input_files:
        fatal(f"No audio files found in {args.input_dir.resolve()}.")

    files_to_process: List[Path] = []
    skipped_count = 0

    if args.overwrite:
        files_to_process = all_input_files
    else:
        existing_output_stems = set()
        if args.output_dir.exists():
            for f_out in args.output_dir.glob(f"*{ext}"):
                if f_out.is_file():
                    existing_output_stems.add(f_out.stem)

        for in_path_candidate in all_input_files:
            if in_path_candidate.stem in existing_output_stems:
                tqdm.write(
                    f"Skipping existing (pre-scan): {in_path_candidate.stem}{ext}"
                )
                skipped_count += 1
            else:
                files_to_process.append(in_path_candidate)

    if not files_to_process:
        message = f"No files to process. All {len(all_input_files)} input file(s) seem "
        if args.output_dir.exists():
            message += f"to have corresponding outputs with '{ext}' extension in {args.output_dir.resolve()}."
        else:
            message += f"as output directory {args.output_dir.resolve()} does not exist or is empty."
        if not args.overwrite and len(all_input_files) > 0:
            message += " Use --overwrite to re-process."
        print(message)
        return

    for in_path in tqdm(files_to_process, desc="Converting", unit="file"):
        out_filename = in_path.stem + ext
        out_path = args.output_dir / out_filename
        # The pre-scan logic handles skipping if not overwriting.
        # If overwriting, all files are in files_to_process.
        convert_file(
            client, voice_id, in_path, out_path, args.model, args.output_format
        )

    processed_count = len(files_to_process)
    summary_message = f"✅ Processed {processed_count} file(s)"
    if skipped_count > 0:
        summary_message += f", skipped {skipped_count} existing file(s)"
    summary_message += f". Output → {args.output_dir.resolve()}"
    print(summary_message)


if __name__ == "__main__":
    main()
