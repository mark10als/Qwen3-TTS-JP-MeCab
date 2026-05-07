[English](README_en.md) | [日本語](../README.md) | [中文](README_zh.md) | [한국어](README_ko.md) | **Русский** | [Español](README_es.md) | [Italiano](README_it.md) | [Deutsch](README_de.md) | [Français](README_fr.md) | [Português](README_pt.md)

# Qwen3-TTS-JP-MeCab

> ⚠️ **Этот репозиторий предназначен только для японского языка.**  
> Это специализированный форк с предобработкой японского текста на основе MeCab.

---

## Отличия от Qwen3-TTS-JP

| Функция | [Qwen3-TTS-JP](https://github.com/hiroki-abe-58/Qwen3-TTS-JP) | **Этот репозиторий（Qwen3-TTS-JP-MeCab）** |
|---|---|---|
| Целевой язык | Многоязычный（UI на 10 языках） | **Только японский** |
| Предобработка текста | Нет | **Преобразование кандзи→кана через MeCab + pyopenjtalk-plus** |
| Анализ акцента | Нет | **Отображение информации об акценте из словаря MeCab** |
| Пользовательский словарь | Нет | **Регистрация собственных имён с чтением и акцентом** |
| MeCab | Не требуется | **Требуется отдельная установка** |
| Метод запуска | venv Python | **Системный Python（требуется для pyopenjtalk）** |
| Вставка тишины | Нет | **Вставка тишины после `……` и конечных знаков препинания** |

---

## Функции

### Все функции из Qwen3-TTS-JP

- **Нативная работа в Windows**: WSL2/Docker не требуется, FlashAttention2 не требуется
- **Custom Voice**: Синтез речи с предустановленными говорящими
- **Voice Design**: Описание характеристик голоса в тексте для синтеза
- **Voice Clone**: Клонирование голоса из эталонного аудио（с автоматической транскрипцией Whisper）
- **Поддержка RTX 50 серии**: Сборка PyTorch nightly（cu128）

### Добавленные функции（японская предобработка）

- **Автоматическое преобразование кандзи→кана**: Преобразование в хирагану для TTS с помощью MeCab + pyopenjtalk-plus
- **Отображение акцента**: Просмотр чтения с маркерами `↑`（восходящий）`↓`（нисходящий）— редактируемый
- **Пользовательский словарь**: Регистрация собственных имён в `user_dict.json` с правильным чтением и акцентом
- **Интеграция словаря акцентов**: Автоматическое обнаружение `.dic`, скомпилированного [MeCab_accent_tool](https://github.com/daibo0501/MeCab_accent_tool)
- **Вставка тишины**: Вставка тишины после `……`（полная длительность）и `。！？`（половина длительности）

---

## Системные требования

- **ОС**: Windows 10/11（нативная среда）
- **GPU**: GPU NVIDIA（с поддержкой CUDA）
  - RTX 30/40 серии: Стабильная версия PyTorch
  - RTX 50 серии（Blackwell）: PyTorch nightly（cu128）
- **Python**: 3.10 или выше
- **VRAM**: Рекомендуется 8 ГБ и более
- **MeCab**: Требуется отдельная установка（см. ниже）

---

## Установка

### Шаг 1: Установка MeCab（обязательно, отдельно）

MeCab необходимо установить как системное приложение, независимо от виртуальной среды.

1. Загрузите и установите с:  
   👉 **https://github.com/ikegami-yukino/mecab/releases**  
   （Выберите `mecab-64-*.exe`; при установке выберите **UTF-8** для кодировки символов）

2. Проверьте установку:
   ```cmd
   mecab --version
   ```

3. Путь установки по умолчанию:
   ```
   C:\Program Files\MeCab\
   C:\Program Files\MeCab\dic\ipadic\   ← каталог словаря
   ```

### Шаг 2: Клонирование репозитория

```bash
git clone https://github.com/daibo0501/Qwen3-TTS-JP-MeCab.git
cd Qwen3-TTS-JP-MeCab
```

### Шаг 3: Создание виртуальной среды и установка базовых пакетов

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
pip install faster-whisper
```

### Шаг 4: Установка PyTorch（версия с CUDA）

```bash
# Для CUDA 12.x
.venv\Scripts\pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# Для RTX 50 серии（sm_120）
.venv\Scripts\pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128
```

### Шаг 5: Установка пакетов японской предобработки（в системный Python）

> **Важно**: Лаунчер `launch_gui-2.py` использует системный Python.  
> Установите пакеты японской предобработки в системный Python（не в venv）.

```cmd
:: Проверьте путь системного Python
where python

:: Запустите с системным Python（НЕ активируйте venv）
python -m pip install mecab-python3
python -m pip install pyopenjtalk-plus

:: marine требует PYTHONUTF8=1 для избежания ошибок кодировки в Windows
set PYTHONUTF8=1
python -m pip install marine
set PYTHONUTF8=
```

Проверьте установку:

```python
python -c "import MeCab; print('MeCab: OK')"
python -c "import pyopenjtalk; print('pyopenjtalk-plus: OK')"
python -c "import marine; print('marine: OK')"
```

### Шаг 6: Настройка MeCab_accent_tool（рекомендуется）

Вспомогательный инструмент для управления информацией об акценте собственных имён.

```bash
git clone https://github.com/daibo0501/MeCab_accent_tool.git
```

Подробности см. в [README MeCab_accent_tool](https://github.com/daibo0501/MeCab_accent_tool).

---

## Использование

### Запуск GUI

Дважды щёлкните `launch_gui-2.py` или:

```bash
python launch_gui-2.py
```

Браузер автоматически откроется по адресу `http://127.0.0.1:7860`.

> **Примечание**: Запускайте с **системным Python**, а не с `.venv\Scripts\python.exe`.  
> pyopenjtalk-plus установлен в системный Python.

### Процедура японского TTS

1. Откройте вкладку Voice Clone / Custom Voice / Voice Design
2. Введите японский текст в поле «Текст для синтеза»
3. При обнаружении японского автоматически включается флажок **«Предобработка MeCab»**
4. Нажмите **«Преобразовать и проанализировать»**
   - «Преобразованный текст»: Чтение хираганой для TTS（редактируемый）
   - «Чтение с метками акцента»: Отображает чтение с маркерами `↑`/`↓`（редактируемый）
5. При необходимости отредактируйте текст
6. Нажмите **«Создать аудио»**

### Вставка тишины

| Символ | Длительность тишины |
|---|---|
| `……`（многоточие） | Значение слайдера（секунды） |
| `。` `！` `？` | Значение слайдера × 0.5（секунды） |

Настройте с помощью слайдера **«Длительность тишины»**（0–3 секунды）.

### Пользовательский словарь

Зарегистрируйте собственные имена в `user_dict.json`:

```json
{
  "伝の心": {
    "reading": "でんのしん",
    "accent_type": 3,
    "note": "Устройство передачи информации для людей с тяжёлыми нарушениями"
  }
}
```

Значения типа акцента:
- `0`: Плоский（хэйбан）— например, お↑かね
- `1`: Высокий первый слог（атамадака）— например, あ↓たま
- `N`: Падение после N-й моры — например, `3` → で↑んの↓しん

---

## Интеграция с MeCab_accent_tool

Когда `.dic` скомпилирован с помощью [MeCab_accent_tool](https://github.com/daibo0501/MeCab_accent_tool),  
этот репозиторий автоматически обнаруживает и использует его.

```
MeCab_accent_tool/ → компилирует → output/mecab_accent.dic
Qwen3-TTS-JP-MeCab/ preprocess_block.py → автоматически обнаруживает mecab_accent.dic
    → читает тип акцента из 14-го поля записей MeCab
```

Поместите `mecab_accent.dic` в корень проекта для автоматического обнаружения.

---

## Связанные пакеты

| Пакет | Версия | Назначение | Место установки |
|---|---|---|---|
| [mecab-python3](https://github.com/SamuraiT/mecab-python3) | 1.0+ | Привязки MeCab для Python | Системный Python |
| [pyopenjtalk-plus](https://github.com/tsukumijima/pyopenjtalk) | 0.4+ | Преобразование чтения + прогнозирование акцента | Системный Python |
| [marine](https://github.com/6gsn/marine) | 0.0.6+ | DNN прогнозирование акцента（повышенная точность） | Системный Python |
| [gradio](https://github.com/gradio-app/gradio) | 6.0+ | Web UI | venv |
| [torch](https://pytorch.org/) | 2.4+ | Механизм вывода | venv |
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | - | Автоматическая транскрипция | venv |

---

## Устранение неполадок

| Симптом | Причина | Решение |
|---|---|---|
| `pyopenjtalk-plus загрузка не удалась` | Не установлен в системный Python | Запустите `python -m pip install pyopenjtalk-plus` с системным Python |
| Флажок `Предобработка MeCab` не отображается | MeCab или pyopenjtalk не установлены | Проверьте шаги 1 и 5 |
| Ошибка DLL `torch_library_impl` | Запущен с venv Python | Используйте `launch_gui-2.py`（системный Python） |
| `FlashAttention2 cannot be used` | FlashAttention не поддерживается в Windows | Убедитесь, что установлена опция `--no-flash-attn` |
| `SoX could not be found` | SoX не установлен | Можно игнорировать（не влияет на основную функциональность） |
| Акцент не отображается | Отсутствует mecab_accent.dic | Скомпилируйте с помощью MeCab_accent_tool |

---

## Лицензия

Этот проект выпускается под лицензией [Apache License 2.0](../LICENSE).

### Используемое программное обеспечение с открытым исходным кодом

| ПО | Лицензия | Авторские права |
|---|---|---|
| [Qwen3-TTS](https://github.com/QwenLM/Qwen3-TTS) | Apache License 2.0 | Copyright 2026 Alibaba Cloud |
| [Qwen3-TTS-JP](https://github.com/hiroki-abe-58/Qwen3-TTS-JP) | Apache License 2.0 | Copyright hiroki-abe-58 |
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | MIT License | Copyright SYSTRAN |
| [mecab-python3](https://github.com/SamuraiT/mecab-python3) | BSD License | Copyright SamuraiT |
| [pyopenjtalk-plus](https://github.com/tsukumijima/pyopenjtalk) | MIT License | Copyright tsukumijima |
| [marine](https://github.com/6gsn/marine) | Apache License 2.0 | Copyright 6gsn |

Подробности см. в файле [NOTICE](../NOTICE).

---

## Отказ от ответственности

- Сгенерированное аудио создаётся автоматически моделью ИИ и может содержать неточный контент
- **Клонирование или использование голоса другого человека без его согласия может нарушать права на изображение и публичные права**
- Разработчики не несут ответственности за любой ущерб, возникший в результате использования данного ПО

---

## Благодарности

- Оригинальный Qwen3-TTS: [Alibaba Cloud Qwen Team](https://github.com/QwenLM)
- Основа Windows форка: [Qwen3-TTS-JP](https://github.com/hiroki-abe-58/Qwen3-TTS-JP) от hiroki-abe-58
