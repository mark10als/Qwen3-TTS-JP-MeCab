[English](README_en.md) | [日本語](../README.md) | [中文](README_zh.md) | **한국어** | [Русский](README_ru.md) | [Español](README_es.md) | [Italiano](README_it.md) | [Deutsch](README_de.md) | [Français](README_fr.md) | [Português](README_pt.md)

# Qwen3-TTS-JP-MeCab

> ⚠️ **이 저장소는 일본어 전용입니다.**  
> MeCab 기반 일본어 텍스트 전처리가 추가된 일본어 특화 포크입니다.

---

## Qwen3-TTS-JP와의 차이점

| 기능 | [Qwen3-TTS-JP](https://github.com/hiroki-abe-58/Qwen3-TTS-JP) | **본 저장소（Qwen3-TTS-JP-MeCab）** |
|---|---|---|
| 대상 언어 | 다국어（10언어 UI） | **일본어 전용** |
| 텍스트 전처리 | 없음 | **MeCab + pyopenjtalk-plus를 통한 한자→가나 변환** |
| 액센트 분석 | 없음 | **MeCab 사전의 액센트 정보 표시** |
| 사용자 사전 | 없음 | **고유명사의 독음·액센트 등록 가능** |
| MeCab | 불필요 | **별도 설치 필요** |
| 실행 방법 | venv Python | **시스템 Python（pyopenjtalk 필요）** |
| 묵음 삽입 | 없음 | **`……` 및 문장 끝 구두점（。！？） 뒤에 묵음 삽입 가능** |

---

## 기능

### Qwen3-TTS-JP의 모든 기능 계승

- **Windows 네이티브 동작**: WSL2/Docker 불필요, FlashAttention2 불필요
- **Custom Voice**: 프리셋 화자를 이용한 음성 합성
- **Voice Design**: 텍스트로 목소리 특징을 설명하여 합성
- **Voice Clone**: 참조 음성에서 보이스 클론（Whisper 자동 전사 포함）
- **RTX 50 시리즈 지원**: PyTorch nightly 빌드（cu128）

### 추가 기능（일본어 전처리）

- **한자→가나 자동 변환**: MeCab + pyopenjtalk-plus로 TTS용 히라가나로 변환
- **액센트 기호 표시**: `↑`（상승）`↓`（하강）로 독음 확인·편집 가능
- **사용자 사전 지원**: `user_dict.json`에 고유명사 등록, 정확한 독음과 액센트 설정
- **액센트 사전 통합**: [MeCab_accent_tool](https://github.com/mark10als/MeCab_accent_tool)로 컴파일된 `.dic`를 자동 인식
- **묵음 삽입**: `……`에서 지정 초, `。！？`에서 절반 길이의 묵음을 삽입

---

## 동작 환경

- **OS**: Windows 10/11（네이티브 환경）
- **GPU**: NVIDIA GPU（CUDA 지원）
  - RTX 30/40 시리즈: PyTorch 안정판으로 동작
  - RTX 50 시리즈（Blackwell）: PyTorch nightly（cu128） 필요
- **Python**: 3.10 이상
- **VRAM**: 8GB 이상 권장
- **MeCab**: 별도 설치 필요（아래 참조）

---

## 설치

### 단계 1: MeCab 본체 설치（필수·별도）

MeCab은 시스템 수준 애플리케이션으로 별도 설치가 필요합니다. 가상 환경과 독립적입니다.

1. 아래에서 다운로드하여 설치:  
   👉 **https://github.com/ikegami-yukino/mecab/releases**  
   （`mecab-64-*.exe` 선택, 설치 시 문자 코드는 **UTF-8** 선택）

2. 설치 확인:
   ```cmd
   mecab --version
   ```

3. 기본 설치 경로:
   ```
   C:\Program Files\MeCab\
   C:\Program Files\MeCab\dic\ipadic\   ← 사전 디렉토리
   ```

### 단계 2: 저장소 클론

```bash
git clone https://github.com/mark10als/Qwen3-TTS-JP-MeCab.git
cd Qwen3-TTS-JP-MeCab
```

### 단계 3: 가상 환경 생성 및 기본 패키지 설치

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
pip install faster-whisper
```

### 단계 4: PyTorch（CUDA 버전） 설치

```bash
# CUDA 12.x
.venv\Scripts\pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# RTX 50 시리즈（sm_120）
.venv\Scripts\pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128
```

### 단계 5: 일본어 전처리 패키지 설치（시스템 Python에）

> **중요**: 실행 런처 `launch_gui-2.py`는 시스템 Python을 사용합니다.  
> 일본어 전처리 패키지는 시스템 Python에 설치해 주세요（venv 아님）.

```cmd
:: 시스템 Python 경로 확인
where python

:: 시스템 Python으로 실행（venv를 활성화하지 말 것）
python -m pip install mecab-python3
python -m pip install pyopenjtalk-plus

:: marine은 Windows 인코딩 오류 방지를 위해 PYTHONUTF8=1 필요
set PYTHONUTF8=1
python -m pip install marine
set PYTHONUTF8=
```

설치 확인:

```python
python -c "import MeCab; print('MeCab: OK')"
python -c "import pyopenjtalk; print('pyopenjtalk-plus: OK')"
python -c "import marine; print('marine: OK')"
```

### 단계 6: MeCab_accent_tool 설정（권장）

고유명사 액센트 정보를 관리하기 위한 부속 도구입니다.

```bash
git clone https://github.com/mark10als/MeCab_accent_tool.git
```

자세한 내용은 [MeCab_accent_tool README](https://github.com/mark10als/MeCab_accent_tool)를 참조하세요.

---

## 사용 방법

### GUI 시작

`launch_gui-2.py`를 더블클릭하거나:

```bash
python launch_gui-2.py
```

브라우저에서 `http://127.0.0.1:7860`이 자동으로 열립니다.

> **주의**: `.venv\Scripts\python.exe`가 아닌 **시스템 Python**으로 실행하세요.  
> pyopenjtalk-plus는 시스템 Python에 설치되어 있습니다.

### 일본어 TTS 합성 절차

1. Voice Clone / Custom Voice / Voice Design 탭 열기
2. "합성할 텍스트"에 일본어 텍스트 입력
3. 일본어가 감지되면 자동으로 **"MeCab 전처리"** 체크박스가 활성화·체크됨
4. **"변환 및 분석"** 클릭
   - "변환 후 텍스트": TTS에 전달하는 히라가나 독음 표시（편집 가능）
   - "액센트 기호 포함 독음": `↑`/`↓` 기호로 독음과 액센트 확인（편집 가능）
5. 필요에 따라 텍스트 수정
6. **"음성 생성"** 클릭

### 묵음 삽입 기능

| 기호 | 묵음 시간 |
|---|---|
| `……`（말줄임표） | 슬라이더 설정값（초） |
| `。` `！` `？` | 슬라이더 설정값 × 0.5（초） |

**"묵음 시간"** 슬라이더（0～3초）로 조정하세요.

### 사용자 사전 설정

`user_dict.json`에 고유명사를 등록할 수 있습니다:

```json
{
  "伝の心": {
    "reading": "でんのしん",
    "accent_type": 3,
    "note": "중증 장애인용 의사 전달 장치"
  }
}
```

액센트 형의 의미:
- `0`: 평판형（예: お↑かね）
- `1`: 두고형（예: あ↓たま）
- `N`: N번째 박에서 하강（예: `3` → で↑んの↓しん）

---

## MeCab_accent_tool과의 연동

[MeCab_accent_tool](https://github.com/mark10als/MeCab_accent_tool)로 액센트 사전 `.dic`를 컴파일하면,  
본 저장소가 자동으로 감지하여 사용합니다.

```
MeCab_accent_tool/ → 컴파일 → output/mecab_accent.dic
Qwen3-TTS-JP-MeCab/ preprocess_block.py → mecab_accent.dic 자동 감지
    → MeCab 항목의 14번째 필드에서 액센트 형 사용
```

`mecab_accent.dic`를 프로젝트 루트에 배치하면 자동 인식됩니다.

---

## 관련 패키지

| 패키지 | 버전 | 용도 | 설치 위치 |
|---|---|---|---|
| [mecab-python3](https://github.com/SamuraiT/mecab-python3) | 1.0+ | MeCab Python 바인딩 | 시스템 Python |
| [pyopenjtalk-plus](https://github.com/tsukumijima/pyopenjtalk) | 0.4+ | 독음 변환 + 액센트 예측 | 시스템 Python |
| [marine](https://github.com/6gsn/marine) | 0.0.6+ | DNN 액센트 예측（정확도 향상） | 시스템 Python |
| [gradio](https://github.com/gradio-app/gradio) | 6.0+ | Web UI | venv |
| [torch](https://pytorch.org/) | 2.4+ | 추론 엔진 | venv |
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | - | 자동 전사 | venv |

---

## 문제 해결

| 증상 | 원인 | 해결책 |
|---|---|---|
| `pyopenjtalk-plus 로드 실패` | 시스템 Python에 설치되지 않음 | 시스템 Python으로 `python -m pip install pyopenjtalk-plus` 실행 |
| `MeCab 전처리` 체크박스가 표시되지 않음 | MeCab 또는 pyopenjtalk 미설치 | 단계 1·5 확인 |
| `torch_library_impl` DLL 오류 | venv Python으로 시작한 경우 | `launch_gui-2.py`（시스템 Python）로 시작 |
| `FlashAttention2 cannot be used` | FlashAttention이 Windows 비지원 | `--no-flash-attn` 옵션 확인 |
| `SoX could not be found` | SoX 미설치 | 무시 가능（기본 기능에 영향 없음） |
| 액센트가 표시되지 않음 | mecab_accent.dic 없음 | MeCab_accent_tool로 컴파일 |

---

## 라이선스

본 프로젝트는 [Apache License 2.0](../LICENSE) 하에 공개되어 있습니다.

### 사용된 오픈소스 소프트웨어

| 소프트웨어 | 라이선스 | 저작권 |
|---|---|---|
| [Qwen3-TTS](https://github.com/QwenLM/Qwen3-TTS) | Apache License 2.0 | Copyright 2026 Alibaba Cloud |
| [Qwen3-TTS-JP](https://github.com/hiroki-abe-58/Qwen3-TTS-JP) | Apache License 2.0 | Copyright hiroki-abe-58 |
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | MIT License | Copyright SYSTRAN |
| [mecab-python3](https://github.com/SamuraiT/mecab-python3) | BSD License | Copyright SamuraiT |
| [pyopenjtalk-plus](https://github.com/tsukumijima/pyopenjtalk) | MIT License | Copyright tsukumijima |
| [marine](https://github.com/6gsn/marine) | Apache License 2.0 | Copyright 6gsn |

자세한 내용은 [NOTICE](../NOTICE) 파일을 참조하세요.

---

## 면책 조항

- 생성된 음성은 AI에 의해 자동 생성되며 부정확한 내용이 포함될 수 있습니다
- **타인의 목소리를 무단으로 복제·사용하는 것은 초상권 및 퍼블리시티권 침해가 될 수 있습니다**
- 본 소프트웨어의 사용으로 발생한 어떠한 손해에 대해서도 개발자는 책임을 지지 않습니다

---

## 감사의 말

- 원본 Qwen3-TTS: [Alibaba Cloud Qwen Team](https://github.com/QwenLM)
- Windows 포크 기반: [Qwen3-TTS-JP](https://github.com/hiroki-abe-58/Qwen3-TTS-JP) by hiroki-abe-58
