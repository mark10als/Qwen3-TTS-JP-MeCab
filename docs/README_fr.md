[English](README_en.md) | [日本語](../README.md) | [中文](README_zh.md) | [한국어](README_ko.md) | [Русский](README_ru.md) | [Español](README_es.md) | [Italiano](README_it.md) | [Deutsch](README_de.md) | **Français** | [Português](README_pt.md)

# Qwen3-TTS-JP-MeCab

> ⚠️ **Ce dépôt est uniquement pour la langue japonaise.**  
> Il s'agit d'un fork spécialisé en japonais avec prétraitement du texte japonais basé sur MeCab.

---

## Différences avec Qwen3-TTS-JP

| Fonctionnalité | [Qwen3-TTS-JP](https://github.com/hiroki-abe-58/Qwen3-TTS-JP) | **Ce dépôt（Qwen3-TTS-JP-MeCab）** |
|---|---|---|
| Langue cible | Multilingue（UI en 10 langues） | **Japonais uniquement** |
| Prétraitement du texte | Aucun | **Conversion kanji→kana via MeCab + pyopenjtalk-plus** |
| Analyse de l'accent | Aucune | **Affichage des informations d'accent du dictionnaire MeCab** |
| Dictionnaire utilisateur | Aucun | **Enregistrement de noms propres avec lecture et accent** |
| MeCab | Non requis | **Installation séparée requise** |
| Méthode de lancement | venv Python | **Python système（requis pour pyopenjtalk）** |
| Insertion de silence | Aucune | **Insertion de silence après `……` et ponctuation de fin de phrase** |

---

## Fonctionnalités

### Toutes les fonctionnalités de Qwen3-TTS-JP

- **Natif Windows**: Pas de WSL2/Docker, pas de FlashAttention2 requis
- **Custom Voice**: Synthèse vocale avec des locuteurs préréglés
- **Voice Design**: Décrire les caractéristiques vocales en texte pour la synthèse
- **Voice Clone**: Cloner la voix depuis un audio de référence（avec transcription automatique Whisper）
- **Support RTX série 50**: Build nightly PyTorch（cu128）

### Fonctionnalités ajoutées（prétraitement japonais）

- **Conversion automatique kanji→kana**: Conversion en hiragana pour TTS avec MeCab + pyopenjtalk-plus
- **Affichage de l'accent**: Afficher la lecture avec des marqueurs `↑`（montant）`↓`（descendant）— modifiable
- **Dictionnaire utilisateur**: Enregistrement de noms propres dans `user_dict.json` avec lecture et accent corrects
- **Intégration du dictionnaire d'accent**: Détection automatique de `.dic` compilé par [MeCab_accent_tool](https://github.com/mark10als/MeCab_accent_tool)
- **Insertion de silence**: Silence complet après `……` et moitié après `。！？`

---

## Configuration requise

- **Système d'exploitation**: Windows 10/11（environnement natif）
- **GPU**: GPU NVIDIA（compatible CUDA）
  - RTX série 30/40: PyTorch version stable
  - RTX série 50（Blackwell）: PyTorch nightly（cu128）
- **Python**: 3.10 ou supérieur
- **VRAM**: 8 Go ou plus recommandés
- **MeCab**: Installation séparée requise（voir ci-dessous）

---

## Installation

### Étape 1: Installer MeCab（obligatoire, séparé）

MeCab doit être installé en tant qu'application système, indépendamment de l'environnement virtuel.

1. Télécharger et installer depuis:  
   👉 **https://github.com/ikegami-yukino/mecab/releases**  
   （Sélectionner `mecab-64-*.exe`; choisir **UTF-8** pour l'encodage des caractères lors de l'installation）

2. Vérifier l'installation:
   ```cmd
   mecab --version
   ```

3. Chemin d'installation par défaut:
   ```
   C:\Program Files\MeCab\
   C:\Program Files\MeCab\dic\ipadic\   ← répertoire du dictionnaire
   ```

### Étape 2: Cloner le dépôt

```bash
git clone https://github.com/mark10als/Qwen3-TTS-JP-MeCab.git
cd Qwen3-TTS-JP-MeCab
```

### Étape 3: Créer l'environnement virtuel et installer les paquets de base

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
pip install faster-whisper
```

### Étape 4: Installer PyTorch（version CUDA）

```bash
# Pour CUDA 12.x
.venv\Scripts\pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# Pour RTX série 50（sm_120）
.venv\Scripts\pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128
```

### Étape 5: Installer les paquets de prétraitement japonais（dans Python système）

> **Important**: Le lanceur `launch_gui-2.py` utilise Python système.  
> Installer les paquets de prétraitement japonais dans Python système（pas dans venv）.

```cmd
:: Vérifier le chemin Python système
where python

:: Exécuter avec Python système（NE PAS activer venv）
python -m pip install mecab-python3
python -m pip install pyopenjtalk-plus

:: marine nécessite PYTHONUTF8=1 pour éviter les erreurs d'encodage sous Windows
set PYTHONUTF8=1
python -m pip install marine
set PYTHONUTF8=
```

Vérifier l'installation:

```python
python -c "import MeCab; print('MeCab: OK')"
python -c "import pyopenjtalk; print('pyopenjtalk-plus: OK')"
python -c "import marine; print('marine: OK')"
```

### Étape 6: Configurer MeCab_accent_tool（recommandé）

Outil complémentaire pour gérer les informations d'accent des noms propres.

```bash
git clone https://github.com/mark10als/MeCab_accent_tool.git
```

Consultez le [README de MeCab_accent_tool](https://github.com/mark10als/MeCab_accent_tool) pour plus de détails.

---

## Utilisation

### Démarrer l'interface graphique

Double-cliquer sur `launch_gui-2.py`, ou:

```bash
python launch_gui-2.py
```

Le navigateur s'ouvre automatiquement sur `http://127.0.0.1:7860`.

> **Remarque**: Exécuter avec **Python système**, pas avec `.venv\Scripts\python.exe`.  
> pyopenjtalk-plus est installé dans Python système.

### Procédure TTS japonaise

1. Ouvrir l'onglet Voice Clone / Custom Voice / Voice Design
2. Saisir du texte japonais dans "Texte à synthétiser"
3. Lors de la détection du japonais, la case à cocher **"Prétraitement MeCab"** est automatiquement activée et cochée
4. Cliquer sur **"Convertir et analyser"**
   - "Texte converti": Lecture en hiragana pour TTS（modifiable）
   - "Lecture avec marqueurs d'accent": Affiche la lecture avec les marqueurs `↑`/`↓`（modifiable）
5. Modifier le texte si nécessaire
6. Cliquer sur **"Générer l'audio"**

### Insertion de silence

| Symbole | Durée du silence |
|---|---|
| `……`（points de suspension） | Valeur du curseur（secondes） |
| `。` `！` `？` | Valeur du curseur × 0.5（secondes） |

Régler avec le curseur **"Durée du silence"**（0–3 secondes）.

### Dictionnaire utilisateur

Enregistrer des noms propres dans `user_dict.json`:

```json
{
  "伝の心": {
    "reading": "でんのしん",
    "accent_type": 3,
    "note": "Dispositif de communication pour personnes gravement handicapées"
  }
}
```

Valeurs du type d'accent:
- `0`: Plat（heiban）— par exemple, お↑かね
- `1`: Haut initial（atamadaka）— par exemple, あ↓たま
- `N`: Descend après la N-ième more — par exemple, `3` → で↑んの↓しん

---

## Intégration avec MeCab_accent_tool

Lorsqu'un `.dic` est compilé par [MeCab_accent_tool](https://github.com/mark10als/MeCab_accent_tool),  
ce dépôt le détecte et l'utilise automatiquement.

```
MeCab_accent_tool/ → compile → output/mecab_accent.dic
Qwen3-TTS-JP-MeCab/ preprocess_block.py → détecte automatiquement mecab_accent.dic
    → lit le type d'accent depuis le 14e champ des entrées MeCab
```

Placer `mecab_accent.dic` à la racine du projet pour la détection automatique.

---

## Paquets associés

| Paquet | Version | Objectif | Emplacement d'installation |
|---|---|---|---|
| [mecab-python3](https://github.com/SamuraiT/mecab-python3) | 1.0+ | Liaisons MeCab pour Python | Python système |
| [pyopenjtalk-plus](https://github.com/tsukumijima/pyopenjtalk) | 0.4+ | Conversion de lecture + prédiction d'accent | Python système |
| [marine](https://github.com/6gsn/marine) | 0.0.6+ | Prédiction d'accent DNN（précision améliorée） | Python système |
| [gradio](https://github.com/gradio-app/gradio) | 6.0+ | Web UI | venv |
| [torch](https://pytorch.org/) | 2.4+ | Moteur d'inférence | venv |
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | - | Transcription automatique | venv |

---

## Dépannage

| Symptôme | Cause | Solution |
|---|---|---|
| `pyopenjtalk-plus chargement échoué` | Non installé dans Python système | Exécuter `python -m pip install pyopenjtalk-plus` avec Python système |
| Case `Prétraitement MeCab` non affichée | MeCab ou pyopenjtalk non installés | Vérifier les étapes 1 et 5 |
| Erreur DLL `torch_library_impl` | Lancé avec venv Python | Utiliser `launch_gui-2.py`（Python système） |
| `FlashAttention2 cannot be used` | FlashAttention non pris en charge sous Windows | S'assurer que l'option `--no-flash-attn` est définie |
| `SoX could not be found` | SoX non installé | Peut être ignoré（aucun impact sur la fonctionnalité principale） |
| Accent non affiché | mecab_accent.dic manquant | Compiler avec MeCab_accent_tool |

---

## Licence

Ce projet est publié sous la [Apache License 2.0](../LICENSE).

### Logiciels open source utilisés

| Logiciel | Licence | Droits d'auteur |
|---|---|---|
| [Qwen3-TTS](https://github.com/QwenLM/Qwen3-TTS) | Apache License 2.0 | Copyright 2026 Alibaba Cloud |
| [Qwen3-TTS-JP](https://github.com/hiroki-abe-58/Qwen3-TTS-JP) | Apache License 2.0 | Copyright hiroki-abe-58 |
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | MIT License | Copyright SYSTRAN |
| [mecab-python3](https://github.com/SamuraiT/mecab-python3) | BSD License | Copyright SamuraiT |
| [pyopenjtalk-plus](https://github.com/tsukumijima/pyopenjtalk) | MIT License | Copyright tsukumijima |
| [marine](https://github.com/6gsn/marine) | Apache License 2.0 | Copyright 6gsn |

Pour plus de détails, consultez le fichier [NOTICE](../NOTICE).

---

## Avertissement

- L'audio généré est produit automatiquement par un modèle d'IA et peut contenir du contenu inexact
- **Cloner ou utiliser la voix d'une autre personne sans son consentement peut violer les droits à l'image et de publicité**
- Les développeurs n'assument aucune responsabilité pour les dommages résultant de l'utilisation de ce logiciel

---

## Remerciements

- Qwen3-TTS original: [Alibaba Cloud Qwen Team](https://github.com/QwenLM)
- Base du fork Windows: [Qwen3-TTS-JP](https://github.com/hiroki-abe-58/Qwen3-TTS-JP) par hiroki-abe-58
