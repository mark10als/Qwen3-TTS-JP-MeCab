# Qwen3-TTS-JP-MeCab

**English** | [日本語](../README.md) | [中文](README_zh.md) | [한국어](README_ko.md) | [Русский](README_ru.md) | [Español](README_es.md) | [Italiano](README_it.md) | [Deutsch](README_de.md) | [Français](README_fr.md) | [Português](README_pt.md)

> ⚠️ **This repository is for Japanese language only.**  
> This is a Japanese-specialized fork with MeCab-based Japanese text preprocessing.

---

## Differences from Qwen3-TTS-JP

| Feature | [Qwen3-TTS-JP](https://github.com/hiroki-abe-58/Qwen3-TTS-JP) | **This repo (Qwen3-TTS-JP-MeCab)** |
|---|---|---|
| Target language | Multilingual (10-language UI) | **Japanese only** |
| Text preprocessing | None | **Kanji → kana conversion via MeCab + pyopenjtalk-plus** |
| Accent analysis | None | **Accent info display from MeCab dictionary** |
| User dictionary | None | **Register proper nouns with reading and accent** |
| MeCab | Not required | **Separate installation required** |
| Launch method | venv Python | **System Python (required for pyopenjtalk)** |
| Silence insertion | None | **Insert silence after `……` and sentence-end punctuation** |

---

## Features

### All features from Qwen3-TTS-JP

- **Windows-native**: No WSL2/Docker, no FlashAttention2 required
- **Custom Voice**: Speech synthesis with preset speakers
- **Voice Design**: Describe voice characteristics in text
- **Voice Clone**: Clone voice from reference audio (with Whisper auto-transcription)
- **RTX 50 series support**: PyTorch nightly build (cu128)

### Added features (Japanese preprocessing)

- **Kanji → Kana conversion**: Converts to hiragana for TTS using MeCab + pyopenjtalk-plus
- **Accent display**: View reading with `↑` (rising) `↓` (falling) markers — editable
- **User dictionary**: Register proper nouns in `user_dict.json` with correct reading and accent
- **Accent dictionary integration**: Auto-detects `.dic` compiled by [MeCab_accent_tool](https://github.com/mark10als/MeCab_accent_tool)
- **Silence insertion**: Insert silence after `……` (full duration) and `。！？` (half duration)

---

## System Requirements

- **OS**: Windows 10/11 (native environment)
- **GPU**: NVIDIA GPU (CUDA compatible)
  - RTX 30/40 series: Stable PyTorch
  - RTX 50 series (Blackwell): PyTorch nightly (cu128)
- **Python**: 3.10 or higher
- **VRAM**: 8GB or more recommended
- **MeCab**: Separate installation required (see below)

---

## Installation

### Step 1: Install MeCab (required, separate)

MeCab must be installed as a system-wide application, independent of the virtual environment.

1. Download and install from:  
   👉 **https://github.com/ikegami-yukino/mecab/releases**  
   (Select `mecab-64-*.exe`; choose **UTF-8** for character encoding during installation)

2. Verify installation:
   ```cmd
   mecab --version
   ```

3. Default installation path:
   ```
   C:\Program Files\MeCab\
   C:\Program Files\MeCab\dic\ipadic\   ← dictionary directory
   ```

### Step 2: Clone the repository

```bash
git clone https://github.com/mark10als/Qwen3-TTS-JP-MeCab.git
cd Qwen3-TTS-JP-MeCab
```

### Step 3: Create virtual environment and install base packages

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
pip install faster-whisper
```

### Step 4: Install PyTorch (CUDA version)

```bash
# For CUDA 12.x
.venv\Scripts\pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# For RTX 50 series (sm_120)
.venv\Scripts\pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128
```

### Step 5: Install Japanese preprocessing packages (in System Python)

> **Important**: The launcher `launch_gui-2.py` uses system Python.  
> Install Japanese preprocessing packages in system Python (not in the venv).

```cmd
:: Check system Python path
where python

:: Run with system Python (do NOT activate venv)
python -m pip install mecab-python3
python -m pip install pyopenjtalk-plus

:: marine requires PYTHONUTF8=1 to avoid encoding errors on Windows
set PYTHONUTF8=1
python -m pip install marine
set PYTHONUTF8=
```

Verify installation:

```python
python -c "import MeCab; print('MeCab: OK')"
python -c "import pyopenjtalk; print('pyopenjtalk-plus: OK')"
python -c "import marine; print('marine: OK')"
```

### Step 6: Set up MeCab_accent_tool (recommended)

A companion tool for managing accent information for proper nouns.

```bash
git clone https://github.com/mark10als/MeCab_accent_tool.git
```

See [MeCab_accent_tool README](https://github.com/mark10als/MeCab_accent_tool) for details.

---

## Usage

### Starting the GUI

Double-click `launch_gui-2.py`, or:

```bash
python launch_gui-2.py
```

Browser opens automatically at `http://127.0.0.1:7860`.

> **Note**: Run with **system Python**, not `.venv\Scripts\python.exe`.  
> pyopenjtalk-plus is installed in system Python.

### Japanese TTS procedure

1. Open Voice Clone / Custom Voice / Voice Design tab
2. Enter Japanese text in "Text to Synthesize"
3. When Japanese is detected, the **"MeCab preprocessing"** checkbox is automatically enabled and checked
4. Click **"Convert & Analyze"**
   - "Converted text": Hiragana reading for TTS (editable)
   - "Reading with accent marks": Shows reading with `↑`/`↓` markers (editable)
5. Edit text if necessary
6. Click **"Generate Audio"**

### Silence insertion

| Symbol | Silence duration |
|---|---|
| `……` (ellipsis) | Slider value (seconds) |
| `。` `！` `？` | Slider value × 0.5 (seconds) |

Adjust with the **"Silence duration"** slider (0–3 seconds).

### User dictionary

Register proper nouns in `user_dict.json`:

```json
{
  "伝の心": {
    "reading": "でんのしん",
    "accent_type": 3,
    "note": "Communication device for severely disabled persons"
  }
}
```

Accent type values:
- `0`: Flat (heiban) — e.g., お↑かね
- `1`: Head-high (atamadaka) — e.g., あ↓たま
- `N`: Falls after N-th mora — e.g., `3` → で↑んの↓しん

---

## Integration with MeCab_accent_tool

When a `.dic` file is compiled by [MeCab_accent_tool](https://github.com/mark10als/MeCab_accent_tool),  
this repository automatically detects and uses it.

```
MeCab_accent_tool/ → compile → output/mecab_accent.dic
Qwen3-TTS-JP-MeCab/ preprocess_block.py → auto-detects mecab_accent.dic
    → reads accent type from 14th field of MeCab entries
```

Place `mecab_accent.dic` in the project root for automatic detection.

---

## Related Packages

| Package | Version | Purpose | Install location |
|---|---|---|---|
| [mecab-python3](https://github.com/SamuraiT/mecab-python3) | 1.0+ | MeCab Python bindings | System Python |
| [pyopenjtalk-plus](https://github.com/tsukumijima/pyopenjtalk) | 0.4+ | Reading conversion + accent prediction | System Python |
| [marine](https://github.com/6gsn/marine) | 0.0.6+ | DNN accent prediction (improved accuracy) | System Python |
| [gradio](https://github.com/gradio-app/gradio) | 6.0+ | Web UI | venv |
| [torch](https://pytorch.org/) | 2.4+ | Inference engine | venv |
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | - | Auto-transcription | venv |

---

## Troubleshooting

| Symptom | Cause | Solution |
|---|---|---|
| `pyopenjtalk-plus load failed` | Not installed in system Python | Run `python -m pip install pyopenjtalk-plus` with system Python |
| MeCab preprocessing checkbox not shown | MeCab or pyopenjtalk not installed | Check steps 1 and 5 |
| `torch_library_impl` DLL error | Launched with venv Python | Use `launch_gui-2.py` (system Python) |
| `FlashAttention2 cannot be used` | FlashAttention not supported on Windows | Ensure `--no-flash-attn` option is set |
| `SoX could not be found` | SoX not installed | Can be ignored (no impact on core functionality) |
| Accent not displayed | mecab_accent.dic missing | Compile with MeCab_accent_tool |

---

## License

This project is released under the [Apache License 2.0](../LICENSE).

### Open Source Software Used

| Software | License | Copyright |
|---|---|---|
| [Qwen3-TTS](https://github.com/QwenLM/Qwen3-TTS) | Apache License 2.0 | Copyright 2026 Alibaba Cloud |
| [Qwen3-TTS-JP](https://github.com/hiroki-abe-58/Qwen3-TTS-JP) | Apache License 2.0 | Copyright hiroki-abe-58 |
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | MIT License | Copyright SYSTRAN |
| [mecab-python3](https://github.com/SamuraiT/mecab-python3) | BSD License | Copyright SamuraiT |
| [pyopenjtalk-plus](https://github.com/tsukumijima/pyopenjtalk) | MIT License | Copyright tsukumijima |
| [marine](https://github.com/6gsn/marine) | Apache License 2.0 | Copyright 6gsn |

See the [NOTICE](../NOTICE) file for details.

---

## Disclaimer

- Generated audio is produced automatically by an AI model and may contain inaccurate content
- **Cloning or using another person's voice without consent may violate portrait rights and publicity rights**
- The developers assume no liability for any damages arising from the use of this software

---

## Acknowledgments

- Original Qwen3-TTS: [Alibaba Cloud Qwen Team](https://github.com/QwenLM)
- Windows fork base: [Qwen3-TTS-JP](https://github.com/hiroki-abe-58/Qwen3-TTS-JP) by hiroki-abe-58
