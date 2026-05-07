[English](README_en.md) | [日本語](../README.md) | **中文** | [한국어](README_ko.md) | [Русский](README_ru.md) | [Español](README_es.md) | [Italiano](README_it.md) | [Deutsch](README_de.md) | [Français](README_fr.md) | [Português](README_pt.md)

# Qwen3-TTS-JP-MeCab

> ⚠️ **本仓库仅限日语使用。**  
> 这是基于 MeCab 的日语文本预处理专用日语分支。

---

## 与 Qwen3-TTS-JP 的区别

| 功能 | [Qwen3-TTS-JP](https://github.com/hiroki-abe-58/Qwen3-TTS-JP) | **本仓库（Qwen3-TTS-JP-MeCab）** |
|---|---|---|
| 目标语言 | 多语言（10语言UI） | **仅限日语** |
| 文本预处理 | 无 | **通过 MeCab + pyopenjtalk-plus 进行汉字→假名转换** |
| 声调分析 | 无 | **显示 MeCab 词典中的声调信息** |
| 用户词典 | 无 | **可注册专有名词的读音和声调** |
| MeCab | 不需要 | **需要单独安装** |
| 启动方式 | venv Python | **系统 Python（pyopenjtalk 需要）** |
| 静音插入 | 无 | **可在 `……` 和句末标点（。！？）后插入静音** |

---

## 功能特点

### 继承 Qwen3-TTS-JP 的全部功能

- **Windows 原生运行**：无需 WSL2/Docker，无需 FlashAttention2
- **Custom Voice**：使用预设说话人进行语音合成
- **Voice Design**：通过文字描述声音特征进行合成
- **Voice Clone**：从参考音频克隆声音（附带 Whisper 自动转录）
- **RTX 50 系列支持**：PyTorch nightly 构建（cu128）

### 新增功能（日语预处理）

- **汉字→假名自动转换**：使用 MeCab + pyopenjtalk-plus 将文本转换为 TTS 用平假名
- **声调标记显示**：以 `↑`（升调）`↓`（降调）标记显示读音，可编辑
- **用户词典支持**：在 `user_dict.json` 中注册专有名词，设置正确的读音和声调
- **声调词典集成**：自动识别由 [MeCab_accent_tool](https://github.com/daibo0501/MeCab_accent_tool) 编译的 `.dic` 文件
- **静音插入**：`……` 后插入指定秒数的静音，`。！？` 后插入一半时长的静音

---

## 系统要求

- **操作系统**：Windows 10/11（原生环境）
- **GPU**：NVIDIA GPU（支持 CUDA）
  - RTX 30/40 系列：使用 PyTorch 稳定版
  - RTX 50 系列（Blackwell）：需要 PyTorch nightly（cu128）
- **Python**：3.10 或更高
- **显存**：建议 8GB 以上
- **MeCab**：需要单独安装（见下文）

---

## 安装

### 步骤 1：安装 MeCab（必须，单独安装）

MeCab 需要作为系统级应用程序单独安装，与虚拟环境无关。

1. 从以下地址下载并安装：  
   👉 **https://github.com/ikegami-yukino/mecab/releases**  
   （选择 `mecab-64-*.exe`，安装时字符编码选择 **UTF-8**）

2. 验证安装：
   ```cmd
   mecab --version
   ```

3. 默认安装路径：
   ```
   C:\Program Files\MeCab\
   C:\Program Files\MeCab\dic\ipadic\   ← 词典目录
   ```

### 步骤 2：克隆仓库

```bash
git clone https://github.com/daibo0501/Qwen3-TTS-JP-MeCab.git
cd Qwen3-TTS-JP-MeCab
```

### 步骤 3：创建虚拟环境并安装基础包

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
pip install faster-whisper
```

### 步骤 4：安装 PyTorch（CUDA 版本）

```bash
# CUDA 12.x
.venv\Scripts\pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# RTX 50 系列（sm_120）
.venv\Scripts\pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128
```

### 步骤 5：安装日语预处理包（在系统 Python 中）

> **重要**：启动器 `launch_gui-2.py` 使用系统 Python。  
> 请将日语预处理包安装到系统 Python 中（而非 venv）。

```cmd
:: 确认系统 Python 路径
where python

:: 使用系统 Python 运行（不要激活 venv）
python -m pip install mecab-python3
python -m pip install pyopenjtalk-plus

:: marine 需要 PYTHONUTF8=1 以避免 Windows 编码错误
set PYTHONUTF8=1
python -m pip install marine
set PYTHONUTF8=
```

验证安装：

```python
python -c "import MeCab; print('MeCab: OK')"
python -c "import pyopenjtalk; print('pyopenjtalk-plus: OK')"
python -c "import marine; print('marine: OK')"
```

### 步骤 6：设置 MeCab_accent_tool（推荐）

用于管理专有名词声调信息的配套工具。

```bash
git clone https://github.com/daibo0501/MeCab_accent_tool.git
```

详细信息请参阅 [MeCab_accent_tool README](https://github.com/daibo0501/MeCab_accent_tool)。

---

## 使用方法

### 启动 GUI

双击 `launch_gui-2.py`，或：

```bash
python launch_gui-2.py
```

浏览器将自动打开 `http://127.0.0.1:7860`。

> **注意**：请使用**系统 Python** 运行，而非 `.venv\Scripts\python.exe`。  
> pyopenjtalk-plus 安装在系统 Python 中。

### 日语 TTS 操作步骤

1. 打开 Voice Clone / Custom Voice / Voice Design 标签页
2. 在"合成文本"中输入日语文本
3. 检测到日语后，**"MeCab 预处理"**复选框自动启用并勾选
4. 点击**"转换与分析"**
   - "转换后文本"：显示 TTS 使用的平假名读音（可编辑）
   - "带声调标记的读音"：显示带 `↑`/`↓` 标记的读音（可编辑）
5. 根据需要编辑文本
6. 点击**"生成音频"**

### 静音插入功能

| 符号 | 静音时长 |
|---|---|
| `……`（省略号） | 滑块设定值（秒） |
| `。` `！` `？` | 滑块设定值 × 0.5（秒） |

通过**"静音时长"**滑块（0～3 秒）进行调整。

### 用户词典设置

在 `user_dict.json` 中注册专有名词：

```json
{
  "伝の心": {
    "reading": "でんのしん",
    "accent_type": 3,
    "note": "重度障障者用意思传达装置"
  }
}
```

声调型含义：
- `0`：平板型（例：お↑かね）
- `1`：头高型（例：あ↓たま）
- `N`：第 N 拍后下降（例：`3` → で↑んの↓しん）

---

## 与 MeCab_accent_tool 的联动

当 [MeCab_accent_tool](https://github.com/daibo0501/MeCab_accent_tool) 编译声调词典 `.dic` 后，  
本仓库将自动检测并使用它。

```
MeCab_accent_tool/ → 编译 → output/mecab_accent.dic
Qwen3-TTS-JP-MeCab/ preprocess_block.py → 自动检测 mecab_accent.dic
    → 使用 MeCab 条目第 14 个字段中的声调型
```

将 `mecab_accent.dic` 放置于项目根目录即可自动识别。

---

## 相关包

| 包名 | 版本 | 用途 | 安装位置 |
|---|---|---|---|
| [mecab-python3](https://github.com/SamuraiT/mecab-python3) | 1.0+ | MeCab Python 绑定 | 系统 Python |
| [pyopenjtalk-plus](https://github.com/tsukumijima/pyopenjtalk) | 0.4+ | 读音转换 + 声调预测 | 系统 Python |
| [marine](https://github.com/6gsn/marine) | 0.0.6+ | DNN 声调预测（提高精度） | 系统 Python |
| [gradio](https://github.com/gradio-app/gradio) | 6.0+ | Web UI | venv |
| [torch](https://pytorch.org/) | 2.4+ | 推理引擎 | venv |
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | - | 自动转录 | venv |

---

## 故障排除

| 症状 | 原因 | 解决方案 |
|---|---|---|
| `pyopenjtalk-plus 加载失败` | 未安装在系统 Python 中 | 使用系统 Python 运行 `python -m pip install pyopenjtalk-plus` |
| 未显示 `MeCab 预处理`复选框 | MeCab 或 pyopenjtalk 未安装 | 检查步骤 1 和 5 |
| `torch_library_impl` DLL 错误 | 使用 venv Python 启动 | 使用 `launch_gui-2.py`（系统 Python）启动 |
| `FlashAttention2 cannot be used` | FlashAttention 不支持 Windows | 确认已设置 `--no-flash-attn` 选项 |
| `SoX could not be found` | 未安装 SoX | 可忽略（不影响核心功能） |
| 声调未显示 | 缺少 mecab_accent.dic | 使用 MeCab_accent_tool 编译 |

---

## 许可证

本项目基于 [Apache License 2.0](../LICENSE) 发布。

### 使用的开源软件

| 软件 | 许可证 | 版权 |
|---|---|---|
| [Qwen3-TTS](https://github.com/QwenLM/Qwen3-TTS) | Apache License 2.0 | Copyright 2026 Alibaba Cloud |
| [Qwen3-TTS-JP](https://github.com/hiroki-abe-58/Qwen3-TTS-JP) | Apache License 2.0 | Copyright hiroki-abe-58 |
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | MIT License | Copyright SYSTRAN |
| [mecab-python3](https://github.com/SamuraiT/mecab-python3) | BSD License | Copyright SamuraiT |
| [pyopenjtalk-plus](https://github.com/tsukumijima/pyopenjtalk) | MIT License | Copyright tsukumijima |
| [marine](https://github.com/6gsn/marine) | Apache License 2.0 | Copyright 6gsn |

详细信息请参阅 [NOTICE](../NOTICE) 文件。

---

## 免责声明

- 生成的音频由 AI 模型自动产生，可能包含不准确的内容
- **未经他人同意克隆或使用其声音，可能侵犯肖像权和公开权**
- 开发者对使用本软件所造成的任何损害不承担责任

---

## 致谢

- 原始 Qwen3-TTS：[Alibaba Cloud Qwen Team](https://github.com/QwenLM)
- Windows 移植基础：[Qwen3-TTS-JP](https://github.com/hiroki-abe-58/Qwen3-TTS-JP) by hiroki-abe-58
