# Workflow

## Command order

Run global flags before the subcommand:

```bash
python "$CLI" --repo /path/to/VideoLingo-Freelancer --json --dry-run run --input /path/to/video.mp4
python "$CLI" --repo /path/to/VideoLingo-Freelancer --json run --input /path/to/video.mp4
```

`run` performs `doctor`, optional `prepare`, `subtitles`, `proofread`, `render`, optional `dub`, and `archive`. Use `--skip-render` or `--skip-archive` only when the user requests that boundary. Add `--dub` when a dubbed track and dubbed video are required.

## Subtitle stages

The CLI calls the customized checkout in this order:

1. `core._2_asr.transcribe`
2. `core._3_1_split_nlp.split_by_spacy`
3. `core._3_2_split_meaning.split_sentences_by_meaning`
4. `core._4_1_summarize.get_summary`
5. `core._4_2_translate.translate_all`
6. `core._5_split_sub.split_for_sub_main`
7. `core._6_gen_sub.align_timestamp_main`

Automatic ASR resolves to `mlx` with model `large-v3` on macOS. It resolves to `local` WhisperX with model `large-v3` on Linux and Windows. Override with:

```bash
python "$CLI" --json subtitles --asr-runtime local --whisper-model large-v3
```

The override is in memory for that process. It does not rewrite application configuration.

## Quality gate

Always run `proofread` after subtitle generation. Blocking errors include malformed SRT, unequal variant counts, invalid or overlapping timestamps, empty text, mismatched bilingual text, and mismatched bilingual timing. Exit code 5 prevents render and dubbing.

Warnings such as suspicious ASR text, fragments, or excessive reading speed do not stop automatically. Include their count, type, timestamp, source, and translation in the user-facing summary.

## Rendering and watermark

Select one subtitle mode: `source_only`, `translation_only`, `bilingual_src_top`, `bilingual_trans_top`, or `single_bilingual_trans_top`.

```bash
python "$CLI" --json render --subtitle-mode bilingual_trans_top --watermark-text "Freelancer Studio"
python "$CLI" --json render --subtitle-mode translation_only --no-watermark
```

The watermark override exists only during the render call. Unsafe ASS/FFmpeg punctuation is converted to visually equivalent full-width punctuation. Application source and configuration remain unchanged.

## Resume

Run `status --json`, inspect the last failed stage, correct the reported cause, then invoke the smallest relevant command. Do not delete the output directory as a generic retry strategy. If the input fingerprint or source video changed, start a new workflow instead of trusting old intermediates.
