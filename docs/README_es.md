[English](README_en.md) | [日本語](../README.md) | [中文](README_zh.md) | [한국어](README_ko.md) | [Русский](README_ru.md) | **Español** | [Italiano](README_it.md) | [Deutsch](README_de.md) | [Français](README_fr.md) | [Português](README_pt.md)

# Qwen3-TTS-JP-MeCab

> ⚠️ **Este repositorio es solo para japonés.**  
> Es un fork especializado en japonés con preprocesamiento de texto japonés basado en MeCab.

---

## Diferencias con Qwen3-TTS-JP

| Función | [Qwen3-TTS-JP](https://github.com/hiroki-abe-58/Qwen3-TTS-JP) | **Este repositorio（Qwen3-TTS-JP-MeCab）** |
|---|---|---|
| Idioma objetivo | Multilingüe（UI en 10 idiomas） | **Solo japonés** |
| Preprocesamiento de texto | Ninguno | **Conversión kanji→kana vía MeCab + pyopenjtalk-plus** |
| Análisis de acento | Ninguno | **Visualización de información de acento del diccionario MeCab** |
| Diccionario de usuario | Ninguno | **Registro de nombres propios con lectura y acento** |
| MeCab | No requerido | **Instalación separada requerida** |
| Método de lanzamiento | venv Python | **Python del sistema（requerido para pyopenjtalk）** |
| Inserción de silencio | Ninguna | **Inserción de silencio después de `……` y puntuación final de oración** |

---

## Características

### Todas las características de Qwen3-TTS-JP

- **Windows nativo**: Sin WSL2/Docker, sin FlashAttention2
- **Custom Voice**: Síntesis de voz con hablantes preestablecidos
- **Voice Design**: Descripción de características de voz en texto para síntesis
- **Voice Clone**: Clonar voz desde audio de referencia（con transcripción automática Whisper）
- **Soporte RTX serie 50**: PyTorch nightly build（cu128）

### Características añadidas（preprocesamiento japonés）

- **Conversión automática kanji→kana**: Convierte a hiragana para TTS usando MeCab + pyopenjtalk-plus
- **Visualización de acento**: Ver lectura con marcadores `↑`（ascendente）`↓`（descendente）— editable
- **Diccionario de usuario**: Registro de nombres propios en `user_dict.json` con lectura y acento correctos
- **Integración de diccionario de acento**: Detección automática de `.dic` compilado por [MeCab_accent_tool](https://github.com/daibo0501/MeCab_accent_tool)
- **Inserción de silencio**: Silencio completo después de `……` y medio después de `。！？`

---

## Requisitos del sistema

- **SO**: Windows 10/11（entorno nativo）
- **GPU**: GPU NVIDIA（compatible con CUDA）
  - RTX serie 30/40: PyTorch versión estable
  - RTX serie 50（Blackwell）: PyTorch nightly（cu128）
- **Python**: 3.10 o superior
- **VRAM**: Se recomiendan 8 GB o más
- **MeCab**: Instalación separada requerida（ver abajo）

---

## Instalación

### Paso 1: Instalar MeCab（obligatorio, por separado）

MeCab debe instalarse como aplicación del sistema, independiente del entorno virtual.

1. Descargue e instale desde:  
   👉 **https://github.com/ikegami-yukino/mecab/releases**  
   （Seleccione `mecab-64-*.exe`; elija **UTF-8** para la codificación de caracteres durante la instalación）

2. Verifique la instalación:
   ```cmd
   mecab --version
   ```

3. Ruta de instalación predeterminada:
   ```
   C:\Program Files\MeCab\
   C:\Program Files\MeCab\dic\ipadic\   ← directorio del diccionario
   ```

### Paso 2: Clonar el repositorio

```bash
git clone https://github.com/daibo0501/Qwen3-TTS-JP-MeCab.git
cd Qwen3-TTS-JP-MeCab
```

### Paso 3: Crear entorno virtual e instalar paquetes base

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
pip install faster-whisper
```

### Paso 4: Instalar PyTorch（versión CUDA）

```bash
# Para CUDA 12.x
.venv\Scripts\pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# Para RTX serie 50（sm_120）
.venv\Scripts\pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128
```

### Paso 5: Instalar paquetes de preprocesamiento japonés（en Python del sistema）

> **Importante**: El lanzador `launch_gui-2.py` usa Python del sistema.  
> Instale los paquetes de preprocesamiento japonés en Python del sistema（no en venv）.

```cmd
:: Verificar ruta de Python del sistema
where python

:: Ejecutar con Python del sistema（NO activar venv）
python -m pip install mecab-python3
python -m pip install pyopenjtalk-plus

:: marine requiere PYTHONUTF8=1 para evitar errores de codificación en Windows
set PYTHONUTF8=1
python -m pip install marine
set PYTHONUTF8=
```

Verifique la instalación:

```python
python -c "import MeCab; print('MeCab: OK')"
python -c "import pyopenjtalk; print('pyopenjtalk-plus: OK')"
python -c "import marine; print('marine: OK')"
```

### Paso 6: Configurar MeCab_accent_tool（recomendado）

Herramienta complementaria para gestionar información de acento de nombres propios.

```bash
git clone https://github.com/daibo0501/MeCab_accent_tool.git
```

Consulte el [README de MeCab_accent_tool](https://github.com/daibo0501/MeCab_accent_tool) para más detalles.

---

## Uso

### Iniciar la GUI

Haga doble clic en `launch_gui-2.py`, o:

```bash
python launch_gui-2.py
```

El navegador se abre automáticamente en `http://127.0.0.1:7860`.

> **Nota**: Ejecute con **Python del sistema**, no con `.venv\Scripts\python.exe`.  
> pyopenjtalk-plus está instalado en Python del sistema.

### Procedimiento de TTS japonés

1. Abra la pestaña Voice Clone / Custom Voice / Voice Design
2. Ingrese texto japonés en "Texto a sintetizar"
3. Al detectar japonés, la casilla **"Preprocesamiento MeCab"** se activa y marca automáticamente
4. Haga clic en **"Convertir y analizar"**
   - "Texto convertido": Lectura en hiragana para TTS（editable）
   - "Lectura con marcas de acento": Muestra la lectura con marcadores `↑`/`↓`（editable）
5. Edite el texto si es necesario
6. Haga clic en **"Generar audio"**

### Inserción de silencio

| Símbolo | Duración del silencio |
|---|---|
| `……`（puntos suspensivos） | Valor del deslizador（segundos） |
| `。` `！` `？` | Valor del deslizador × 0.5（segundos） |

Ajuste con el deslizador **"Duración del silencio"**（0–3 segundos）.

### Diccionario de usuario

Registre nombres propios en `user_dict.json`:

```json
{
  "伝の心": {
    "reading": "でんのしん",
    "accent_type": 3,
    "note": "Dispositivo de comunicación para personas con discapacidad grave"
  }
}
```

Valores del tipo de acento:
- `0`: Plano（heiban）— por ejemplo, お↑かね
- `1`: Alto inicial（atamadaka）— por ejemplo, あ↓たま
- `N`: Cae después de la N-ésima mora — por ejemplo, `3` → で↑んの↓しん

---

## Integración con MeCab_accent_tool

Cuando se compila un `.dic` con [MeCab_accent_tool](https://github.com/daibo0501/MeCab_accent_tool),  
este repositorio lo detecta y usa automáticamente.

```
MeCab_accent_tool/ → compila → output/mecab_accent.dic
Qwen3-TTS-JP-MeCab/ preprocess_block.py → detecta automáticamente mecab_accent.dic
    → lee el tipo de acento del campo 14 de las entradas MeCab
```

Coloque `mecab_accent.dic` en la raíz del proyecto para detección automática.

---

## Paquetes relacionados

| Paquete | Versión | Propósito | Ubicación de instalación |
|---|---|---|---|
| [mecab-python3](https://github.com/SamuraiT/mecab-python3) | 1.0+ | Bindings de MeCab para Python | Python del sistema |
| [pyopenjtalk-plus](https://github.com/tsukumijima/pyopenjtalk) | 0.4+ | Conversión de lectura + predicción de acento | Python del sistema |
| [marine](https://github.com/6gsn/marine) | 0.0.6+ | Predicción de acento DNN（mayor precisión） | Python del sistema |
| [gradio](https://github.com/gradio-app/gradio) | 6.0+ | Web UI | venv |
| [torch](https://pytorch.org/) | 2.4+ | Motor de inferencia | venv |
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | - | Transcripción automática | venv |

---

## Solución de problemas

| Síntoma | Causa | Solución |
|---|---|---|
| `pyopenjtalk-plus carga fallida` | No instalado en Python del sistema | Ejecute `python -m pip install pyopenjtalk-plus` con Python del sistema |
| Casilla `Preprocesamiento MeCab` no aparece | MeCab o pyopenjtalk no instalados | Verifique los pasos 1 y 5 |
| Error DLL `torch_library_impl` | Lanzado con venv Python | Use `launch_gui-2.py`（Python del sistema） |
| `FlashAttention2 cannot be used` | FlashAttention no compatible con Windows | Asegúrese de que la opción `--no-flash-attn` esté configurada |
| `SoX could not be found` | SoX no instalado | Se puede ignorar（sin impacto en la funcionalidad principal） |
| Acento no mostrado | Falta mecab_accent.dic | Compile con MeCab_accent_tool |

---

## Licencia

Este proyecto se publica bajo la [Apache License 2.0](../LICENSE).

### Software de código abierto utilizado

| Software | Licencia | Derechos de autor |
|---|---|---|
| [Qwen3-TTS](https://github.com/QwenLM/Qwen3-TTS) | Apache License 2.0 | Copyright 2026 Alibaba Cloud |
| [Qwen3-TTS-JP](https://github.com/hiroki-abe-58/Qwen3-TTS-JP) | Apache License 2.0 | Copyright hiroki-abe-58 |
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | MIT License | Copyright SYSTRAN |
| [mecab-python3](https://github.com/SamuraiT/mecab-python3) | BSD License | Copyright SamuraiT |
| [pyopenjtalk-plus](https://github.com/tsukumijima/pyopenjtalk) | MIT License | Copyright tsukumijima |
| [marine](https://github.com/6gsn/marine) | Apache License 2.0 | Copyright 6gsn |

Consulte el archivo [NOTICE](../NOTICE) para más detalles.

---

## Descargo de responsabilidad

- El audio generado es producido automáticamente por un modelo de IA y puede contener contenido inexacto
- **Clonar o usar la voz de otra persona sin su consentimiento puede violar los derechos de imagen y publicidad**
- Los desarrolladores no asumen responsabilidad por ningún daño derivado del uso de este software

---

## Agradecimientos

- Qwen3-TTS original: [Alibaba Cloud Qwen Team](https://github.com/QwenLM)
- Base del fork para Windows: [Qwen3-TTS-JP](https://github.com/hiroki-abe-58/Qwen3-TTS-JP) por hiroki-abe-58
