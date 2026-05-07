[English](README_en.md) | [日本語](../README.md) | [中文](README_zh.md) | [한국어](README_ko.md) | [Русский](README_ru.md) | [Español](README_es.md) | **Italiano** | [Deutsch](README_de.md) | [Français](README_fr.md) | [Português](README_pt.md)

# Qwen3-TTS-JP-MeCab

> ⚠️ **Questo repository è solo per la lingua giapponese.**  
> È un fork specializzato in giapponese con preprocessamento del testo giapponese basato su MeCab.

---

## Differenze da Qwen3-TTS-JP

| Funzione | [Qwen3-TTS-JP](https://github.com/hiroki-abe-58/Qwen3-TTS-JP) | **Questo repository（Qwen3-TTS-JP-MeCab）** |
|---|---|---|
| Lingua target | Multilingue（UI in 10 lingue） | **Solo giapponese** |
| Preprocessamento testo | Nessuno | **Conversione kanji→kana tramite MeCab + pyopenjtalk-plus** |
| Analisi accento | Nessuna | **Visualizzazione informazioni accento dal dizionario MeCab** |
| Dizionario utente | Nessuno | **Registrazione di nomi propri con lettura e accento** |
| MeCab | Non richiesto | **Installazione separata richiesta** |
| Metodo di avvio | venv Python | **Python di sistema（richiesto per pyopenjtalk）** |
| Inserimento silenzio | Nessuno | **Inserimento silenzio dopo `……` e punteggiatura finale** |

---

## Funzionalità

### Tutte le funzionalità da Qwen3-TTS-JP

- **Nativo Windows**: Nessun WSL2/Docker, nessun FlashAttention2
- **Custom Voice**: Sintesi vocale con speaker preimpostati
- **Voice Design**: Descrivere le caratteristiche vocali in testo per la sintesi
- **Voice Clone**: Clonare la voce da audio di riferimento（con trascrizione automatica Whisper）
- **Supporto RTX serie 50**: Build nightly PyTorch（cu128）

### Funzionalità aggiunte（preprocessamento giapponese）

- **Conversione automatica kanji→kana**: Converte in hiragana per TTS usando MeCab + pyopenjtalk-plus
- **Visualizzazione accento**: Visualizza la lettura con marcatori `↑`（ascendente）`↓`（discendente）— modificabile
- **Dizionario utente**: Registrazione di nomi propri in `user_dict.json` con lettura e accento corretti
- **Integrazione dizionario accento**: Rilevamento automatico di `.dic` compilato da [MeCab_accent_tool](https://github.com/daibo0501/MeCab_accent_tool)
- **Inserimento silenzio**: Silenzio completo dopo `……` e metà dopo `。！？`

---

## Requisiti di sistema

- **SO**: Windows 10/11（ambiente nativo）
- **GPU**: GPU NVIDIA（compatibile CUDA）
  - RTX serie 30/40: PyTorch versione stabile
  - RTX serie 50（Blackwell）: PyTorch nightly（cu128）
- **Python**: 3.10 o superiore
- **VRAM**: 8 GB o più raccomandati
- **MeCab**: Installazione separata richiesta（vedere sotto）

---

## Installazione

### Passo 1: Installare MeCab（obbligatorio, separato）

MeCab deve essere installato come applicazione di sistema, indipendente dall'ambiente virtuale.

1. Scaricare e installare da:  
   👉 **https://github.com/ikegami-yukino/mecab/releases**  
   （Selezionare `mecab-64-*.exe`; scegliere **UTF-8** per la codifica dei caratteri durante l'installazione）

2. Verificare l'installazione:
   ```cmd
   mecab --version
   ```

3. Percorso di installazione predefinito:
   ```
   C:\Program Files\MeCab\
   C:\Program Files\MeCab\dic\ipadic\   ← directory del dizionario
   ```

### Passo 2: Clonare il repository

```bash
git clone https://github.com/daibo0501/Qwen3-TTS-JP-MeCab.git
cd Qwen3-TTS-JP-MeCab
```

### Passo 3: Creare l'ambiente virtuale e installare i pacchetti base

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
pip install faster-whisper
```

### Passo 4: Installare PyTorch（versione CUDA）

```bash
# Per CUDA 12.x
.venv\Scripts\pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# Per RTX serie 50（sm_120）
.venv\Scripts\pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128
```

### Passo 5: Installare i pacchetti di preprocessamento giapponese（in Python di sistema）

> **Importante**: Il launcher `launch_gui-2.py` usa Python di sistema.  
> Installare i pacchetti di preprocessamento giapponese in Python di sistema（non nel venv）.

```cmd
:: Verificare il percorso di Python di sistema
where python

:: Eseguire con Python di sistema（NON attivare venv）
python -m pip install mecab-python3
python -m pip install pyopenjtalk-plus

:: marine richiede PYTHONUTF8=1 per evitare errori di codifica su Windows
set PYTHONUTF8=1
python -m pip install marine
set PYTHONUTF8=
```

Verificare l'installazione:

```python
python -c "import MeCab; print('MeCab: OK')"
python -c "import pyopenjtalk; print('pyopenjtalk-plus: OK')"
python -c "import marine; print('marine: OK')"
```

### Passo 6: Configurare MeCab_accent_tool（raccomandato）

Strumento complementare per la gestione delle informazioni sull'accento dei nomi propri.

```bash
git clone https://github.com/daibo0501/MeCab_accent_tool.git
```

Per i dettagli, consultare il [README di MeCab_accent_tool](https://github.com/daibo0501/MeCab_accent_tool).

---

## Utilizzo

### Avviare la GUI

Fare doppio clic su `launch_gui-2.py`, o:

```bash
python launch_gui-2.py
```

Il browser si apre automaticamente su `http://127.0.0.1:7860`.

> **Nota**: Eseguire con **Python di sistema**, non con `.venv\Scripts\python.exe`.  
> pyopenjtalk-plus è installato in Python di sistema.

### Procedura TTS giapponese

1. Aprire la scheda Voice Clone / Custom Voice / Voice Design
2. Inserire testo giapponese in "Testo da sintetizzare"
3. Al rilevamento del giapponese, la casella **"Preprocessamento MeCab"** viene abilitata e selezionata automaticamente
4. Fare clic su **"Converti e analizza"**
   - "Testo convertito": Lettura in hiragana per TTS（modificabile）
   - "Lettura con marcatori accento": Mostra la lettura con marcatori `↑`/`↓`（modificabile）
5. Modificare il testo se necessario
6. Fare clic su **"Genera audio"**

### Inserimento silenzio

| Simbolo | Durata silenzio |
|---|---|
| `……`（puntini di sospensione） | Valore dello slider（secondi） |
| `。` `！` `？` | Valore dello slider × 0.5（secondi） |

Regolare con lo slider **"Durata silenzio"**（0–3 secondi）.

### Dizionario utente

Registrare nomi propri in `user_dict.json`:

```json
{
  "伝の心": {
    "reading": "でんのしん",
    "accent_type": 3,
    "note": "Dispositivo di comunicazione per persone con disabilità gravi"
  }
}
```

Valori del tipo di accento:
- `0`: Piatto（heiban）— per esempio, お↑かね
- `1`: Alto iniziale（atamadaka）— per esempio, あ↓たま
- `N`: Cade dopo la N-esima mora — per esempio, `3` → で↑んの↓しん

---

## Integrazione con MeCab_accent_tool

Quando un `.dic` viene compilato da [MeCab_accent_tool](https://github.com/daibo0501/MeCab_accent_tool),  
questo repository lo rileva e lo usa automaticamente.

```
MeCab_accent_tool/ → compila → output/mecab_accent.dic
Qwen3-TTS-JP-MeCab/ preprocess_block.py → rileva automaticamente mecab_accent.dic
    → legge il tipo di accento dal 14° campo delle voci MeCab
```

Posizionare `mecab_accent.dic` nella radice del progetto per il rilevamento automatico.

---

## Pacchetti correlati

| Pacchetto | Versione | Scopo | Posizione installazione |
|---|---|---|---|
| [mecab-python3](https://github.com/SamuraiT/mecab-python3) | 1.0+ | Binding MeCab per Python | Python di sistema |
| [pyopenjtalk-plus](https://github.com/tsukumijima/pyopenjtalk) | 0.4+ | Conversione lettura + previsione accento | Python di sistema |
| [marine](https://github.com/6gsn/marine) | 0.0.6+ | Previsione accento DNN（precisione migliorata） | Python di sistema |
| [gradio](https://github.com/gradio-app/gradio) | 6.0+ | Web UI | venv |
| [torch](https://pytorch.org/) | 2.4+ | Motore di inferenza | venv |
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | - | Trascrizione automatica | venv |

---

## Risoluzione dei problemi

| Sintomo | Causa | Soluzione |
|---|---|---|
| `pyopenjtalk-plus caricamento fallito` | Non installato in Python di sistema | Eseguire `python -m pip install pyopenjtalk-plus` con Python di sistema |
| Casella `Preprocessamento MeCab` non mostrata | MeCab o pyopenjtalk non installati | Verificare i passi 1 e 5 |
| Errore DLL `torch_library_impl` | Avviato con venv Python | Usare `launch_gui-2.py`（Python di sistema） |
| `FlashAttention2 cannot be used` | FlashAttention non supportato su Windows | Assicurarsi che l'opzione `--no-flash-attn` sia impostata |
| `SoX could not be found` | SoX non installato | Può essere ignorato（nessun impatto sulla funzionalità principale） |
| Accento non visualizzato | mecab_accent.dic mancante | Compilare con MeCab_accent_tool |

---

## Licenza

Questo progetto è rilasciato sotto la [Apache License 2.0](../LICENSE).

### Software open source utilizzato

| Software | Licenza | Copyright |
|---|---|---|
| [Qwen3-TTS](https://github.com/QwenLM/Qwen3-TTS) | Apache License 2.0 | Copyright 2026 Alibaba Cloud |
| [Qwen3-TTS-JP](https://github.com/hiroki-abe-58/Qwen3-TTS-JP) | Apache License 2.0 | Copyright hiroki-abe-58 |
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | MIT License | Copyright SYSTRAN |
| [mecab-python3](https://github.com/SamuraiT/mecab-python3) | BSD License | Copyright SamuraiT |
| [pyopenjtalk-plus](https://github.com/tsukumijima/pyopenjtalk) | MIT License | Copyright tsukumijima |
| [marine](https://github.com/6gsn/marine) | Apache License 2.0 | Copyright 6gsn |

Per i dettagli, consultare il file [NOTICE](../NOTICE).

---

## Dichiarazione di non responsabilità

- L'audio generato è prodotto automaticamente da un modello di IA e può contenere contenuti imprecisi
- **Clonare o usare la voce di un'altra persona senza il suo consenso può violare i diritti all'immagine e di pubblicità**
- Gli sviluppatori non si assumono alcuna responsabilità per i danni derivanti dall'uso di questo software

---

## Ringraziamenti

- Qwen3-TTS originale: [Alibaba Cloud Qwen Team](https://github.com/QwenLM)
- Base del fork Windows: [Qwen3-TTS-JP](https://github.com/hiroki-abe-58/Qwen3-TTS-JP) di hiroki-abe-58
