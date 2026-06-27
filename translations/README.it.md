# VideoLingo-Freelancer Skill

[English](../README.md)｜[简体中文](README.zh.md)｜[Español](README.es.md)｜[Русский](README.ru.md)｜[Français](README.fr.md)｜[Deutsch](README.de.md)｜**Italiano**｜[日本語](README.ja.md)

Skill unificato per Codex, Claude Code e OpenClaw che controlla tramite CLI un’applicazione [VideoLingo-Freelancer](https://github.com/jcxl8/VideoLingo-freelancer) già configurata.

## Funzioni e ambito

- Orchestra `doctor`, `prepare`, `subtitles`, `proofread`, `render`, `dub`, `archive` e `run`.
- MLX Whisper su macOS, WhisperX su Linux/Windows, modello `large-v3`.
- Gli errori del controllo sottotitoli bloccano rendering e doppiaggio con codice di uscita 5.
- Supporta `--watermark-text`, `--no-watermark` e JSON con segreti mascherati.
- Opera solo sulla versione personalizzata installata; non installa applicazione, modelli o chiavi e rifiuta VideoLingo upstream non modificato.

## Installazione

```bash
# Codex
git clone https://github.com/jcxl8/videolingo-freelancer-skill.git ~/.agents/skills/videolingo-freelancer
# Claude Code
git clone https://github.com/jcxl8/videolingo-freelancer-skill.git ~/.claude/skills/videolingo-freelancer
# OpenClaw
openclaw skills install git:jcxl8/videolingo-freelancer-skill@main
```

## Individuare l’applicazione e avvio rapido

```bash
export VIDEOLINGO_FREELANCER_HOME="$HOME/VideoLingo-Freelancer"
python scripts/videolingo_freelancer.py --json doctor
python scripts/videolingo_freelancer.py --json --dry-run run --input "$HOME/Movies/talk.mp4"
python scripts/videolingo_freelancer.py --json run --input "$HOME/Movies/talk.mp4" --watermark-text "Freelancer Studio" --dub
```

Esempi di richieste: genera e controlla solo i sottotitoli; sottotitoli bilingui con doppiaggio; nessuna filigrana; continua in sicurezza dopo un errore.

## Riferimento CLI

| Comando | Uso |
|---|---|
| `doctor` / `status` | Controllo ambiente e stato |
| `prepare INPUT` | Copiare un video o scaricare un URL |
| `subtitles` / `proofread` | Generare e verificare sottotitoli |
| `render` / `dub` | Incorporare sottotitoli o doppiare |
| `archive` / `run` | Archiviare o eseguire il flusso completo |

## ASR, filigrana e codici di uscita

```text
macOS → MLX Whisper → large-v3
Linux / Windows → WhisperX → large-v3
```

Usare `--watermark-text "Nome"` o `--no-watermark`. Codici: `0` completato, `2` input/repository, `3` ambiente, `4` fase, `5` blocco `proofread`, `130` interruzione.

## Sicurezza GitHub e FAQ

Non pubblicare configurazione, chiavi API, cookies, output, cronologia, modelli, log o media. Usare `--repo` o `VIDEOLINGO_FREELANCER_HOME` se l’applicazione non viene trovata. Con codice 5 correggere il rapporto e ripetere `proofread`. Streamlit non è necessario. Per avviare automaticamente l’applicazione o Hy-MT2 con macOS LaunchAgent, vedere la [guida macOS LaunchAgent](https://github.com/jcxl8/VideoLingo-freelancer/blob/main/docs/macos-launch-agent.md).

## LICENSE

Basato su [Huanshere/VideoLingo](https://github.com/Huanshere/VideoLingo), con [Apache License 2.0](../LICENSE).
