# VideoLingo-Freelancer Skill

[English](../README.md)｜**简体中文**｜[Español](README.es.md)｜[Русский](README.ru.md)｜[Français](README.fr.md)｜[Deutsch](README.de.md)｜[Italiano](README.it.md)｜[日本語](README.ja.md)

用于 Codex、Claude Code 和 OpenClaw 的统一 Agent Skill，通过 CLI 操作已经安装并配置好的 [VideoLingo-Freelancer 应用](https://github.com/jcxl8/VideoLingo-freelancer)。

## 功能与边界

- 编排 `doctor`、`prepare`、`subtitles`、`proofread`、`render`、`dub`、`archive` 和 `run`。
- macOS 默认使用 MLX Whisper；Linux/Windows 默认使用 WhisperX；模型均为 `large-v3`。
- 字幕质检失败时以退出码 5 阻止烧录或配音。
- 支持 `--watermark-text` 自定义水印及 `--no-watermark`。
- JSON 输出隐藏密钥、token、cookies 和授权信息。
- 只操作定制版，不安装应用、模型或 API 密钥，也拒绝普通上游 VideoLingo。

## 安装

```bash
# Codex
git clone https://github.com/jcxl8/videolingo-freelancer-skill.git ~/.agents/skills/videolingo-freelancer
# Claude Code
git clone https://github.com/jcxl8/videolingo-freelancer-skill.git ~/.claude/skills/videolingo-freelancer
# OpenClaw
openclaw skills install git:jcxl8/videolingo-freelancer-skill@main
```

## 定位应用与快速开始

```bash
export VIDEOLINGO_FREELANCER_HOME="$HOME/VideoLingo-Freelancer"
python scripts/videolingo_freelancer.py --json doctor
python scripts/videolingo_freelancer.py --json --dry-run run --input "$HOME/Movies/talk.mp4"
python scripts/videolingo_freelancer.py --json run --input "$HOME/Movies/talk.mp4" --watermark-text "Freelancer Studio" --dub
```

自然语言示例：要求 Agent“只生成并检查字幕”“生成双语字幕并配音”“不要水印”或“从失败步骤安全继续”。

## CLI 命令

| 命令 | 用途 |
|---|---|
| `doctor` / `status` | 只读环境和状态检查 |
| `prepare INPUT` | 复制本地视频或下载 URL |
| `subtitles` / `proofread` | 生成字幕并执行质量门禁 |
| `render` / `dub` | 烧录字幕或合成配音 |
| `archive` / `run` | 归档成果或执行完整流程 |

## ASR、水印与退出码

```text
macOS → MLX Whisper → large-v3
Linux / Windows → WhisperX → large-v3
```

`--watermark-text "名称"` 自定义水印；`--no-watermark` 关闭水印。退出码：`0` 完成、`2` 参数/仓库错误、`3` 环境错误、`4` 阶段失败、`5` 质检阻断、`130` 用户中断。

## GitHub 安全与 FAQ

不要上传应用配置、API 密钥、cookies、输出/历史目录、模型缓存、日志或媒体文件。找不到应用时使用 `--repo` 或 `VIDEOLINGO_FREELANCER_HOME`；退出码 5 时修复报告问题后重跑 `proofread`，不要绕过门禁。Skill 不需要 Streamlit。需要 macOS LaunchAgent 自动启动应用或 Hy-MT2 服务时，请看应用仓库的 [macOS LaunchAgent 指南](https://github.com/jcxl8/VideoLingo-freelancer/blob/main/docs/macos-launch-agent.md)。

## 许可证

基于 [Huanshere/VideoLingo](https://github.com/Huanshere/VideoLingo)，采用 [Apache License 2.0](../LICENSE)。
