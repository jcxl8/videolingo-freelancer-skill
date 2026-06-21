# VideoLingo-Freelancer Skill

[English](../README.md)｜[简体中文](README.zh.md)｜[Español](README.es.md)｜[Русский](README.ru.md)｜[Français](README.fr.md)｜[Deutsch](README.de.md)｜[Italiano](README.it.md)｜**日本語**

Codex、Claude Code、OpenClaw から、設定済みの [VideoLingo-Freelancer アプリ](https://github.com/jcxl8/VideoLingo-freelancer)を CLI で操作する統合 Skill です。

## 機能と対象範囲

- `doctor`、`prepare`、`subtitles`、`proofread`、`render`、`dub`、`archive`、`run` を編成します。
- macOS は MLX Whisper、Linux/Windows は WhisperX、モデルは `large-v3` です。
- 字幕品質エラー時は終了コード 5 でレンダリングと吹き替えを停止します。
- `--watermark-text`、`--no-watermark`、秘密情報を隠す JSON 出力に対応します。
- インストール済みカスタム版のみを操作し、アプリ、モデル、API キーは導入しません。通常の上流 VideoLingo は拒否します。

## インストール

```bash
# Codex
git clone https://github.com/jcxl8/videolingo-freelancer-skill.git ~/.agents/skills/videolingo-freelancer
# Claude Code
git clone https://github.com/jcxl8/videolingo-freelancer-skill.git ~/.claude/skills/videolingo-freelancer
# OpenClaw
openclaw skills install git:jcxl8/videolingo-freelancer-skill@main
```

## アプリの検出とクイックスタート

```bash
export VIDEOLINGO_FREELANCER_HOME="$HOME/VideoLingo-Freelancer"
python scripts/videolingo_freelancer.py --json doctor
python scripts/videolingo_freelancer.py --json --dry-run run --input "$HOME/Movies/talk.mp4"
python scripts/videolingo_freelancer.py --json run --input "$HOME/Movies/talk.mp4" --watermark-text "Freelancer Studio" --dub
```

自然言語の例：字幕だけ生成して確認、二言語字幕と吹き替え、透かしなし、失敗地点から安全に再開。

## CLI リファレンス

| コマンド | 用途 |
|---|---|
| `doctor` / `status` | 環境と状態の確認 |
| `prepare INPUT` | 動画コピーまたは URL ダウンロード |
| `subtitles` / `proofread` | 字幕生成と品質確認 |
| `render` / `dub` | 字幕焼き込みまたは吹き替え |
| `archive` / `run` | 成果物保存または全工程実行 |

## ASR、透かし、終了コード

```text
macOS → MLX Whisper → large-v3
Linux / Windows → WhisperX → large-v3
```

`--watermark-text "名前"` または `--no-watermark` を使用します。コード：`0` 完了、`2` 入力/リポジトリ、`3` 環境、`4` 工程、`5` `proofread` ブロック、`130` 中断。

## GitHub の安全性と FAQ

設定、API キー、cookies、出力、履歴、モデル、ログ、メディアを公開しないでください。アプリが見つからない場合は `--repo` または `VIDEOLINGO_FREELANCER_HOME` を指定します。コード 5 では報告を修正して `proofread` を再実行します。Streamlit は不要です。

## LICENSE

[Huanshere/VideoLingo](https://github.com/Huanshere/VideoLingo) を基盤とし、[Apache License 2.0](../LICENSE) を使用します。
