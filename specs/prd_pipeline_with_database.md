# PRD: Automated Audio Processing Pipeline with Database Tracking

## 1. Introduction

This document outlines the requirements for an automated audio processing pipeline. The system will take an input audio file, process it through several stages (chunking, voice conversion, joining), and track the status of each file using an SQLite database. The goal is to create a resilient and manageable workflow for batch audio processing.

## 2. Goals

*   Automate the multi-step audio processing workflow.
*   Provide clear status tracking for each processed file.
*   Ensure resilience by allowing a file's processing to be resumed or retried if a stage fails.
*   Avoid re-processing already successfully processed files.
*   Establish a standardized directory structure for clarity and organization.
*   Centralize database operations into a dedicated module.

## 3. Core Components

### 3.1. Standardized Directory Structure

A clear directory structure will be established to manage files at different stages:

*   `pipeline_input/`: "Bucket" directory where users drop new audio files (e.g., MP4, WAV, M4A).
*   `pipeline_processing/`: Root for intermediate files.
    *   `pipeline_processing/<job_id>/original/`: Stores a copy of the original input file.
    *   `pipeline_processing/<job_id>/chunks/`: Stores audio chunks created by `lossless_splitter.py` or `audio_chunker.py split`.
    *   `pipeline_processing/<job_id>/converted_chunks/`: Stores voice-converted chunks from `convert.py`.
*   `pipeline_output/`: Directory for the final assembled audio files from `audio_chunker.py join`.
*   `pipeline_data/`:
    *   `pipeline_data/audio_pipeline.db`: The SQLite database file.
    *   `pipeline_data/logs/`: For storing detailed logs (future enhancement).

*(Note: `<job_id>` would be a unique identifier for each processing job, likely derived from the database unique ID).*

### 3.2. Input Mechanism

*   Users will place new audio files into the `pipeline_input/` directory.
*   The system needs a mechanism (e.g., a polling orchestrator) to detect these new files.

### 3.3. Processing Pipeline Stages

The pipeline will utilize the existing (and refactored) scripts as stages:

1.  **Initial Ingestion:** New file detected, copied to its unique processing directory, and DB record created.
2.  **Chunking:**
    *   Uses `spudshut/lossless_splitter.py` (for lossless splitting) or `spudshut/audio_chunker.py split` (if initial transcoding is desired, TBD).
    *   Input: Original audio file.
    *   Output: Audio chunks in `pipeline_processing/<job_id>/chunks/`.
3.  **Voice Conversion:**
    *   Uses `spudshut/convert.py`.
    *   Input: Directory of chunks (`pipeline_processing/<job_id>/chunks/`).
    *   Output: Directory of converted chunks (`pipeline_processing/<job_id>/converted_chunks/`).
4.  **Joining:**
    *   Uses `spudshut/audio_chunker.py join`.
    *   Input: Directory of converted chunks (`pipeline_processing/<job_id>/converted_chunks/`).
    *   Output: Final assembled audio file in `pipeline_output/`.

### 3.4. SQLite Database Operator

A dedicated Python module (e.g., `spudshut/db_operator.py`) will encapsulate all SQLite database interactions.

#### 3.4.1. Database Schema (`audio_pipeline.db`)

*   **Table: `processing_jobs`**
    *   `job_id` (INTEGER, Primary Key, Autoincrement) - Unique ID for the processing job.
    *   `original_filename` (TEXT, NOT NULL) - Original name of the dropped file.
    *   `job_identifier` (TEXT, UNIQUE, NOT NULL) - A unique string to identify the job, perhaps a hash of original file + timestamp, or a UUID. Used for directory naming.
    *   `status` (TEXT, NOT NULL) - Current stage in the pipeline (e.g., "NEW", "PENDING_CHUNK", "CHUNKING", "CHUNKED", "PENDING_CONVERSION", "CONVERTING", "CONVERTED", "PENDING_JOIN", "JOINING", "COMPLETED", "ERROR").
    *   `input_file_path` (TEXT) - Path to the original file copy in `pipeline_processing`.
    *   `chunks_dir_path` (TEXT) - Path to the directory containing chunks.
    *   `converted_chunks_dir_path` (TEXT) - Path to the directory containing converted chunks.
    *   `output_file_path` (TEXT) - Path to the final processed file in `pipeline_output`.
    *   `last_updated` (TIMESTAMP, NOT NULL, DEFAULT CURRENT_TIMESTAMP) - Timestamp of the last status update.
    *   `created_at` (TIMESTAMP, NOT NULL, DEFAULT CURRENT_TIMESTAMP) - Timestamp of job creation.
    *   `error_message` (TEXT) - Stores error details if a stage fails.

#### 3.4.2. Key Operations for DB Operator

*   `initialize_database()`: Creates the table if it doesn't exist.
*   `add_new_job(original_filename: str, job_identifier: str, input_file_path: str) -> int`: Adds a new file to the database with status "NEW". Returns the `job_id`.
*   `update_job_status(job_id: int, new_status: str)`: Updates the status and `last_updated` timestamp.
*   `update_job_paths(job_id: int, chunks_dir: str = None, converted_chunks_dir: str = None, output_file: str = None)`: Updates path fields as stages complete.
*   `log_job_error(job_id: int, error_msg: str)`: Sets status to "ERROR" and records the error message.
*   `get_jobs_by_status(status: str) -> list`: Retrieves all jobs with a specific status.
*   `get_job_details(job_id: int) -> dict`: Retrieves all details for a specific job.
*   `check_if_job_exists(original_filename: str, file_hash: str) -> bool`: (Future: Use file hash to truly check for duplicates if filenames can be reused). For now, can check by `original_filename` and a recent "COMPLETED" status.

### 3.5. Orchestrator Script

A new main Python script (e.g., `pipeline_orchestrator.py`) will manage the overall workflow:

1.  **Watch Input Directory:** Periodically scan `pipeline_input/` for new files.
2.  **File Ingestion:**
    *   For each new file:
        *   Generate a unique `job_identifier`.
        *   Copy the file to `pipeline_processing/<job_identifier>/original/`.
        *   Call `db_operator.add_new_job()` to create a database record.
        *   Move the original file from `pipeline_input/` to an archive (e.g., `pipeline_input/processed/`) or delete it, to prevent re-processing.
3.  **Process Pending Jobs:**
    *   Periodically query the database for jobs in various pending states (e.g., "NEW", "CHUNKED", "CONVERTED").
    *   For each pending job, trigger the corresponding pipeline stage:
        *   Update status to "IN_PROGRESS_STAGE" (e.g., "CHUNKING").
        *   Execute the relevant script (e.g., `lossless_splitter.py`) as a subprocess, passing necessary paths.
        *   Upon successful completion of a stage, update status to "STAGE_COMPLETED" (e.g., "CHUNKED") and store output paths in the DB.
        *   If a stage fails, call `db_operator.log_job_error()`.

## 4. Workflow Example

1.  User drops `my_talk.mp4` into `pipeline_input/`.
2.  Orchestrator detects `my_talk.mp4`.
    *   Generates `job_identifier` (e.g., `mytalk_20231027100000`).
    *   Copies file to `pipeline_processing/mytalk_20231027100000/original/my_talk.mp4`.
    *   DB: `add_new_job("my_talk.mp4", "mytalk_20231027100000", ...)` -> `job_id = 1`, status "NEW".
    *   Moves `my_talk.mp4` from input.
3.  Orchestrator queries for "NEW" jobs. Finds `job_id = 1`.
    *   DB: `update_job_status(1, "CHUNKING")`.
    *   Executes `lossless_splitter.py` for `job_id = 1`. Chunks are saved to `pipeline_processing/mytalk_20231027100000/chunks/`.
    *   DB: `update_job_status(1, "CHUNKED")`, `update_job_paths(1, chunks_dir=...)`.
4.  Orchestrator queries for "CHUNKED" jobs. Finds `job_id = 1`.
    *   DB: `update_job_status(1, "CONVERTING")`.
    *   Executes `convert.py` for chunks in `pipeline_processing/mytalk_20231027100000/chunks/`. Converted chunks to `.../converted_chunks/`.
    *   DB: `update_job_status(1, "CONVERTED")`, `update_job_paths(1, converted_chunks_dir=...)`.
5.  Orchestrator queries for "CONVERTED" jobs. Finds `job_id = 1`.
    *   DB: `update_job_status(1, "JOINING")`.
    *   Executes `audio_chunker.py join` for `.../converted_chunks/`. Output to `pipeline_output/mytalk_20231027100000_final.flac`.
    *   DB: `update_job_status(1, "COMPLETED")`, `update_job_paths(1, output_file=...)`.

## 5. Error Handling and Resilience

*   Each pipeline stage execution should be wrapped in try-except blocks.
*   Failures should be logged to the database with an "ERROR" status and an error message.
*   The orchestrator should not halt on a single job failure; it should continue processing other jobs.
*   A mechanism to manually or automatically retry "ERROR" jobs could be a future enhancement.

## 6. Out of Scope for Initial Version (Future Considerations)

*   Detailed file-based logging for each stage.
*   Web UI/Dashboard for monitoring job statuses.
*   Automatic retry logic for failed jobs.
*   Advanced duplicate detection (e.g., file content hashing).
*   Support for parallel processing of multiple files or stages.
*   Configuration file for pipeline settings (paths, API keys, etc.). 