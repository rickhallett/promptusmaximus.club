# Code Refactor Plan: Audio Processing Scripts

This document outlines a plan for refactoring the Python audio processing scripts:
- `spudshut/convert.py`
- `spudshut/lossless_splitter.py` (formerly `spud_converter.py`)
- `spudshut/audio_chunker.py` (formerly `audio_transcoder.py`)

The goals are to reduce code duplication, simplify logic, and improve maintainability.

## Phase 1: Address Critical Issue & Initial Refactor (Completed)

- **Issue:** `spudshut/convert.py` (voice conversion) re-processed already converted files.
- **Solution Implemented:** Modified `spudshut/convert.py` to pre-scan the output directory and skip existing files unless `--overwrite` is specified.
- **Status:** ✅ Done.

- **Refactor:** Centralized `fatal()` and `check_ffmpeg()` utilities into `spudshut/utils.py`.
- **Status:** ✅ Done.

- **Refactor:** Renamed `spudshut/spud_converter.py` to `spudshut/lossless_splitter.py` and `spudshut/audio_transcoder.py` to `spudshut/audio_chunker.py` for clarity.
- **Status:** ✅ Done.

## AI Assistant Workflow Policy

- **Commit Message Auto-Generation:** The AI assistant is expected to auto-generate conventional commit messages for all changes. If uncertain, the AI will propose a message for user confirmation. This policy is also documented in [`ai_conventions.mdc`](mdc:.cursor/rules/ai_conventions.md) and the project's `dev_workflow.md` rule.

## Phase 2: Ongoing Refactoring Tasks (Renamed Files)

### Task 1: Create Shared Utilities Module (Completed)
- See Phase 1.

### Task 2: Clarify Script Roles via Renaming (Completed)
- **Decision:** Keep both original splitting scripts but rename them for clarity.
    - `spudshut/spud_converter.py` → `spudshut/lossless_splitter.py`
    - `spudshut/audio_transcoder.py` → `spudshut/audio_chunker.py`
- **Status:** ✅ Done.

### Task 3: Enhance FFmpeg Error Reporting

- **Description:** Improve FFmpeg error feedback by capturing and displaying `stderr` output directly.
- **Files Affected:** `spudshut/lossless_splitter.py`, `spudshut/audio_chunker.py`
- **Priority:** Medium
- **Status:** Pending

### Task 4: Review Constants for Centralization

- **Description:** Identify and centralize shared constants (e.g., `CHUNK_DEFAULT_SECS`).
- **Files Affected:** `spudshut/lossless_splitter.py`, `spudshut/audio_chunker.py`
- **Action:** Move to `spudshut/utils.py` or `spudshut/constants.py`.
- **Priority:** Low
- **Status:** Pending

### Task 5: Investigate Robustness of `audio_chunker.py join`

- **Description:** The `join_audio` function in `spudshut/audio_chunker.py` uses `ffmpeg -c copy`. Investigate if re-encoding is needed for robustness when chunk codecs/containers differ from the desired output.
- **Files Affected:** `spudshut/audio_chunker.py`
- **Priority:** Medium
- **Status:** Pending

## Other Observations

- **Argument Parsing:** Common CLI argument patterns exist. Current separation is acceptable.
- **Output Directory Creation:** `mkdir(parents=True, exist_ok=True)` is a common pattern. Low priority for utility function. 