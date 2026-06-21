from __future__ import annotations

import importlib.util
import io
import json
import os
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = ROOT / "scripts" / "videolingo_freelancer.py"


def load_cli():
    spec = importlib.util.spec_from_file_location("videolingo_freelancer_cli", CLI_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


cli = load_cli()


def make_repo(root: Path) -> Path:
    for relative in cli.REQUIRED_MARKERS:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# marker\n", encoding="utf-8")
    (root / "config.yaml").write_text(
        "target_language: 简体中文\nwatermark_enabled: true\n",
        encoding="utf-8",
    )
    return root


def snapshot_tree(root: Path):
    snapshot = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            stat = path.stat()
            snapshot[str(path.relative_to(root))] = (path.read_bytes(), stat.st_mtime_ns)
    return snapshot


class DiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_explicit_repo_wins_over_environment(self):
        explicit = make_repo(self.root / "explicit")
        environment = make_repo(self.root / "environment")
        found = cli.discover_repo(
            str(explicit),
            {"VIDEOLINGO_FREELANCER_HOME": str(environment)},
            self.root,
            home=self.root / "home",
        )
        self.assertEqual(found, explicit.resolve())

    def test_new_environment_repo_precedes_legacy_environment(self):
        environment = make_repo(self.root / "environment")
        legacy = make_repo(self.root / "legacy-environment")
        found = cli.discover_repo(
            None,
            {
                "VIDEOLINGO_FREELANCER_HOME": str(environment),
                "VIDEOLINGO_JUNCAI_HOME": str(legacy),
            },
            self.root,
            home=self.root / "home",
        )
        self.assertEqual(found, environment.resolve())

    def test_legacy_environment_repo_still_works(self):
        legacy = make_repo(self.root / "legacy-environment")
        found = cli.discover_repo(
            None,
            {"VIDEOLINGO_JUNCAI_HOME": str(legacy)},
            self.root,
            home=self.root / "home",
        )
        self.assertEqual(found, legacy.resolve())

    def test_parent_repo_is_discovered(self):
        repo = make_repo(self.root / "project")
        nested = repo / "work" / "nested"
        nested.mkdir(parents=True)
        found = cli.discover_repo(None, {}, nested, home=self.root / "home")
        self.assertEqual(found, repo.resolve())

    def test_new_public_name_precedes_legacy_home_name(self):
        home = self.root / "home"
        new = make_repo(home / "VideoLingo-Freelancer")
        make_repo(home / "VideoLingo-Juncai")
        make_repo(home / "VideoLingo")
        found = cli.discover_repo(None, {}, self.root / "empty", home=home)
        self.assertEqual(found, new.resolve())

    def test_plain_upstream_checkout_is_rejected(self):
        upstream = self.root / "upstream"
        upstream.mkdir()
        (upstream / "st.py").write_text("", encoding="utf-8")
        with self.assertRaises(cli.CliError) as caught:
            cli.validate_repo(upstream)
        self.assertEqual(caught.exception.exit_code, cli.EXIT_INPUT)
        self.assertIn("core/subtitle_proofread.py", caught.exception.details["missing"])


class JsonProtocolTests(unittest.TestCase):
    def test_all_commands_parse(self):
        for command in (
            "doctor",
            "prepare",
            "subtitles",
            "proofread",
            "render",
            "dub",
            "archive",
            "run",
            "status",
        ):
            args = cli.build_parser().parse_args([command] + (["movie.mp4"] if command == "prepare" else []))
            self.assertEqual(args.command, command)

    def test_render_accepts_custom_watermark(self):
        args = cli.build_parser().parse_args(
            ["--json", "render", "--watermark-text", "俊才译制", "--subtitle-mode", "translation_only"]
        )
        self.assertTrue(args.json_mode)
        self.assertEqual(args.watermark_text, "俊才译制")
        self.assertEqual(args.subtitle_mode, "translation_only")

    def test_result_has_stable_schema(self):
        result = cli.CommandResult(
            command="doctor",
            status="passed",
            repo="/resolved/path",
            stage="doctor",
        )
        self.assertEqual(
            result.as_dict(),
            {
                "version": 1,
                "command": "doctor",
                "status": "passed",
                "repo": "/resolved/path",
                "stage": "doctor",
                "artifacts": {},
                "warnings": [],
                "details": {},
            },
        )

    def test_json_output_is_one_machine_readable_line(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        result = cli.CommandResult("status", "passed", "/repo", "status")
        cli.emit_result(result, True, stdout, stderr)
        parsed = json.loads(stdout.getvalue())
        self.assertEqual(parsed["command"], "status")
        self.assertEqual(stderr.getvalue(), "")

    def test_exit_code_contract(self):
        self.assertEqual(
            (cli.EXIT_OK, cli.EXIT_INPUT, cli.EXIT_ENVIRONMENT, cli.EXIT_EXECUTION, cli.EXIT_PROOFREAD),
            (0, 2, 3, 4, 5),
        )


class ReadOnlyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.repo = make_repo(Path(self.temp.name) / "repo")

    def tearDown(self):
        self.temp.cleanup()

    def test_status_does_not_write(self):
        before = snapshot_tree(self.repo)
        result = cli.load_status(self.repo)
        after = snapshot_tree(self.repo)
        self.assertEqual(before, after)
        self.assertEqual(result.status, "idle")

    def test_new_state_writer_does_not_create_legacy_state(self):
        cli.write_state(self.repo, {"status": "running", "stage": "test"})
        self.assertTrue((self.repo / "output/.videolingo_freelancer_cli_status.json").is_file())
        self.assertFalse((self.repo / "output/.videolingo_juncai_cli_status.json").exists())

    def test_status_reads_legacy_state_when_new_state_is_absent(self):
        legacy = self.repo / "output/.videolingo_juncai_cli_status.json"
        legacy.parent.mkdir(parents=True, exist_ok=True)
        legacy.write_text('{"status":"failed","stage":"legacy"}', encoding="utf-8")
        result = cli.load_status(self.repo)
        self.assertEqual(result.status, "failed")
        self.assertEqual(result.stage, "legacy")

    def test_dry_run_does_not_write(self):
        before = snapshot_tree(self.repo)
        args = cli.build_parser().parse_args(["--dry-run", "run", "--watermark-text", "俊才译制"])
        result = cli.dry_run(self.repo, "run", args)
        after = snapshot_tree(self.repo)
        self.assertEqual(before, after)
        self.assertEqual(result.details["stages"][0], "doctor")
        self.assertIn("proofread", result.details["stages"])


class PipelineTests(unittest.TestCase):
    def test_macos_defaults_to_mlx_whisper(self):
        self.assertEqual(cli.resolve_asr_settings("auto", None, system="Darwin"), ("mlx", "large-v3"))

    def test_non_macos_defaults_to_whisper_large_v3(self):
        self.assertEqual(cli.resolve_asr_settings("auto", None, system="Linux"), ("local", "large-v3"))
        self.assertEqual(cli.resolve_asr_settings("auto", None, system="Windows"), ("local", "large-v3"))

    def test_explicit_asr_runtime_overrides_platform_default(self):
        self.assertEqual(cli.resolve_asr_settings("local", "large-v3", system="Darwin"), ("local", "large-v3"))

    def test_subtitles_parser_exposes_asr_override(self):
        args = cli.build_parser().parse_args(
            ["subtitles", "--asr-runtime", "local", "--whisper-model", "large-v3"]
        )
        self.assertEqual(args.asr_runtime, "local")
        self.assertEqual(args.whisper_model, "large-v3")

    def test_asr_override_is_in_memory_and_restored(self):
        original = lambda key: {"whisper.runtime": "configured", "whisper.model": "configured-model"}.get(key)
        module = types.SimpleNamespace(load_key=original)
        utils = types.SimpleNamespace(load_key=original)
        with patch.object(cli.importlib, "import_module", return_value=utils):
            with cli.temporary_asr_settings(module, "mlx", "large-v3"):
                self.assertEqual(module.load_key("whisper.runtime"), "mlx")
                self.assertEqual(module.load_key("whisper.model"), "large-v3")
            self.assertIs(module.load_key, original)
            self.assertIs(utils.load_key, original)

    def test_subtitle_stage_order(self):
        expected = [
            "core._2_asr.transcribe",
            "core._3_1_split_nlp.split_by_spacy",
            "core._3_2_split_meaning.split_sentences_by_meaning",
            "core._4_1_summarize.get_summary",
            "core._4_2_translate.translate_all",
            "core._5_split_sub.split_for_sub_main",
            "core._6_gen_sub.align_timestamp_main",
        ]
        self.assertEqual([stage.qualified_name for stage in cli.SUBTITLE_STAGES], expected)

    def test_dubbing_stage_order(self):
        expected = [
            "core._8_1_audio_task.gen_audio_task_main",
            "core._8_2_dub_chunks.gen_dub_chunks",
            "core._9_refer_audio.extract_refer_audio_main",
            "core._10_gen_audio.gen_audio",
            "core._11_merge_audio.merge_full_audio",
            "core._12_dub_to_vid.merge_video_audio",
        ]
        self.assertEqual([stage.qualified_name for stage in cli.DUB_STAGES], expected)

    def test_failure_stops_later_stages(self):
        calls = []

        def loader(module_name):
            module = types.SimpleNamespace()

            def first():
                calls.append("first")
                raise RuntimeError("boom")

            def second():
                calls.append("second")

            module.first = first
            module.second = second
            return module

        stages = [cli.Stage("first", "fake", "first"), cli.Stage("second", "fake", "second")]
        with self.assertRaises(cli.CliError) as caught:
            cli.run_stages(Path.cwd(), stages, loader=loader, state_writer=lambda *_: None)
        self.assertEqual(calls, ["first"])
        self.assertEqual(caught.exception.exit_code, cli.EXIT_EXECUTION)
        self.assertEqual(caught.exception.details["stage"], "first")


class WatermarkTests(unittest.TestCase):
    def test_custom_watermark_is_runtime_only(self):
        module = types.SimpleNamespace(WATERMARK_TEXT="AI 词级视频译制")
        with cli.temporary_watermark(module, "俊才译制"):
            self.assertEqual(module.WATERMARK_TEXT, "俊才译制")
        self.assertEqual(module.WATERMARK_TEXT, "AI 词级视频译制")

    def test_watermark_is_restored_after_exception(self):
        module = types.SimpleNamespace(WATERMARK_TEXT="default")
        with self.assertRaises(RuntimeError):
            with cli.temporary_watermark(module, "custom"):
                raise RuntimeError("boom")
        self.assertEqual(module.WATERMARK_TEXT, "default")

    def test_filter_metacharacters_are_made_literal(self):
        self.assertEqual(
            cli.sanitize_watermark_text("A'B:C,D{E}\\F\nG"),
            "A’B：C，D｛E｝＼F G",
        )

    def test_control_character_is_rejected(self):
        with self.assertRaises(cli.CliError):
            cli.sanitize_watermark_text("bad\x00name")


class SafetyHelpersTests(unittest.TestCase):
    def test_url_prepare_returns_downloaded_video_path(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = make_repo(Path(temp) / "repo")
            downloaded = repo / "output" / "downloaded.mp4"

            def download(*_args, **_kwargs):
                downloaded.parent.mkdir(parents=True, exist_ok=True)
                downloaded.write_bytes(b"video")

            module = types.SimpleNamespace(
                download_video_ytdlp=download,
                find_video_files=lambda: "output/downloaded.mp4",
            )
            with patch.object(cli.importlib, "import_module", return_value=module):
                result = cli.prepare_input(repo, "https://example.test/video", "1080")
            self.assertEqual(result, str(downloaded.resolve()))

    def test_recursive_redaction(self):
        value = {
            "api_key": "secret",
            "nested": {"Authorization": "Bearer" + " secret", "model": "safe"},
            "items": [{"cookie": "secret"}],
        }
        redacted = cli.redact(value)
        self.assertEqual(redacted["api_key"], "[REDACTED]")
        self.assertEqual(redacted["nested"]["Authorization"], "[REDACTED]")
        self.assertEqual(redacted["nested"]["model"], "safe")

    def test_proofread_errors_block_pipeline(self):
        report = {
            "status": "issues_found",
            "summary": {"error_count": 1, "warning_count": 2},
            "issues": [{"severity": "error", "type": "timestamp_overlap"}],
        }
        with self.assertRaises(cli.CliError) as caught:
            cli.enforce_proofread_gate(report)
        self.assertEqual(caught.exception.exit_code, cli.EXIT_PROOFREAD)

    def test_proofread_warnings_are_returned(self):
        report = {
            "status": "issues_found",
            "summary": {"error_count": 0, "warning_count": 1},
            "issues": [{"severity": "warning", "type": "translation_cps"}],
        }
        warnings = cli.enforce_proofread_gate(report)
        self.assertEqual(warnings[0]["type"], "translation_cps")


if __name__ == "__main__":
    unittest.main()
