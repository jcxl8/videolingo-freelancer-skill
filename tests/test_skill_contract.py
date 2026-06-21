from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"


class SkillContractTests(unittest.TestCase):
    def test_readme_starts_with_shared_logo(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        logo = ROOT / "docs" / "logo.png"

        self.assertTrue(logo.is_file())
        self.assertTrue(readme.startswith('<div align="center">\n\n<img src="docs/logo.png"'))
        self.assertLess(readme.index('docs/logo.png'), readme.index("# VideoLingo-Freelancer"))
        self.assertIn('alt="VideoLingo-Freelancer Logo"', readme)
        self.assertIn('height="140"', readme)

    def test_readme_is_bilingual_and_accurate(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        required = (
            "# VideoLingo-Freelancer",
            "## 中文",
            "## English",
            "~/.agents/skills/videolingo-freelancer",
            "~/.claude/skills/videolingo-freelancer",
            "openclaw skills install",
            "scripts/videolingo_freelancer.py",
            "MLX Whisper",
            "WhisperX",
            "large-v3",
            "--watermark-text",
            "exit code 5",
            "Huanshere/VideoLingo",
            "ordinary upstream VideoLingo",
        )
        for item in required:
            self.assertIn(item, readme)
        self.assertNotIn("/" + "Users" + "/" + "zheng", readme)
        self.assertNotRegex(readme, r"sk-[A-Za-z0-9]{12,}")
        self.assertNotIn("img.shields.io", readme)
        self.assertNotIn("xiaohu-video-md", readme)

    def test_readme_uses_published_repository_urls(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertNotIn("OWNER/REPO", readme)
        self.assertIn(
            "https://github.com/jcxl8/videolingo-freelancer-skill.git",
            readme,
        )
        self.assertIn(
            "git:jcxl8/videolingo-freelancer-skill@main",
            readme,
        )
        self.assertIn(
            "https://github.com/jcxl8/VideoLingo-freelancer",
            readme,
        )

    def test_complete_localized_readmes_are_published(self):
        root_readme = (ROOT / "README.md").read_text(encoding="utf-8")
        languages = ("zh", "es", "ru", "fr", "de", "it", "ja")
        required = (
            "VideoLingo-Freelancer",
            "https://github.com/jcxl8/videolingo-freelancer-skill.git",
            "https://github.com/jcxl8/VideoLingo-freelancer",
            "Codex",
            "Claude Code",
            "OpenClaw",
            "doctor",
            "proofread",
            "large-v3",
            "--watermark-text",
            "LICENSE",
        )

        for code in languages:
            relative = f"translations/README.{code}.md"
            self.assertIn(relative, root_readme)
            page = ROOT / relative
            self.assertTrue(page.is_file(), relative)
            text = page.read_text(encoding="utf-8")
            for item in required:
                with self.subTest(language=code, item=item):
                    self.assertIn(item, text)

    def test_frontmatter_is_portable(self):
        text = SKILL.read_text(encoding="utf-8")
        frontmatter = text.split("---", 2)[1]
        keys = [line.split(":", 1)[0].strip() for line in frontmatter.splitlines() if ":" in line]
        self.assertEqual(keys, ["name", "description"])
        self.assertIn("name: videolingo-freelancer", frontmatter)
        self.assertRegex(frontmatter, r"description:\s*[\"']?Use when")

    def test_skill_contains_safety_and_workflow_contract(self):
        text = SKILL.read_text(encoding="utf-8")
        for required in (
            "doctor",
            "--dry-run",
            "proofread",
            "--watermark-text",
            "exit code 5",
            "ordinary upstream",
        ):
            self.assertIn(required, text)

    def test_every_markdown_reference_exists(self):
        text = SKILL.read_text(encoding="utf-8")
        links = re.findall(r"\[[^\]]+\]\(([^)]+\.md)\)", text)
        self.assertGreaterEqual(len(links), 4)
        for relative in links:
            self.assertTrue((ROOT / relative).is_file(), relative)

    def test_package_contains_no_private_or_sensitive_payload(self):
        forbidden = (
            re.compile("/" + "Users" + "/" + "zheng"),
            re.compile(r"sk-[A-Za-z0-9]{12,}"),
            re.compile(r"Bearer\s+[A-Za-z0-9._-]+", re.I),
            re.compile(r"BEGIN (?:RSA |OPENSSH )?PRIVATE KEY"),
        )
        forbidden_names = {"config_history.json", "_model_cache", "history", "output"}
        for path in ROOT.rglob("*"):
            if path.is_dir():
                self.assertNotIn(path.name, forbidden_names)
                continue
            self.assertLess(path.stat().st_size, 1024 * 1024, str(path))
            if path.suffix.lower() in {".md", ".py", ".yaml", ".yml", ".json", ".txt", ".srt"}:
                text = path.read_text(encoding="utf-8")
                for pattern in forbidden:
                    self.assertIsNone(pattern.search(text), f"{pattern.pattern} in {path}")

    def test_legacy_juncai_names_are_confined_to_compatibility_surface(self):
        allowed = {
            "scripts/videolingo_freelancer.py",
            "references/configuration.md",
            "tests/test_cli.py",
            "tests/test_skill_contract.py",
        }
        needles = ("videolingo-juncai", "VideoLingo-Juncai", "VIDEOLINGO_JUNCAI")
        for path in ROOT.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".md", ".py", ".yaml", ".yml"}:
                continue
            text = path.read_text(encoding="utf-8")
            if any(needle in text for needle in needles):
                self.assertIn(str(path.relative_to(ROOT)), allowed)


if __name__ == "__main__":
    unittest.main()
