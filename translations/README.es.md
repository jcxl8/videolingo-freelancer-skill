# VideoLingo-Freelancer Skill

[English](../README.md)｜[简体中文](README.zh.md)｜**Español**｜[Русский](README.ru.md)｜[Français](README.fr.md)｜[Deutsch](README.de.md)｜[Italiano](README.it.md)｜[日本語](README.ja.md)

Skill unificado para Codex, Claude Code y OpenClaw que controla mediante CLI una instalación ya configurada de [VideoLingo-Freelancer](https://github.com/jcxl8/VideoLingo-freelancer).

## Funciones y alcance

- Orquesta `doctor`, `prepare`, `subtitles`, `proofread`, `render`, `dub`, `archive` y `run`.
- MLX Whisper en macOS y WhisperX en Linux/Windows; ambos usan `large-v3`.
- El control de calidad detiene renderizado y doblaje con el código de salida 5.
- Admite `--watermark-text` y `--no-watermark`; la salida JSON oculta secretos.
- Solo opera la versión personalizada; no instala la aplicación, modelos ni credenciales y rechaza VideoLingo upstream sin modificar.

## Instalación

```bash
# Codex
git clone https://github.com/jcxl8/videolingo-freelancer-skill.git ~/.agents/skills/videolingo-freelancer
# Claude Code
git clone https://github.com/jcxl8/videolingo-freelancer-skill.git ~/.claude/skills/videolingo-freelancer
# OpenClaw
openclaw skills install git:jcxl8/videolingo-freelancer-skill@main
```

## Localizar la aplicación e inicio rápido

```bash
export VIDEOLINGO_FREELANCER_HOME="$HOME/VideoLingo-Freelancer"
python scripts/videolingo_freelancer.py --json doctor
python scripts/videolingo_freelancer.py --json --dry-run run --input "$HOME/Movies/talk.mp4"
python scripts/videolingo_freelancer.py --json run --input "$HOME/Movies/talk.mp4" --watermark-text "Freelancer Studio" --dub
```

Peticiones naturales: «solo genera y revisa subtítulos», «subtítulos bilingües con doblaje», «sin marca de agua» o «continúa de forma segura».

## Referencia CLI

| Comando | Uso |
|---|---|
| `doctor` / `status` | Comprobaciones de entorno y estado |
| `prepare INPUT` | Copiar un vídeo o descargar una URL |
| `subtitles` / `proofread` | Generar y validar subtítulos |
| `render` / `dub` | Incrustar subtítulos o crear doblaje |
| `archive` / `run` | Archivar o ejecutar el flujo completo |

## ASR, marca de agua y códigos de salida

```text
macOS → MLX Whisper → large-v3
Linux / Windows → WhisperX → large-v3
```

Use `--watermark-text "Nombre"` o `--no-watermark`. Códigos: `0` completado, `2` entrada/repositorio, `3` entorno, `4` etapa fallida, `5` bloqueo de `proofread`, `130` interrupción.

## Seguridad de GitHub y FAQ

No publique configuración, claves API, cookies, salidas, historial, modelos, registros ni medios. Si no encuentra la aplicación, use `--repo` o `VIDEOLINGO_FREELANCER_HOME`. Con código 5, corrija el informe y repita `proofread`; no omita el control. Streamlit no es obligatorio. Para iniciar automáticamente la aplicación o Hy-MT2 con macOS LaunchAgent, consulte la [guía macOS LaunchAgent](https://github.com/jcxl8/VideoLingo-freelancer/blob/main/docs/macos-launch-agent.md).

## LICENSE

Basado en [Huanshere/VideoLingo](https://github.com/Huanshere/VideoLingo), bajo [Apache License 2.0](../LICENSE).
