# Code Refactor Plan: Audio Processing Scripts

This document outlines a plan for refactoring the Python audio processing scripts:
- `spudshut/convert.py`
- `spudshut/spud_converter.py`
- `spudshut/audio_transcoder.py`

The goals are to reduce code duplication, simplify logic, and improve maintainability.

## Phase 1: Address Critical Issue (Completed)

- **Issue:** `spudshut/convert.py` (voice conversion) re-processed already converted files, leading to unnecessary API calls and potential rate limiting (e.g., HTTP 429 errors).
- **Solution Implemented:** Modified `spudshut/convert.py` to pre-scan the output directory. It now builds a set of already converted file stems and uses that to determine which input files need processing, unless `--overwrite` is specified.
- **Status:** ✅ Done.

## Phase 2: Code Review Findings & Refactoring Tasks

### Task 1: Create Shared Utilities Module

- **Description:** Consolidate common utility functions into a new `spudshut/utils.py` module.
- **Files Affected:** `spudshut/convert.py`, `spudshut/spud_converter.py`, `spudshut/audio_transcoder.py`
- **Details:**
    - **Function to move:** `fatal(msg: str) -> NoReturn`
        - *Current locations:* `convert.py` (lines 45-53), `spud_converter.py` (lines 30-34), `audio_transcoder.py` (lines 39-42)
    - **Function to move:** `check_ffmpeg()`
        - *Current locations:* `spud_converter.py` (lines 37-39), `audio_transcoder.py` (lines 45-47)
- **Action:**
    1. Create `spudshut/utils.py`.
    2. Move the specified functions into `spudshut/utils.py`.
    3. Update `convert.py`, `spud_converter.py`, and `audio_transcoder.py` to import and use these functions from `spudshut/utils.py`.
- **Priority:** High
- **Status:** Pending

### Task 2: Evaluate Redundancy of `spud_converter.py`

- **Description:** `spud_converter.py` functionality (lossless audio splitting) appears to be a subset of `audio_transcoder.py split --codec copy`. Evaluate if `spud_converter.py` can be deprecated or merged.
- **Files Affected:** `spudshut/spud_converter.py`, `spudshut/audio_transcoder.py`
- **Considerations:**
    - `spud_converter.py` offers a simpler interface for its specific task.
    - User preference for single-function files vs. maintainability of fewer, more comprehensive scripts.
- **Action:**
    1. Discuss with the development team/user the pros and cons of merging.
    2. If merging is decided:
        - Ensure `audio_transcoder.py split --codec copy` fully covers all use cases of `spud_converter.py`.
        - Update any documentation or scripts that might reference `spud_converter.py`.
        - Delete `spud_converter.py`.
- **Priority:** Medium
- **Status:** Pending

### Task 3: Enhance FFmpeg Error Reporting

- **Description:** Improve FFmpeg error feedback to users by capturing and displaying `stderr` output directly when an FFmpeg command fails.
- **Files Affected:** `spudshut/spud_converter.py`, `spudshut/audio_transcoder.py`
- **Details:**
    - Currently, a generic "FFmpeg failed" message is shown, requiring a rerun with `-v`.
    - Modifying `subprocess.run()` calls (e.g., with `capture_output=True, text=True`) can allow direct access to `stderr`.
- **Action:**
    1. Update FFmpeg execution logic in affected scripts to capture `stderr`.
    2. If `CalledProcessError` occurs, print the captured `stderr` along with the error message.
- **Priority:** Medium
- **Status:** Pending

### Task 4: Review Constants for Centralization

- **Description:** Identify and centralize shared constants.
- **Files Affected:** `spudshut/spud_converter.py`, `spudshut/audio_transcoder.py`
- **Details:**
    - `CHUNK_DEFAULT_SECS` is defined in both `spud_converter.py` (line 27) and `audio_transcoder.py` (line 26).
- **Action:**
    1. If these constants should always be synchronized, move them to `spudshut/utils.py` or a dedicated `spudshut/constants.py`.
    2. Update scripts to import the constant from the central location.
- **Priority:** Low
- **Status:** Pending

### Task 5: Investigate Robustness of `audio_transcoder.py join`

- **Description:** The `join_audio` function in `audio_transcoder.py` currently uses `ffmpeg -c copy`. This might fail if chunks have incompatible codecs with the desired output container (inferred from the output filename extension) or if chunks have mixed codecs.
- **Files Affected:** `spudshut/audio_transcoder.py`
- **Details:**
    - For example, joining FLAC chunks into an MP3 output file with `-c copy` will not work.
- **Action:**
    1. Evaluate the need for re-encoding during the join operation based on output file extension and chunk codecs.
    2. If necessary, enhance `join_audio` to detect codec mismatches and transcode accordingly (similar to how the `split` command handles transcoding options). This would increase complexity but improve robustness.
- **Priority:** Medium
- **Status:** Pending

## Other Observations

- **Argument Parsing:** While not direct duplication, common CLI argument patterns exist (input/output paths, verbosity). Current separation is acceptable but could be unified if a more cohesive CLI toolset is envisioned.
- **Output Directory Creation:** `mkdir(parents=True, exist_ok=True)` is a common pattern. Could be a shared utility function but is low priority. 