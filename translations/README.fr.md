# VideoLingo-Freelancer Skill

[English](../README.md)｜[简体中文](README.zh.md)｜[Español](README.es.md)｜[Русский](README.ru.md)｜**Français**｜[Deutsch](README.de.md)｜[Italiano](README.it.md)｜[日本語](README.ja.md)

Skill unifié pour Codex, Claude Code et OpenClaw, pilotant par CLI une installation déjà configurée de [VideoLingo-Freelancer](https://github.com/jcxl8/VideoLingo-freelancer).

## Fonctions et périmètre

- Orchestre `doctor`, `prepare`, `subtitles`, `proofread`, `render`, `dub`, `archive` et `run`.
- MLX Whisper sur macOS, WhisperX sur Linux/Windows, modèle `large-v3`.
- Les erreurs de contrôle bloquent rendu et doublage avec le code de sortie 5.
- `--watermark-text`, `--no-watermark` et sortie JSON avec secrets masqués.
- Fonctionne uniquement avec la version personnalisée déjà installée ; n’installe ni application, ni modèles, ni clés et refuse VideoLingo upstream non modifié.

## Installation

```bash
# Codex
git clone https://github.com/jcxl8/videolingo-freelancer-skill.git ~/.agents/skills/videolingo-freelancer
# Claude Code
git clone https://github.com/jcxl8/videolingo-freelancer-skill.git ~/.claude/skills/videolingo-freelancer
# OpenClaw
openclaw skills install git:jcxl8/videolingo-freelancer-skill@main
```

## Localiser l’application et démarrage rapide

```bash
export VIDEOLINGO_FREELANCER_HOME="$HOME/VideoLingo-Freelancer"
python scripts/videolingo_freelancer.py --json doctor
python scripts/videolingo_freelancer.py --json --dry-run run --input "$HOME/Movies/talk.mp4"
python scripts/videolingo_freelancer.py --json run --input "$HOME/Movies/talk.mp4" --watermark-text "Freelancer Studio" --dub
```

Exemples de demandes : générer et vérifier uniquement les sous-titres ; créer des sous-titres bilingues avec doublage ; retirer le filigrane ; reprendre après une erreur.

## Référence CLI

| Commande | Usage |
|---|---|
| `doctor` / `status` | Vérifier environnement et état |
| `prepare INPUT` | Copier une vidéo ou télécharger une URL |
| `subtitles` / `proofread` | Générer et contrôler les sous-titres |
| `render` / `dub` | Incruster ou doubler |
| `archive` / `run` | Archiver ou exécuter le flux complet |

## ASR, filigrane et codes de sortie

```text
macOS → MLX Whisper → large-v3
Linux / Windows → WhisperX → large-v3
```

Utilisez `--watermark-text "Nom"` ou `--no-watermark`. Codes : `0` terminé, `2` entrée/dépôt, `3` environnement, `4` étape, `5` blocage `proofread`, `130` interruption.

## Sécurité GitHub et FAQ

Ne publiez pas configuration, clés API, cookies, sorties, historique, modèles, journaux ou médias. Utilisez `--repo` ou `VIDEOLINGO_FREELANCER_HOME` si l’application est introuvable. Avec le code 5, corrigez le rapport puis relancez `proofread`. Streamlit n’est pas requis. Pour démarrer automatiquement l’application ou Hy-MT2 avec macOS LaunchAgent, consultez le [guide macOS LaunchAgent](https://github.com/jcxl8/VideoLingo-freelancer/blob/main/docs/macos-launch-agent.md).

## LICENSE

Basé sur [Huanshere/VideoLingo](https://github.com/Huanshere/VideoLingo), sous [Apache License 2.0](../LICENSE).
