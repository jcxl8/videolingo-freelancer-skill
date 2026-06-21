---
name: videolingo-freelancer
description: Use when operating, diagnosing, resuming, or verifying an existing customized VideoLingo-Freelancer checkout to transcribe, translate, proofread, render, dub, or archive a localized video.
---

# VideoLingo-Freelancer

Operate the existing customized application through the bundled CLI. Do not patch an ordinary upstream VideoLingo checkout or require Streamlit.

## Start safely

Resolve this Skill directory from the loaded `SKILL.md` path and set `CLI` to `scripts/videolingo_freelancer.py` inside it.

1. Run `python "$CLI" --json doctor`.
2. Before mutation, run the intended command with global `--dry-run`, for example `python "$CLI" --json --dry-run run --input VIDEO`.
3. Show the resolved repository, planned stages, ASR runtime, model, and watermark choice.
4. Execute only after inputs are unambiguous. Never print configuration secrets.

Repository discovery prefers `--repo`, then `VIDEOLINGO_FREELANCER_HOME`, a customized parent checkout, `~/VideoLingo-Freelancer`, and finally legacy `~/VideoLingo`. Marker validation rejects an ordinary upstream checkout.

## Choose a command

- `doctor`, `status`: read-only inspection.
- `prepare INPUT`: copy a local video or download a URL.
- `subtitles`: ASR through aligned subtitle generation.
- `proofread`: audit all SRT variants. Treat exit code 5 as a hard stop.
- `render`: burn selected subtitles; add `--watermark-text "NAME"` or `--no-watermark`.
- `dub`: synthesize and merge translated audio.
- `archive`: move completed artifacts into history and verify the manifest.
- `run`: execute the guarded workflow. Add `--dub` for dubbing.

On macOS, automatic ASR uses MLX Whisper. On other systems it uses local WhisperX. Both default to `large-v3`; explicit `--asr-runtime` and `--whisper-model` win.

## Stop and report

Stop on any nonzero exit. For exit code 5, report proofread errors and do not render or dub. Warnings may continue but must appear in the final summary. Never delete outputs to recover; use `status`, fix the cause, and rerun the smallest failed command.

Read [workflow details](references/workflow.md) before a full run or resume. Read [configuration](references/configuration.md) for discovery, ASR, model services, or environment failures. Read [artifacts](references/artifacts.md) when locating or validating results. Read [troubleshooting](references/troubleshooting.md) after any nonzero exit.
