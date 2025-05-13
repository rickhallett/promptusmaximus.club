#!/usr/bin/env python3
"""
Shared utility functions for SpudShut audio processing scripts.
"""
from __future__ import annotations

import sys
import shutil
from typing import NoReturn


def fatal(msg: str) -> NoReturn:
    """
    Prints an error message to stderr and exits the program with status 1.

    Args:
        msg (str): The error message to print.

    Returns:
        NoReturn: This function does not return, it exits the program.
    """
    sys.stderr.write(f"Error: {msg}\\n")
    sys.exit(1)


def check_ffmpeg() -> None:
    """
    Checks if the FFmpeg executable is available on the system PATH.
    Calls fatal() if FFmpeg is not found.
    """
    if shutil.which("ffmpeg") is None:
        fatal("FFmpeg executable not found – install it and ensure it's on PATH.")


# Shared constants
CHUNK_DEFAULT_SECS = 240  # Default chunk length in seconds (4 minutes)
