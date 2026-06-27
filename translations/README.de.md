# VideoLingo-Freelancer Skill

[English](../README.md)｜[简体中文](README.zh.md)｜[Español](README.es.md)｜[Русский](README.ru.md)｜[Français](README.fr.md)｜**Deutsch**｜[Italiano](README.it.md)｜[日本語](README.ja.md)

Ein einheitlicher Skill für Codex, Claude Code und OpenClaw, der eine bereits konfigurierte [VideoLingo-Freelancer-Anwendung](https://github.com/jcxl8/VideoLingo-freelancer) per CLI steuert.

## Funktionen und Grenzen

- Orchestriert `doctor`, `prepare`, `subtitles`, `proofread`, `render`, `dub`, `archive` und `run`.
- MLX Whisper unter macOS, WhisperX unter Linux/Windows, jeweils `large-v3`.
- Fehler der Untertitelprüfung stoppen Rendering und Synchronisation mit Exit-Code 5.
- Unterstützt `--watermark-text`, `--no-watermark` und JSON mit geschwärzten Geheimnissen.
- Arbeitet nur mit der installierten angepassten Version; installiert weder Anwendung noch Modelle oder Schlüssel und lehnt unverändertes Upstream-VideoLingo ab.

## Installation

```bash
# Codex
git clone https://github.com/jcxl8/videolingo-freelancer-skill.git ~/.agents/skills/videolingo-freelancer
# Claude Code
git clone https://github.com/jcxl8/videolingo-freelancer-skill.git ~/.claude/skills/videolingo-freelancer
# OpenClaw
openclaw skills install git:jcxl8/videolingo-freelancer-skill@main
```

## Anwendung finden und Schnellstart

```bash
export VIDEOLINGO_FREELANCER_HOME="$HOME/VideoLingo-Freelancer"
python scripts/videolingo_freelancer.py --json doctor
python scripts/videolingo_freelancer.py --json --dry-run run --input "$HOME/Movies/talk.mp4"
python scripts/videolingo_freelancer.py --json run --input "$HOME/Movies/talk.mp4" --watermark-text "Freelancer Studio" --dub
```

Beispielanfragen: nur Untertitel erzeugen und prüfen; zweisprachige Untertitel mit Synchronisation; kein Wasserzeichen; nach einem Fehler sicher fortsetzen.

## CLI-Referenz

| Befehl | Zweck |
|---|---|
| `doctor` / `status` | Umgebung und Status prüfen |
| `prepare INPUT` | Video kopieren oder URL laden |
| `subtitles` / `proofread` | Untertitel erzeugen und prüfen |
| `render` / `dub` | Untertitel einbrennen oder synchronisieren |
| `archive` / `run` | Archivieren oder vollständigen Ablauf ausführen |

## ASR, Wasserzeichen und Exit-Codes

```text
macOS → MLX Whisper → large-v3
Linux / Windows → WhisperX → large-v3
```

Verwenden Sie `--watermark-text "Name"` oder `--no-watermark`. Codes: `0` fertig, `2` Eingabe/Repository, `3` Umgebung, `4` Stufe, `5` `proofread`-Sperre, `130` Abbruch.

## GitHub-Sicherheit und FAQ

Veröffentlichen Sie keine Konfiguration, API-Schlüssel, Cookies, Ausgaben, Verläufe, Modelle, Protokolle oder Medien. Nutzen Sie `--repo` oder `VIDEOLINGO_FREELANCER_HOME`, wenn die Anwendung nicht gefunden wird. Bei Code 5 Bericht korrigieren und `proofread` erneut ausführen. Streamlit ist nicht erforderlich. Für den automatischen Start der Anwendung oder von Hy-MT2 mit macOS LaunchAgent siehe die [macOS LaunchAgent-Anleitung](https://github.com/jcxl8/VideoLingo-freelancer/blob/main/docs/macos-launch-agent.md).

## LICENSE

Basierend auf [Huanshere/VideoLingo](https://github.com/Huanshere/VideoLingo), lizenziert unter [Apache License 2.0](../LICENSE).
