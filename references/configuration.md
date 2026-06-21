# Configuration and environment

## Locate the customized checkout

Discovery order is:

1. `--repo PATH`
2. `VIDEOLINGO_FREELANCER_HOME`
3. Legacy `VIDEOLINGO_JUNCAI_HOME`
4. Current directory and parents
5. `~/VideoLingo-Freelancer`
6. Legacy `~/VideoLingo-Juncai`
7. Legacy `~/VideoLingo`

The checkout must contain `st.py`, `core/_2_asr.py`, `core/subtitle_proofread.py`, `core/utils/model_router.py`, and `scripts/run_regression_checks.py`. These markers distinguish VideoLingo-Freelancer from ordinary upstream VideoLingo.

For a shared installation, recommend setting:

```bash
export VIDEOLINGO_FREELANCER_HOME="$HOME/VideoLingo-Freelancer"
```

Do not assume a username or copy a path from another machine. Existing installations may keep using `VIDEOLINGO_JUNCAI_HOME` or `~/VideoLingo-Juncai`; these names are read-only compatibility fallbacks, not the public identity of new installations.

## Required runtime

- A Python environment that already runs the customized checkout.
- FFmpeg available on `PATH`.
- Existing local or remote workflow-model configuration.
- Existing translator-model configuration when translation uses a separate endpoint.
- MLX Whisper installed for automatic macOS ASR, or local WhisperX dependencies elsewhere.
- Existing TTS credentials or local TTS runtime when `dub` is requested.

Run `doctor --json` before mutation. It validates customized markers, Python syntax, FFmpeg, platform, and the computed ASR default without importing the full application or writing files.

## Secret handling

Keep credentials in the application's existing secret/config mechanism. Never place keys, authorization headers, cookies, or complete configuration in prompts, Skill files, JSON summaries, commits, or issue reports. The CLI recursively redacts fields whose names contain key, token, secret, password, cookie, or authorization.

The Skill package must not contain application config history, model caches, output media, history archives, logs, PID files, browser cookies, or machine-specific absolute paths.
