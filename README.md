<div align="center">

<img src="docs/logo.png" alt="VideoLingo-Freelancer Logo" height="140">

# VideoLingo-Freelancer-Skill

</div>

> 用一句自然语言，让 Codex、Claude Code 或 OpenClaw 操作你已有的 VideoLingo-Freelancer：下载视频、转录、翻译、质检、烧录字幕、配音和归档。
>
> Use one natural-language request to let Codex, Claude Code, or OpenClaw operate your existing VideoLingo-Freelancer workflow: download, transcribe, translate, proofread, render, dub, and archive.

**Language:** [English](#english)｜[简体中文](translations/README.zh.md)｜[Español](translations/README.es.md)｜[Русский](translations/README.ru.md)｜[Français](translations/README.fr.md)｜[Deutsch](translations/README.de.md)｜[Italiano](translations/README.it.md)｜[日本語](translations/README.ja.md)

这是一个遵循 [AgentSkills](https://agentskills.io) 标准的 **AI Agent Skill**，核心是 `SKILL.md + CLI 编排器`。它没有 GUI，也不包含 VideoLingo 应用源码；它负责可靠地操作已经安装和配置好的 VideoLingo-Freelancer 定制版。

This repository is an **AI Agent Skill** built on the [AgentSkills](https://agentskills.io) standard. It contains a `SKILL.md` and a CLI orchestrator—not the VideoLingo application itself and not a GUI.

Application source / 应用源码：[jcxl8/VideoLingo-freelancer](https://github.com/jcxl8/VideoLingo-freelancer)

---

## 中文

### 它能做什么

VideoLingo-Freelancer 把定制版 VideoLingo 的多阶段译制流程封装成稳定命令，让 Agent 不必猜测模块顺序、产物路径或恢复方式。

```text
视频链接 / 本地视频
        │
        ▼
  环境检查与输入准备
        │
        ▼
  ASR 转录 → NLP/语义分句 → 摘要与翻译 → 字幕拆分与时间轴对齐
                                                │
                                                ▼
                                    字幕质检（错误则停止）
                                                │
                         ┌──────────────────────┴──────────────────────┐
                         ▼                                             ▼
                   烧录字幕视频                              生成配音与译制视频
                         └──────────────────────┬──────────────────────┘
                                                ▼
                                          历史归档与 manifest
```

### 核心能力

- **一条命令编排全流程**：`doctor`、`prepare`、`subtitles`、`proofread`、`render`、`dub`、`archive`、`run`。
- **平台自适应 ASR**：macOS 默认使用 MLX Whisper；Linux 和 Windows 默认使用本地 WhisperX；模型均默认为 `large-v3`。
- **字幕质量门禁**：SRT 解析、条目数、时间轴、双语一致性等出现错误时，以退出码 5 阻止烧录和配音。
- **自定义水印**：单次运行指定名称或关闭水印，不修改 VideoLingo-Freelancer 的配置和源码。
- **Agent 友好输出**：`--json` 提供稳定状态，`--dry-run` 在执行前展示仓库、阶段、ASR 和水印选择。
- **失败可恢复**：记录失败阶段，保留已有中间成果，鼓励重跑最小失败命令而不是删除全部输出。
- **敏感信息保护**：状态输出会递归隐藏 key、token、secret、password、cookie 和 authorization 字段。

### 重要边界

本仓库只操作**已经定制好的 VideoLingo-Freelancer**。它不会把普通上游 VideoLingo 自动修改成定制版，也不会安装模型、填写 API 密钥或替你完成应用本体配置。

兼容仓库需要至少包含：

```text
st.py
core/_2_asr.py
core/subtitle_proofread.py
core/utils/model_router.py
scripts/run_regression_checks.py
```

项目基于并感谢 [Huanshere/VideoLingo](https://github.com/Huanshere/VideoLingo)。

### 前置条件

- 已有能正常运行的 VideoLingo-Freelancer 定制版。
- Python 环境、FFmpeg 和应用依赖已安装。
- 翻译、工作流模型和可选 TTS 已在应用侧配置。
- macOS 使用 MLX Whisper；其他系统使用本地 WhisperX。
- 不要把 `config.yaml`、cookies、模型缓存、输出视频或历史目录上传到 Skill 仓库。

### 安装

#### Codex

```bash
git clone https://github.com/jcxl8/videolingo-freelancer-skill.git ~/.agents/skills/videolingo-freelancer
```

Codex CLI、IDE 扩展和 Codex app 都能从个人 Agent Skills 目录发现它。安装后可显式调用 `$videolingo-freelancer`，也可让 Codex 根据任务自动触发。

#### Claude Code

```bash
git clone https://github.com/jcxl8/videolingo-freelancer-skill.git ~/.claude/skills/videolingo-freelancer
```

重新启动 Claude Code，或在新会话中使用 `/videolingo-freelancer`。

#### OpenClaw

```bash
openclaw skills install git:jcxl8/videolingo-freelancer-skill@main
```

也可以将仓库复制到 OpenClaw 工作区的 `skills/` 或 `.agents/skills/`。

### 指定 VideoLingo-Freelancer 位置

推荐设置环境变量：

```bash
export VIDEOLINGO_FREELANCER_HOME="$HOME/VideoLingo-Freelancer"
```

CLI 的仓库发现顺序是：`--repo` → `VIDEOLINGO_FREELANCER_HOME` → 当前目录及父目录 → `~/VideoLingo-Freelancer` → 兼容旧目录 `~/VideoLingo`。不会写死任何用户名。

### 快速开始

先在 Skill 仓库中运行只读检查：

```bash
python scripts/videolingo_freelancer.py --json doctor
python scripts/videolingo_freelancer.py --json status
```

完整流程执行前先 dry-run：

```bash
python scripts/videolingo_freelancer.py --json --dry-run run \
  --input "$HOME/Movies/talk.mp4" \
  --watermark-text "Freelancer Studio"
```

确认计划后执行：

```bash
python scripts/videolingo_freelancer.py --json run \
  --input "$HOME/Movies/talk.mp4" \
  --watermark-text "Freelancer Studio" \
  --dub
```

### 直接对 Agent 说

| 你说的话 | Agent 应执行的流程 |
|---|---|
| `用 VideoLingo-Freelancer 把这个链接译成中文字幕视频：https://…` | 检查 → 下载 → 字幕 → 质检 → 烧录 → 归档 |
| `处理这个本地视频，要双语字幕并配中文音轨` | 准备输入 → 字幕 → 质检 → 双语烧录 → 配音 → 归档 |
| `只生成和检查字幕，先不要烧录` | `subtitles` → `proofread` |
| `用“自由译制”作为水印` | `render/run --watermark-text "自由译制"` |
| `不要水印` | `render/run --no-watermark` |
| `刚才失败了，从安全位置继续` | `status` → 修复原因 → 重跑最小失败命令 |

### CLI 速查

| 命令 | 用途 | 是否写入应用目录 |
|---|---|---|
| `doctor` | 检查仓库、Python、FFmpeg 和平台默认 ASR | 否 |
| `status` | 读取 CLI 与应用任务状态 | 否 |
| `prepare INPUT` | 复制本地视频或下载 URL | 是 |
| `subtitles` | 生成并对齐字幕 | 是 |
| `proofread` | 生成字幕质检报告 | 是 |
| `render` | 烧录字幕，可自定义水印 | 是 |
| `dub` | 生成并合并译制音频 | 是 |
| `archive` | 归档成果并检查 manifest | 是 |
| `run` | 执行受质量门禁保护的完整流程 | 是 |

全局选项 `--repo`、`--json`、`--dry-run` 必须放在子命令前；子命令自己的选项放在子命令后。

### ASR 默认值

```text
macOS (Darwin)  → MLX Whisper    → large-v3
Linux / Windows → local WhisperX → large-v3
```

显式参数优先：

```bash
python scripts/videolingo_freelancer.py --json subtitles \
  --asr-runtime local \
  --whisper-model large-v3
```

选择只在当前 CLI 进程中生效，不重写应用的 `config.yaml`。

### 水印

```bash
# 自定义名称
python scripts/videolingo_freelancer.py --json render \
  --subtitle-mode bilingual_trans_top \
  --watermark-text "Freelancer Studio"

# 关闭水印
python scripts/videolingo_freelancer.py --json render \
  --subtitle-mode translation_only \
  --no-watermark
```

水印文字只在本次渲染进程中覆盖，完成或异常后都会恢复原值。

### 质量门禁与退出码

| 退出码 | 含义 |
|---:|---|
| 0 | 命令完成；仍需检查产物和警告 |
| 2 | 输入、参数或仓库不兼容 |
| 3 | Python、FFmpeg 或运行环境不可用 |
| 4 | 某个译制阶段执行失败 |
| 5 | 字幕质检发现阻断错误，禁止继续烧录或配音 |
| 130 | 用户中断 |

退出码 0 不代表字幕语义一定正确。最终交付仍应检查质检报告、警告和代表性视频帧。

### 上传 GitHub 前

只上传 Skill 自身：

```text
README.md
SKILL.md
agents/
scripts/
references/
tests/
```

不要上传：

- VideoLingo-Freelancer 的 `config.yaml` 或配置历史
- API 密钥、cookies、授权头
- `output/`、`history/`、模型缓存
- 日志、PID、视频、音频和字幕成品
- 带有个人用户名的绝对路径

### 常见问题

**为什么 Skill 说找不到兼容仓库？**

传入 `--repo` 或设置 `VIDEOLINGO_FREELANCER_HOME`。如果缺少定制版标记文件，请不要强行对普通上游仓库运行。

**Mac 上为什么默认 MLX Whisper？**

MLX 可利用 Apple Silicon/Metal。Linux 和 Windows 则默认使用本地 WhisperX；两边都选择 `large-v3`。

**字幕质检返回退出码 5 怎么办？**

阅读 JSON/Markdown 报告，定位时间轴、条目数或双语一致性错误。修复后单独重跑 `proofread`，不要绕过门禁。

**必须使用 Streamlit 吗？**

不需要。Skill 以 CLI 为主；Streamlit 是 VideoLingo-Freelancer 应用本体的可选界面。

**可以用 macOS LaunchAgent 自动启动应用吗？**

可以，但这是应用本体的部署方式，不是 Skill 的必要条件。需要开机或登录后自动启动 VideoLingo-Freelancer / Hy-MT2 服务时，请参考应用仓库的 [macOS LaunchAgent 指南](https://github.com/jcxl8/VideoLingo-freelancer/blob/main/docs/macos-launch-agent.md)。Skill 本身仍然以 CLI 调用为主，不依赖 Streamlit 或 LaunchAgent。

**可以直接操作普通 Huanshere/VideoLingo 吗？**

不可以。本 Skill 依赖定制版模块并会主动拒绝缺少标记文件的仓库。

### 许可证状态

[Huanshere/VideoLingo](https://github.com/Huanshere/VideoLingo) 使用 Apache-2.0。本 Skill 同样采用仓库内 `LICENSE` 所载的 Apache License 2.0。

---

## English

### What it does

VideoLingo-Freelancer turns a customized VideoLingo workflow into a stable command surface for AI coding agents. The agent no longer needs to guess module order, artifact paths, quality gates, or recovery steps.

```text
video URL / local video
        │
        ▼
  environment check + input preparation
        │
        ▼
  ASR → NLP/semantic segmentation → summarize/translate → subtitle timing
                                                               │
                                                               ▼
                                                  proofread quality gate
                                                       │ errors stop
                               ┌───────────────────────┴───────────────────────┐
                               ▼                                               ▼
                       render subtitles                                synthesize dubbing
                               └───────────────────────┬───────────────────────┘
                                                       ▼
                                                archive + manifest
```

### Highlights

- **One guarded workflow:** `doctor`, `prepare`, `subtitles`, `proofread`, `render`, `dub`, `archive`, and `run`.
- **Platform-aware ASR:** MLX Whisper on macOS; local WhisperX on Linux and Windows; both default to `large-v3`.
- **Subtitle quality gate:** parsing, count, timing, and bilingual consistency errors stop rendering and dubbing with exit code 5.
- **Runtime-only watermark:** set a custom name or disable it without changing application source or configuration.
- **Agent-friendly protocol:** stable JSON output and read-only dry-run planning.
- **Recoverable stages:** preserve intermediates, report the failed stage, and rerun the smallest command.
- **Secret redaction:** key, token, secret, password, cookie, and authorization fields are hidden recursively.

### Scope and requirements

This repository operates an **existing customized VideoLingo-Freelancer checkout**. It does not convert ordinary upstream VideoLingo into the customized application, install models, or configure credentials.

The compatible checkout must include:

```text
st.py
core/_2_asr.py
core/subtitle_proofread.py
core/utils/model_router.py
scripts/run_regression_checks.py
```

VideoLingo-Freelancer builds on and acknowledges [Huanshere/VideoLingo](https://github.com/Huanshere/VideoLingo).

Before using this Skill, ensure the customized application already has a working Python environment, FFmpeg, translation/workflow models, and any requested TTS backend.

### Installation

#### Codex

```bash
git clone https://github.com/jcxl8/videolingo-freelancer-skill.git ~/.agents/skills/videolingo-freelancer
```

Invoke it explicitly as `$videolingo-freelancer`, or let Codex match the task to the Skill description.

#### Claude Code

```bash
git clone https://github.com/jcxl8/videolingo-freelancer-skill.git ~/.claude/skills/videolingo-freelancer
```

Start a new Claude Code session and invoke `/videolingo-freelancer`.

#### OpenClaw

```bash
openclaw skills install git:jcxl8/videolingo-freelancer-skill@main
```

Alternatively, place the repository under the OpenClaw workspace `skills/` or `.agents/skills/` directory.

### Locate the customized checkout

For a standard public installation:

```bash
export VIDEOLINGO_FREELANCER_HOME="$HOME/VideoLingo-Freelancer"
```

Discovery order is `--repo`, `VIDEOLINGO_FREELANCER_HOME`, current directory and parents, `~/VideoLingo-Freelancer`, then the legacy `~/VideoLingo`. No username is hardcoded.

### Quick start

Run the read-only checks first:

```bash
python scripts/videolingo_freelancer.py --json doctor
python scripts/videolingo_freelancer.py --json status
```

Preview the full workflow without mutation:

```bash
python scripts/videolingo_freelancer.py --json --dry-run run \
  --input "$HOME/Movies/talk.mp4" \
  --watermark-text "Freelancer Studio"
```

Execute after reviewing the plan:

```bash
python scripts/videolingo_freelancer.py --json run \
  --input "$HOME/Movies/talk.mp4" \
  --watermark-text "Freelancer Studio" \
  --dub
```

### Natural-language requests

| Request | Expected workflow |
|---|---|
| `Translate this link into a Chinese-subtitled video: https://…` | Check → download → subtitles → proofread → render → archive |
| `Process this local video with bilingual subtitles and Chinese dubbing.` | Prepare → subtitles → proofread → bilingual render → dub → archive |
| `Generate and check subtitles only. Do not render yet.` | `subtitles` → `proofread` |
| `Use “Freelancer Studio” as the watermark.` | `render/run --watermark-text "Freelancer Studio"` |
| `Do not add a watermark.` | `render/run --no-watermark` |
| `Resume safely after the previous failure.` | `status` → fix cause → rerun the smallest failed command |

### Command reference

| Command | Purpose | Mutates the application checkout |
|---|---|---|
| `doctor` | Check markers, Python, FFmpeg, and platform ASR default | No |
| `status` | Read CLI and application task state | No |
| `prepare INPUT` | Copy a local video or download a URL | Yes |
| `subtitles` | Generate and align subtitles | Yes |
| `proofread` | Generate subtitle quality reports | Yes |
| `render` | Burn subtitles with optional watermark | Yes |
| `dub` | Synthesize and merge translated audio | Yes |
| `archive` | Archive artifacts and inspect the manifest | Yes |
| `run` | Execute the quality-gated workflow | Yes |

Place global options such as `--repo`, `--json`, and `--dry-run` before the subcommand. Place subcommand-specific options after it.

### ASR defaults

```text
macOS (Darwin)  → MLX Whisper    → large-v3
Linux / Windows → local WhisperX → large-v3
```

Explicit options override automatic selection for the current process only:

```bash
python scripts/videolingo_freelancer.py --json subtitles \
  --asr-runtime local \
  --whisper-model large-v3
```

### Custom watermark

```bash
python scripts/videolingo_freelancer.py --json render \
  --subtitle-mode bilingual_trans_top \
  --watermark-text "Freelancer Studio"

python scripts/videolingo_freelancer.py --json render \
  --subtitle-mode translation_only \
  --no-watermark
```

The override is restored after success or failure and never rewrites application source or `config.yaml`.

### Quality gate and exit codes

| Exit code | Meaning |
|---:|---|
| 0 | Command completed; artifacts and warnings still require inspection |
| 2 | Invalid input, arguments, or incompatible checkout |
| 3 | Python, FFmpeg, or runtime environment unavailable |
| 4 | A workflow stage failed |
| 5 | Subtitle proofread blocked rendering and dubbing |
| 130 | Interrupted by the user |

A zero exit code does not prove semantic subtitle or dubbing quality. Review the proofread report, warnings, and representative rendered frames before delivery.

### GitHub safety checklist

Publish only:

```text
README.md
SKILL.md
agents/
scripts/
references/
tests/
```

Never publish application configuration, credentials, cookies, authorization headers, output/history directories, model caches, logs, PID files, media, subtitle deliverables, or personal absolute paths.

### FAQ

**Why does repository discovery fail?**

Pass `--repo` or set `VIDEOLINGO_FREELANCER_HOME`. Do not force the Skill to run against ordinary upstream VideoLingo when customized marker files are absent.

**Why is MLX Whisper the macOS default?**

MLX uses Apple Silicon and Metal. Linux and Windows default to local WhisperX. Both use `large-v3` unless explicitly overridden.

**What should I do with exit code 5?**

Read the JSON/Markdown proofread report, correct timing/count/bilingual consistency errors, and rerun `proofread`. Do not bypass the gate.

**Does this Skill require Streamlit?**

No. The Skill is CLI-first. Streamlit belongs to the VideoLingo-Freelancer application and remains an optional manual interface.

**Can the application start automatically with macOS LaunchAgent?**

Yes, but that is an application deployment choice, not a Skill requirement. If you want VideoLingo-Freelancer or a Hy-MT2 local service to start after macOS login, see the application repository's [macOS LaunchAgent guide](https://github.com/jcxl8/VideoLingo-freelancer/blob/main/docs/macos-launch-agent.md). The Skill itself remains CLI-first and does not depend on Streamlit or LaunchAgent.

**Can it operate an ordinary Huanshere/VideoLingo checkout?**

No. It depends on customized modules and deliberately rejects a checkout without the required markers.

### License status

[Huanshere/VideoLingo](https://github.com/Huanshere/VideoLingo) is licensed under Apache-2.0. This Skill is also distributed under the Apache License 2.0 in the repository `LICENSE` file.
