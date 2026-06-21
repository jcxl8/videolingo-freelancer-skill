# Troubleshooting

## Exit codes

| Code | Meaning | Action |
|---:|---|---|
| 0 | Command completed | Validate returned artifacts and warnings. |
| 2 | Input, repository, or argument error | Correct the path, input type, or option. Confirm this is a customized checkout. |
| 3 | Environment unavailable | Run `doctor --json`; fix Python, FFmpeg, MLX, WhisperX, model service, or TTS availability. |
| 4 | Pipeline stage failed | Run `status --json`; inspect `details.stage` and `details.error`; rerun the smallest stage after correction. |
| 5 | Subtitle proofread blocked | Review the JSON/Markdown report. Do not render or dub until errors are corrected. |
| 130 | Interrupted | Preserve intermediates, inspect status, and resume deliberately. |

## Common failures

### Customized checkout not found

Pass `--repo`, set `VIDEOLINGO_FREELANCER_HOME`, or start inside the customized repository. If marker files are missing, do not run against ordinary upstream VideoLingo.

### MLX unavailable on macOS

Automatic macOS mode selects `mlx` and `large-v3`. Install the customized checkout's MLX dependencies or explicitly choose `--asr-runtime local` if its WhisperX environment is valid.

### WhisperX unavailable on Linux or Windows

Automatic non-macOS mode selects `local` and `large-v3`. Repair the existing WhisperX environment before retrying. Do not silently fall back to a remote ASR API.

### Translation endpoint unavailable

Check the configured workflow and translator services without printing credentials. Test only non-secret health/model endpoints, then rerun `subtitles`; existing completed transcription intermediates may allow the application to skip earlier work.

### Watermark text breaks rendering

Use `--watermark-text` rather than editing application source. The CLI converts filter metacharacters to literal full-width forms. Use `--no-watermark` to isolate whether a remaining failure is watermark-related.

### Proofread blocks

Open the reported subtitle entries, compare them to the audio, correct the smallest upstream cause, and rerun `proofread`. Do not bypass exit code 5 or delete all outputs as a first response.
