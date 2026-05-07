[English](README_en.md) | [日本語](../README.md) | [中文](README_zh.md) | [한국어](README_ko.md) | [Русский](README_ru.md) | [Español](README_es.md) | [Italiano](README_it.md) | **Deutsch** | [Français](README_fr.md) | [Português](README_pt.md)

# Qwen3-TTS-JP-MeCab

> ⚠️ **Dieses Repository ist nur für die japanische Sprache.**  
> Dies ist ein auf Japanisch spezialisierter Fork mit MeCab-basierter japanischer Textvorverarbeitung.

---

## Unterschiede zu Qwen3-TTS-JP

| Funktion | [Qwen3-TTS-JP](https://github.com/hiroki-abe-58/Qwen3-TTS-JP) | **Dieses Repository（Qwen3-TTS-JP-MeCab）** |
|---|---|---|
| Zielsprache | Mehrsprachig（10-Sprachen-UI） | **Nur Japanisch** |
| Textvorverarbeitung | Keine | **Kanji→Kana-Konvertierung über MeCab + pyopenjtalk-plus** |
| Akzentanalyse | Keine | **Akzentinformationen aus dem MeCab-Wörterbuch anzeigen** |
| Benutzerwörterbuch | Keines | **Eigennamen mit Lesung und Akzent registrieren** |
| MeCab | Nicht erforderlich | **Separate Installation erforderlich** |
| Startmethode | venv Python | **System-Python（für pyopenjtalk erforderlich）** |
| Stille-Einfügung | Keine | **Stille nach `……` und Satzendzeichen einfügen** |

---

## Funktionen

### Alle Funktionen von Qwen3-TTS-JP

- **Windows-nativ**: Kein WSL2/Docker, kein FlashAttention2 erforderlich
- **Custom Voice**: Sprachsynthese mit voreingestellten Sprechern
- **Voice Design**: Sprachmerkmale in Text beschreiben für die Synthese
- **Voice Clone**: Stimme aus Referenzaudio klonen（mit automatischer Whisper-Transkription）
- **RTX 50er-Serie Unterstützung**: PyTorch Nightly-Build（cu128）

### Hinzugefügte Funktionen（japanische Vorverarbeitung）

- **Automatische Kanji→Kana-Konvertierung**: Konvertiert mit MeCab + pyopenjtalk-plus in Hiragana für TTS
- **Akzentanzeige**: Lesung mit `↑`（steigend）`↓`（fallend）Markierungen anzeigen — bearbeitbar
- **Benutzerwörterbuch**: Eigennamen in `user_dict.json` mit korrekter Lesung und Akzent registrieren
- **Akzentwörterbuch-Integration**: Automatische Erkennung von `.dic`, kompiliert durch [MeCab_accent_tool](https://github.com/daibo0501/MeCab_accent_tool)
- **Stille-Einfügung**: Vollständige Stille nach `……` und halbe Dauer nach `。！？`

---

## Systemanforderungen

- **Betriebssystem**: Windows 10/11（native Umgebung）
- **GPU**: NVIDIA GPU（CUDA-kompatibel）
  - RTX 30/40er-Serie: Stabile PyTorch-Version
  - RTX 50er-Serie（Blackwell）: PyTorch Nightly（cu128）
- **Python**: 3.10 oder höher
- **VRAM**: 8 GB oder mehr empfohlen
- **MeCab**: Separate Installation erforderlich（siehe unten）

---

## Installation

### Schritt 1: MeCab installieren（erforderlich, separat）

MeCab muss als systemweite Anwendung, unabhängig von der virtuellen Umgebung, installiert werden.

1. Herunterladen und installieren von:  
   👉 **https://github.com/ikegami-yukino/mecab/releases**  
   （Wählen Sie `mecab-64-*.exe`; wählen Sie **UTF-8** für die Zeichenkodierung bei der Installation）

2. Installation überprüfen:
   ```cmd
   mecab --version
   ```

3. Standard-Installationspfad:
   ```
   C:\Program Files\MeCab\
   C:\Program Files\MeCab\dic\ipadic\   ← Wörterbuchverzeichnis
   ```

### Schritt 2: Repository klonen

```bash
git clone https://github.com/daibo0501/Qwen3-TTS-JP-MeCab.git
cd Qwen3-TTS-JP-MeCab
```

### Schritt 3: Virtuelle Umgebung erstellen und Basispakete installieren

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
pip install faster-whisper
```

### Schritt 4: PyTorch（CUDA-Version）installieren

```bash
# Für CUDA 12.x
.venv\Scripts\pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# Für RTX 50er-Serie（sm_120）
.venv\Scripts\pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128
```

### Schritt 5: Japanische Vorverarbeitungspakete installieren（in System-Python）

> **Wichtig**: Der Launcher `launch_gui-2.py` verwendet System-Python.  
> Installieren Sie japanische Vorverarbeitungspakete in System-Python（nicht in venv）.

```cmd
:: System-Python-Pfad überprüfen
where python

:: Mit System-Python ausführen（venv NICHT aktivieren）
python -m pip install mecab-python3
python -m pip install pyopenjtalk-plus

:: marine benötigt PYTHONUTF8=1 zur Vermeidung von Kodierungsfehlern unter Windows
set PYTHONUTF8=1
python -m pip install marine
set PYTHONUTF8=
```

Installation überprüfen:

```python
python -c "import MeCab; print('MeCab: OK')"
python -c "import pyopenjtalk; print('pyopenjtalk-plus: OK')"
python -c "import marine; print('marine: OK')"
```

### Schritt 6: MeCab_accent_tool einrichten（empfohlen）

Begleitwerkzeug zur Verwaltung von Akzentinformationen für Eigennamen.

```bash
git clone https://github.com/daibo0501/MeCab_accent_tool.git
```

Details finden Sie in der [README von MeCab_accent_tool](https://github.com/daibo0501/MeCab_accent_tool).

---

## Verwendung

### GUI starten

Doppelklicken Sie auf `launch_gui-2.py`, oder:

```bash
python launch_gui-2.py
```

Der Browser öffnet sich automatisch unter `http://127.0.0.1:7860`.

> **Hinweis**: Mit **System-Python** ausführen, nicht mit `.venv\Scripts\python.exe`.  
> pyopenjtalk-plus ist in System-Python installiert.

### Japanische TTS-Prozedur

1. Öffnen Sie den Tab Voice Clone / Custom Voice / Voice Design
2. Geben Sie japanischen Text in "Zu synthetisierender Text" ein
3. Bei Erkennung von Japanisch wird das Kontrollkästchen **"MeCab-Vorverarbeitung"** automatisch aktiviert und angehakt
4. Klicken Sie auf **"Konvertieren und analysieren"**
   - "Konvertierter Text": Hiragana-Lesung für TTS（bearbeitbar）
   - "Lesung mit Akzentmarkierungen": Zeigt die Lesung mit `↑`/`↓`-Markierungen（bearbeitbar）
5. Text bei Bedarf bearbeiten
6. Klicken Sie auf **"Audio generieren"**

### Stille-Einfügung

| Symbol | Stille-Dauer |
|---|---|
| `……`（Auslassungspunkte） | Schiebereglerwert（Sekunden） |
| `。` `！` `？` | Schiebereglerwert × 0.5（Sekunden） |

Mit dem Schieberegler **"Stille-Dauer"**（0–3 Sekunden）einstellen.

### Benutzerwörterbuch

Eigennamen in `user_dict.json` registrieren:

```json
{
  "伝の心": {
    "reading": "でんのしん",
    "accent_type": 3,
    "note": "Kommunikationsgerät für schwer behinderte Personen"
  }
}
```

Akzenttyp-Werte:
- `0`: Flach（heiban）— z.B. お↑かね
- `1`: Hoch-erster（atamadaka）— z.B. あ↓たま
- `N`: Fällt nach der N-ten Mora — z.B. `3` → で↑んの↓しん

---

## Integration mit MeCab_accent_tool

Wenn eine `.dic`-Datei von [MeCab_accent_tool](https://github.com/daibo0501/MeCab_accent_tool) kompiliert wird,  
erkennt und verwendet dieses Repository sie automatisch.

```
MeCab_accent_tool/ → kompiliert → output/mecab_accent.dic
Qwen3-TTS-JP-MeCab/ preprocess_block.py → erkennt mecab_accent.dic automatisch
    → liest den Akzenttyp aus dem 14. Feld der MeCab-Einträge
```

Platzieren Sie `mecab_accent.dic` im Projektstammverzeichnis für automatische Erkennung.

---

## Verwandte Pakete

| Paket | Version | Zweck | Installationsort |
|---|---|---|---|
| [mecab-python3](https://github.com/SamuraiT/mecab-python3) | 1.0+ | MeCab Python-Bindungen | System-Python |
| [pyopenjtalk-plus](https://github.com/tsukumijima/pyopenjtalk) | 0.4+ | Lesungskonvertierung + Akzentvorhersage | System-Python |
| [marine](https://github.com/6gsn/marine) | 0.0.6+ | DNN-Akzentvorhersage（verbesserte Genauigkeit） | System-Python |
| [gradio](https://github.com/gradio-app/gradio) | 6.0+ | Web UI | venv |
| [torch](https://pytorch.org/) | 2.4+ | Inferenz-Engine | venv |
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | - | Automatische Transkription | venv |

---

## Fehlerbehebung

| Symptom | Ursache | Lösung |
|---|---|---|
| `pyopenjtalk-plus Laden fehlgeschlagen` | Nicht in System-Python installiert | `python -m pip install pyopenjtalk-plus` mit System-Python ausführen |
| Kontrollkästchen `MeCab-Vorverarbeitung` nicht angezeigt | MeCab oder pyopenjtalk nicht installiert | Schritte 1 und 5 überprüfen |
| DLL-Fehler `torch_library_impl` | Mit venv-Python gestartet | `launch_gui-2.py`（System-Python）verwenden |
| `FlashAttention2 cannot be used` | FlashAttention nicht unter Windows unterstützt | Sicherstellen, dass die Option `--no-flash-attn` gesetzt ist |
| `SoX could not be found` | SoX nicht installiert | Kann ignoriert werden（keine Auswirkung auf Kernfunktionalität） |
| Akzent nicht angezeigt | mecab_accent.dic fehlt | Mit MeCab_accent_tool kompilieren |

---

## Lizenz

Dieses Projekt wird unter der [Apache License 2.0](../LICENSE) veröffentlicht.

### Verwendete Open-Source-Software

| Software | Lizenz | Urheberrecht |
|---|---|---|
| [Qwen3-TTS](https://github.com/QwenLM/Qwen3-TTS) | Apache License 2.0 | Copyright 2026 Alibaba Cloud |
| [Qwen3-TTS-JP](https://github.com/hiroki-abe-58/Qwen3-TTS-JP) | Apache License 2.0 | Copyright hiroki-abe-58 |
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | MIT License | Copyright SYSTRAN |
| [mecab-python3](https://github.com/SamuraiT/mecab-python3) | BSD License | Copyright SamuraiT |
| [pyopenjtalk-plus](https://github.com/tsukumijima/pyopenjtalk) | MIT License | Copyright tsukumijima |
| [marine](https://github.com/6gsn/marine) | Apache License 2.0 | Copyright 6gsn |

Einzelheiten finden Sie in der [NOTICE](../NOTICE)-Datei.

---

## Haftungsausschluss

- Generiertes Audio wird automatisch von einem KI-Modell erzeugt und kann ungenaue Inhalte enthalten
- **Das Klonen oder Verwenden der Stimme einer anderen Person ohne deren Zustimmung kann Persönlichkeits- und Publizitätsrechte verletzen**
- Die Entwickler übernehmen keine Haftung für Schäden, die durch die Nutzung dieser Software entstehen

---

## Danksagungen

- Original Qwen3-TTS: [Alibaba Cloud Qwen Team](https://github.com/QwenLM)
- Windows-Fork-Basis: [Qwen3-TTS-JP](https://github.com/hiroki-abe-58/Qwen3-TTS-JP) von hiroki-abe-58
