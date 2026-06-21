# Artifacts and acceptance

## Subtitle artifacts

The customized checkout derives the exact basename from the input video, language pair, and model settings. Expect four canonical SRT variants in its output directory:

- Source-only: `*_src.srt`
- Translation-only: `*_trans.srt`
- Source above translation: `*_src_trans.srt`
- Translation above source: `*_trans_src.srt`

The proofread command writes a machine-readable JSON report under `output/log/` and a human-readable Markdown report under `output/`.

## Video and audio artifacts

`render` returns the exact rendered video path in `artifacts.video`. `dub` creates TTS chunks, a merged translated track, and the final dubbed video through the customized application's existing naming rules. Do not infer filenames when the JSON result provides them.

`archive` returns `artifacts.archive` and `artifacts.manifest`. The customized application may move active output files into the history directory during this step, so prefer the returned archive paths after completion.

## Acceptance checklist

Before reporting success:

1. Confirm the command exited with code 0.
2. Confirm the returned artifact paths exist.
3. Confirm proofread reports zero blocking errors.
4. Report all remaining warnings.
5. For rendered video, verify a representative frame or user-provided visual acceptance when available.
6. For dubbed output, verify that the audio stream exists and duration is plausible relative to the source.
7. Confirm the archive manifest contains no secret-bearing fields.

A successful process exit does not prove semantic subtitle or dubbing quality. Preserve that distinction in the final report.
