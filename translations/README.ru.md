# VideoLingo-Freelancer Skill

[English](../README.md)｜[简体中文](README.zh.md)｜[Español](README.es.md)｜**Русский**｜[Français](README.fr.md)｜[Deutsch](README.de.md)｜[Italiano](README.it.md)｜[日本語](README.ja.md)

Единый Skill для Codex, Claude Code и OpenClaw, управляющий через CLI уже настроенным приложением [VideoLingo-Freelancer](https://github.com/jcxl8/VideoLingo-freelancer).

## Возможности и границы

- Команды `doctor`, `prepare`, `subtitles`, `proofread`, `render`, `dub`, `archive`, `run`.
- MLX Whisper на macOS и WhisperX на Linux/Windows; модель `large-v3`.
- Ошибки проверки субтитров останавливают рендеринг и озвучивание с кодом 5.
- `--watermark-text`, `--no-watermark` и JSON с маскированием секретов.
- Работает только с настроенной пользовательской версией; не устанавливает приложение, модели и ключи и отклоняет обычный upstream VideoLingo.

## Установка

```bash
# Codex
git clone https://github.com/jcxl8/videolingo-freelancer-skill.git ~/.agents/skills/videolingo-freelancer
# Claude Code
git clone https://github.com/jcxl8/videolingo-freelancer-skill.git ~/.claude/skills/videolingo-freelancer
# OpenClaw
openclaw skills install git:jcxl8/videolingo-freelancer-skill@main
```

## Поиск приложения и быстрый старт

```bash
export VIDEOLINGO_FREELANCER_HOME="$HOME/VideoLingo-Freelancer"
python scripts/videolingo_freelancer.py --json doctor
python scripts/videolingo_freelancer.py --json --dry-run run --input "$HOME/Movies/talk.mp4"
python scripts/videolingo_freelancer.py --json run --input "$HOME/Movies/talk.mp4" --watermark-text "Freelancer Studio" --dub
```

Примеры запросов: только создать и проверить субтитры; сделать двуязычные субтитры и озвучку; убрать водяной знак; безопасно продолжить после ошибки.

## Справочник CLI

| Команда | Назначение |
|---|---|
| `doctor` / `status` | Проверка среды и состояния |
| `prepare INPUT` | Копирование видео или загрузка URL |
| `subtitles` / `proofread` | Создание и проверка субтитров |
| `render` / `dub` | Встраивание субтитров или озвучка |
| `archive` / `run` | Архивирование или полный процесс |

## ASR, водяной знак и коды выхода

```text
macOS → MLX Whisper → large-v3
Linux / Windows → WhisperX → large-v3
```

Используйте `--watermark-text "Имя"` или `--no-watermark`. Коды: `0` готово, `2` ввод/репозиторий, `3` среда, `4` этап, `5` блокировка `proofread`, `130` прерывание.

## Безопасность GitHub и FAQ

Не публикуйте конфигурацию, API-ключи, cookies, результаты, историю, модели, журналы или медиа. Для поиска приложения задайте `--repo` или `VIDEOLINGO_FREELANCER_HOME`. При коде 5 исправьте отчёт и повторите `proofread`. Streamlit не требуется. Для автозапуска приложения или Hy-MT2 через macOS LaunchAgent см. [руководство macOS LaunchAgent](https://github.com/jcxl8/VideoLingo-freelancer/blob/main/docs/macos-launch-agent.md).

## LICENSE

Основано на [Huanshere/VideoLingo](https://github.com/Huanshere/VideoLingo), лицензия [Apache License 2.0](../LICENSE).
