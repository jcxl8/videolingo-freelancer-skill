#!/usr/bin/env python3
"""Cross-agent CLI for an existing customized VideoLingo-Freelancer checkout."""

from __future__ import annotations

import argparse
import ast
import importlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.parse
from contextlib import contextmanager
from pathlib import Path
from typing import Mapping


EXIT_OK = 0
EXIT_INPUT = 2
EXIT_ENVIRONMENT = 3
EXIT_EXECUTION = 4
EXIT_PROOFREAD = 5
STATE_RELATIVE_PATH = Path("output/.videolingo_freelancer_cli_status.json")
LEGACY_STATE_RELATIVE_PATH = Path("output/.videolingo_juncai_cli_status.json")
TASK_STATE_RELATIVE_PATH = Path("output/.videolingo_task_status.json")

REQUIRED_MARKERS = (
    "st.py",
    "core/_2_asr.py",
    "core/subtitle_proofread.py",
    "core/utils/model_router.py",
    "scripts/run_regression_checks.py",
)

REDACTED_KEYS = ("key", "token", "secret", "password", "cookie", "authorization")
VIDEO_EXTENSIONS = {".mp4", ".mkv", ".mov", ".webm", ".avi", ".m4v"}
SUBTITLE_MODES = (
    "source_only",
    "translation_only",
    "bilingual_src_top",
    "bilingual_trans_top",
    "single_bilingual_trans_top",
)


class CliError(RuntimeError):
    def __init__(self, message, exit_code=EXIT_EXECUTION, details=None):
        super().__init__(message)
        self.exit_code = int(exit_code)
        self.details = details or {}


class CommandResult:
    def __init__(
        self,
        command,
        status,
        repo,
        stage,
        artifacts=None,
        warnings=None,
        details=None,
    ):
        self.command = command
        self.status = status
        self.repo = str(repo)
        self.stage = stage
        self.artifacts = artifacts or {}
        self.warnings = warnings or []
        self.details = details or {}

    def as_dict(self):
        return {
            "version": 1,
            "command": self.command,
            "status": self.status,
            "repo": self.repo,
            "stage": self.stage,
            "artifacts": self.artifacts,
            "warnings": self.warnings,
            "details": self.details,
        }


class Stage:
    def __init__(self, name, module_name, function_name):
        self.name = name
        self.module_name = module_name
        self.function_name = function_name

    @property
    def qualified_name(self):
        return f"{self.module_name}.{self.function_name}"


SUBTITLE_STAGES = (
    Stage("transcribe", "core._2_asr", "transcribe"),
    Stage("split_nlp", "core._3_1_split_nlp", "split_by_spacy"),
    Stage("split_meaning", "core._3_2_split_meaning", "split_sentences_by_meaning"),
    Stage("summarize", "core._4_1_summarize", "get_summary"),
    Stage("translate", "core._4_2_translate", "translate_all"),
    Stage("split_subtitles", "core._5_split_sub", "split_for_sub_main"),
    Stage("align_timestamps", "core._6_gen_sub", "align_timestamp_main"),
)

DUB_STAGES = (
    Stage("audio_tasks", "core._8_1_audio_task", "gen_audio_task_main"),
    Stage("audio_chunks", "core._8_2_dub_chunks", "gen_dub_chunks"),
    Stage("reference_audio", "core._9_refer_audio", "extract_refer_audio_main"),
    Stage("tts", "core._10_gen_audio", "gen_audio"),
    Stage("merge_audio", "core._11_merge_audio", "merge_full_audio"),
    Stage("merge_dubbed_video", "core._12_dub_to_vid", "merge_video_audio"),
)


def validate_repo(path: Path) -> Path:
    resolved = Path(path).expanduser().resolve()
    missing = [item for item in REQUIRED_MARKERS if not (resolved / item).is_file()]
    if missing:
        raise CliError(
            "Not a customized VideoLingo-Freelancer checkout",
            exit_code=EXIT_INPUT,
            details={"path": str(resolved), "missing": missing},
        )
    return resolved


def _parent_candidates(cwd: Path):
    current = cwd.expanduser().resolve()
    yield current
    yield from current.parents


def discover_repo(explicit, env: Mapping[str, str], cwd: Path, home: Path | None = None) -> Path:
    home = (home or Path.home()).expanduser().resolve()
    candidates = []
    if explicit:
        candidates.append(Path(explicit))
    if env.get("VIDEOLINGO_FREELANCER_HOME"):
        candidates.append(Path(env["VIDEOLINGO_FREELANCER_HOME"]))
    if env.get("VIDEOLINGO_JUNCAI_HOME"):
        candidates.append(Path(env["VIDEOLINGO_JUNCAI_HOME"]))
    candidates.extend(_parent_candidates(Path(cwd)))
    candidates.extend(
        (
            home / "VideoLingo-Freelancer",
            home / "VideoLingo-Juncai",
            home / "VideoLingo",
        )
    )

    attempted = []
    seen = set()
    for candidate in candidates:
        resolved = candidate.expanduser().resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        attempted.append(str(resolved))
        try:
            return validate_repo(resolved)
        except CliError:
            continue
    raise CliError(
        "Customized VideoLingo-Freelancer checkout not found",
        exit_code=EXIT_INPUT,
        details={"attempted": attempted, "required_markers": list(REQUIRED_MARKERS)},
    )


def redact(value):
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            if any(part in str(key).lower() for part in REDACTED_KEYS):
                result[key] = "[REDACTED]"
            else:
                result[key] = redact(item)
        return result
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value


def emit_result(result: CommandResult, json_mode, stdout=sys.stdout, stderr=sys.stderr):
    payload = redact(result.as_dict())
    if json_mode:
        stdout.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
        return
    stdout.write(f"[{payload['status']}] {payload['command']} · {payload['stage']}\n")
    if payload["artifacts"]:
        for name, path in payload["artifacts"].items():
            stdout.write(f"- {name}: {path}\n")
    for warning in payload["warnings"]:
        stderr.write(f"warning: {warning}\n")


def _add_asr_options(parser):
    parser.add_argument(
        "--asr-runtime",
        choices=("auto", "mlx", "local"),
        default="auto",
        help="auto uses MLX on macOS and local WhisperX elsewhere",
    )
    parser.add_argument("--whisper-model", default=None, help="defaults to large-v3")


def _add_render_options(parser):
    parser.add_argument("--subtitle-mode", choices=SUBTITLE_MODES, default="bilingual_trans_top")
    watermark = parser.add_mutually_exclusive_group()
    watermark.add_argument("--watermark-text", default=None)
    watermark.add_argument("--no-watermark", action="store_true")


def build_parser():
    parser = argparse.ArgumentParser(prog="videolingo-freelancer")
    parser.add_argument("--repo", help="customized checkout; overrides discovery")
    parser.add_argument("--json", dest="json_mode", action="store_true", help="emit one JSON object")
    parser.add_argument("--dry-run", action="store_true", help="plan without mutation")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("doctor")
    subparsers.add_parser("status")

    prepare_parser = subparsers.add_parser("prepare")
    prepare_parser.add_argument("input")
    prepare_parser.add_argument("--resolution", default="1080")

    subtitles_parser = subparsers.add_parser("subtitles")
    _add_asr_options(subtitles_parser)

    subparsers.add_parser("proofread")

    render_parser = subparsers.add_parser("render")
    _add_render_options(render_parser)

    subparsers.add_parser("dub")
    subparsers.add_parser("archive")

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--input")
    run_parser.add_argument("--resolution", default="1080")
    run_parser.add_argument("--dub", action="store_true", help="also create dubbed audio/video")
    run_parser.add_argument("--skip-render", action="store_true")
    run_parser.add_argument("--skip-archive", action="store_true")
    _add_asr_options(run_parser)
    _add_render_options(run_parser)
    return parser


def resolve_asr_settings(runtime, model, system=None):
    system = system or platform.system()
    selected_runtime = str(runtime or "auto").strip().lower()
    if selected_runtime == "auto":
        selected_runtime = "mlx" if system == "Darwin" else "local"
    if selected_runtime not in {"mlx", "local"}:
        raise CliError("Unsupported ASR runtime", EXIT_INPUT, {"runtime": selected_runtime})
    selected_model = str(model or "large-v3").strip()
    if not selected_model:
        selected_model = "large-v3"
    return selected_runtime, selected_model


def sanitize_watermark_text(text):
    if text is None:
        return None
    value = str(text).replace("\r", " ").replace("\n", " ").strip()
    if any(ord(character) < 32 for character in value):
        raise CliError("Watermark contains unsupported control characters", EXIT_INPUT)
    replacements = {
        "'": "’",
        ":": "：",
        ",": "，",
        "{": "｛",
        "}": "｝",
        "\\": "＼",
    }
    return "".join(replacements.get(character, character) for character in value)


@contextmanager
def temporary_watermark(module, text):
    original = module.WATERMARK_TEXT
    try:
        module.WATERMARK_TEXT = sanitize_watermark_text(text)
        yield
    finally:
        module.WATERMARK_TEXT = original


@contextmanager
def repository_context(repo: Path):
    original_cwd = Path.cwd()
    original_path = list(sys.path)
    try:
        os.chdir(repo)
        sys.path.insert(0, str(repo))
        yield
    finally:
        os.chdir(original_cwd)
        sys.path[:] = original_path


@contextmanager
def temporary_asr_settings(module, runtime, model):
    """Override config reads in memory for one transcription call."""
    utils = importlib.import_module("core.utils")
    original_module_load = module.load_key
    original_utils_load = utils.load_key

    def override(key):
        if key == "whisper.runtime":
            return runtime
        if key == "whisper.model":
            return model
        return original_module_load(key)

    module.load_key = override
    utils.load_key = override
    touched_backends = []
    try:
        yield
    finally:
        module.load_key = original_module_load
        utils.load_key = original_utils_load
        for backend in touched_backends:
            backend.load_key = original_utils_load
        for name in ("core.asr_backend.mlx_whisper_local", "core.asr_backend.whisperX_local"):
            backend = sys.modules.get(name)
            if backend is not None and getattr(backend, "load_key", None) is override:
                backend.load_key = original_utils_load


def _atomic_write_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(redact(payload), handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temp_name, path)
    finally:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass


def write_state(repo: Path, payload):
    safe = {"version": 1, "updated_at": time.time(), **payload}
    _atomic_write_json(repo / STATE_RELATIVE_PATH, safe)


def run_stages(
    repo: Path,
    stages,
    loader=importlib.import_module,
    state_writer=write_state,
    asr_runtime=None,
    whisper_model=None,
):
    completed = []
    with repository_context(repo):
        for stage in stages:
            state_writer(repo, {"status": "running", "stage": stage.name, "completed": completed})
            try:
                module = loader(stage.module_name)
                function = getattr(module, stage.function_name)
                if stage.qualified_name == "core._2_asr.transcribe" and asr_runtime:
                    with temporary_asr_settings(module, asr_runtime, whisper_model or "large-v3"):
                        function()
                else:
                    function()
            except Exception as exc:
                state_writer(
                    repo,
                    {"status": "failed", "stage": stage.name, "completed": completed, "error": str(exc)},
                )
                raise CliError(
                    f"Stage failed: {stage.name}",
                    EXIT_EXECUTION,
                    {"stage": stage.name, "error": str(exc)},
                ) from exc
            completed.append(stage.name)
    state_writer(repo, {"status": "completed", "stage": completed[-1] if completed else "idle", "completed": completed})
    return completed


def _read_json(path: Path):
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else None
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None


def load_status(repo: Path):
    cli_state = _read_json(repo / STATE_RELATIVE_PATH)
    if cli_state is None:
        cli_state = _read_json(repo / LEGACY_STATE_RELATIVE_PATH)
    task_state = _read_json(repo / TASK_STATE_RELATIVE_PATH)
    active = cli_state or task_state or {}
    return CommandResult(
        "status",
        str(active.get("status") or "idle"),
        repo,
        str(active.get("stage") or active.get("step_label") or "status"),
        details=redact({"cli": cli_state, "videolingo": task_state}),
    )


def doctor(repo: Path, runner=subprocess.run):
    checks = {
        "markers": {item: (repo / item).is_file() for item in REQUIRED_MARKERS},
        "python": sys.version.split()[0],
        "platform": platform.system(),
    }
    invalid_python = []
    for relative in REQUIRED_MARKERS:
        if not relative.endswith(".py"):
            continue
        try:
            ast.parse((repo / relative).read_text(encoding="utf-8"), filename=relative)
        except (OSError, SyntaxError, UnicodeError) as exc:
            invalid_python.append({"path": relative, "error": str(exc)})
    checks["python_syntax"] = {"passed": not invalid_python, "errors": invalid_python}

    ffmpeg = shutil.which("ffmpeg")
    checks["ffmpeg"] = {"path": ffmpeg, "available": bool(ffmpeg)}
    if ffmpeg:
        completed = runner(
            [ffmpeg, "-version"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        checks["ffmpeg"]["returncode"] = completed.returncode
    if invalid_python or not ffmpeg:
        raise CliError("VideoLingo-Freelancer environment check failed", EXIT_ENVIRONMENT, checks)
    runtime, model = resolve_asr_settings("auto", None)
    checks["asr_default"] = {"runtime": runtime, "model": model}
    return CommandResult("doctor", "passed", repo, "doctor", details=checks)


def build_stage_plan(command, args):
    if command == "run":
        stages = ["doctor"]
        if getattr(args, "input", None):
            stages.append("prepare")
        stages.extend(("subtitles", "proofread"))
        if not getattr(args, "skip_render", False):
            stages.append("render")
        if getattr(args, "dub", False):
            stages.append("dub")
        if not getattr(args, "skip_archive", False):
            stages.append("archive")
        return stages
    return [command]


def dry_run(repo: Path, command, args):
    runtime = model = None
    if command in {"subtitles", "run"}:
        runtime, model = resolve_asr_settings(args.asr_runtime, args.whisper_model)
    details = {
        "dry_run": True,
        "stages": build_stage_plan(command, args),
        "asr": {"runtime": runtime, "model": model} if runtime else None,
        "watermark_text": sanitize_watermark_text(getattr(args, "watermark_text", None)),
        "watermark_enabled": False if getattr(args, "no_watermark", False) else None,
    }
    return CommandResult(command, "planned", repo, "dry_run", details=details)


def _unique_destination(path: Path):
    if not path.exists():
        return path
    counter = 2
    while True:
        candidate = path.with_name(f"{path.stem}_v{counter}{path.suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def prepare_input(repo: Path, source, resolution="1080"):
    parsed = urllib.parse.urlparse(str(source))
    with repository_context(repo):
        if parsed.scheme in {"http", "https"}:
            module = importlib.import_module("core._1_ytdlp")
            module.download_video_ytdlp(str(source), save_path="output", resolution=resolution)
            result = module.find_video_files()
            if not result:
                raise CliError("Download completed without a discoverable video", EXIT_EXECUTION)
            return str(Path(result).resolve())
        if parsed.scheme and parsed.scheme != "file":
            raise CliError("Unsupported input scheme", EXIT_INPUT, {"scheme": parsed.scheme})
        input_path = Path(urllib.parse.unquote(parsed.path) if parsed.scheme == "file" else source).expanduser().resolve()
        if not input_path.is_file():
            raise CliError("Input video does not exist", EXIT_INPUT, {"input": str(input_path)})
        if input_path.suffix.lower() not in VIDEO_EXTENSIONS:
            raise CliError("Unsupported video extension", EXIT_INPUT, {"extension": input_path.suffix})
        output_dir = repo / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        destination = _unique_destination(output_dir / input_path.name)
        shutil.copy2(input_path, destination)
        return str(destination.resolve())


def enforce_proofread_gate(report):
    summary = report.get("summary") or {}
    if int(summary.get("error_count") or 0) > 0:
        raise CliError(
            "Subtitle proofread found blocking errors",
            EXIT_PROOFREAD,
            {"summary": summary, "issues": report.get("issues") or []},
        )
    return [item for item in report.get("issues") or [] if item.get("severity") == "warning"]


def run_proofread(repo: Path):
    with repository_context(repo):
        video_module = importlib.import_module("core._7_sub_into_vid")
        proofread_module = importlib.import_module("core.subtitle_proofread")
        paths = video_module.get_default_subtitle_paths()
        report = proofread_module.proofread_subtitle_set(
            paths,
            report_json="output/log/subtitle_proofread_report.json",
            report_md="output/subtitle_proofread_report.md",
        )
    warnings = enforce_proofread_gate(report)
    return CommandResult(
        "proofread",
        "passed_with_warnings" if warnings else "passed",
        repo,
        "proofread",
        artifacts={
            "report_json": str((repo / "output/log/subtitle_proofread_report.json").resolve()),
            "report_markdown": str((repo / "output/subtitle_proofread_report.md").resolve()),
        },
        warnings=warnings,
        details={"summary": report.get("summary") or {}},
    )


def render_video(repo: Path, args):
    with repository_context(repo):
        module = importlib.import_module("core._7_sub_into_vid")
        raw_text = getattr(args, "watermark_text", None)
        text = sanitize_watermark_text(raw_text)
        disabled = bool(getattr(args, "no_watermark", False) or raw_text == "")
        watermark_enabled = False if disabled else (True if text is not None else None)
        if text is None:
            output = module.merge_subtitles_to_video(
                subtitle_mode=args.subtitle_mode,
                watermark_enabled=watermark_enabled,
            )
        else:
            with temporary_watermark(module, text):
                output = module.merge_subtitles_to_video(
                    subtitle_mode=args.subtitle_mode,
                    watermark_enabled=watermark_enabled,
                )
    return CommandResult(
        "render",
        "passed",
        repo,
        "render",
        artifacts={"video": str(Path(output).resolve())},
        details={"watermark_text": text, "watermark_enabled": watermark_enabled},
    )


def run_archive(repo: Path):
    with repository_context(repo):
        module = importlib.import_module("core.utils.onekeycleanup")
        archive_dir = Path(module.cleanup()).resolve()
    manifest = archive_dir / "manifest.json"
    data = _read_json(manifest)
    if data is not None:
        serialized = json.dumps(data, ensure_ascii=False).lower()
        if any(token in serialized for token in ('"api_key"', '"secret"', '"password"', '"token"')):
            raise CliError("Archive manifest may contain a secret", EXIT_EXECUTION, {"manifest": str(manifest)})
    return CommandResult(
        "archive",
        "passed",
        repo,
        "archive",
        artifacts={"archive": str(archive_dir), "manifest": str(manifest)},
    )


def run_subtitles(repo: Path, args):
    runtime, model = resolve_asr_settings(args.asr_runtime, args.whisper_model)
    completed = run_stages(
        repo,
        SUBTITLE_STAGES,
        asr_runtime=runtime,
        whisper_model=model,
    )
    return CommandResult(
        "subtitles",
        "passed",
        repo,
        completed[-1],
        details={"completed": completed, "asr": {"runtime": runtime, "model": model}},
    )


def run_dub(repo: Path):
    completed = run_stages(repo, DUB_STAGES)
    return CommandResult("dub", "passed", repo, completed[-1], details={"completed": completed})


def execute_command(repo: Path, args):
    command = args.command
    if command == "doctor":
        return doctor(repo)
    if command == "status":
        return load_status(repo)
    if args.dry_run:
        return dry_run(repo, command, args)
    if command == "prepare":
        path = prepare_input(repo, args.input, args.resolution)
        return CommandResult("prepare", "passed", repo, "prepare", artifacts={"input_video": path})
    if command == "subtitles":
        return run_subtitles(repo, args)
    if command == "proofread":
        return run_proofread(repo)
    if command == "render":
        return render_video(repo, args)
    if command == "dub":
        return run_dub(repo)
    if command == "archive":
        return run_archive(repo)
    if command == "run":
        doctor(repo)
        artifacts = {}
        warnings = []
        if args.input:
            artifacts["input_video"] = prepare_input(repo, args.input, args.resolution)
        subtitle_result = run_subtitles(repo, args)
        proofread_result = run_proofread(repo)
        artifacts.update(proofread_result.artifacts)
        warnings.extend(proofread_result.warnings)
        if not args.skip_render:
            render_result = render_video(repo, args)
            artifacts.update(render_result.artifacts)
        if args.dub:
            run_dub(repo)
        if not args.skip_archive:
            archive_result = run_archive(repo)
            artifacts.update(archive_result.artifacts)
        return CommandResult(
            "run",
            "passed_with_warnings" if warnings else "passed",
            repo,
            "completed",
            artifacts=artifacts,
            warnings=warnings,
            details={"asr": subtitle_result.details["asr"]},
        )
    raise CliError("Unsupported command", EXIT_INPUT, {"command": command})


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        repo = discover_repo(args.repo, os.environ, Path.cwd())
        result = execute_command(repo, args)
        emit_result(result, args.json_mode)
        return EXIT_OK
    except CliError as exc:
        result = CommandResult(
            args.command,
            "failed",
            args.repo or "",
            (exc.details or {}).get("stage", args.command),
            details={"message": str(exc), **(exc.details or {}), "exit_code": exc.exit_code},
        )
        emit_result(result, args.json_mode)
        return exc.exit_code
    except KeyboardInterrupt:
        result = CommandResult(args.command, "interrupted", args.repo or "", args.command)
        emit_result(result, args.json_mode)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
