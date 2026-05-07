[English](README_en.md) | [日本語](../README.md) | [中文](README_zh.md) | [한국어](README_ko.md) | [Русский](README_ru.md) | [Español](README_es.md) | [Italiano](README_it.md) | [Deutsch](README_de.md) | [Français](README_fr.md) | **Português**

# Qwen3-TTS-JP-MeCab

> ⚠️ **Este repositório é apenas para o idioma japonês.**  
> Este é um fork especializado em japonês com pré-processamento de texto japonês baseado em MeCab.

---

## Diferenças em relação ao Qwen3-TTS-JP

| Funcionalidade | [Qwen3-TTS-JP](https://github.com/hiroki-abe-58/Qwen3-TTS-JP) | **Este repositório（Qwen3-TTS-JP-MeCab）** |
|---|---|---|
| Idioma alvo | Multilíngue（UI em 10 idiomas） | **Apenas japonês** |
| Pré-processamento de texto | Nenhum | **Conversão kanji→kana via MeCab + pyopenjtalk-plus** |
| Análise de acento | Nenhuma | **Exibição de informações de acento do dicionário MeCab** |
| Dicionário do usuário | Nenhum | **Registro de nomes próprios com leitura e acento** |
| MeCab | Não necessário | **Instalação separada necessária** |
| Método de lançamento | venv Python | **Python do sistema（necessário para pyopenjtalk）** |
| Inserção de silêncio | Nenhuma | **Inserção de silêncio após `……` e pontuação final de frase** |

---

## Funcionalidades

### Todas as funcionalidades do Qwen3-TTS-JP

- **Nativo no Windows**: Sem WSL2/Docker, sem FlashAttention2
- **Custom Voice**: Síntese de voz com falantes predefinidos
- **Voice Design**: Descrever características de voz em texto para síntese
- **Voice Clone**: Clonar voz de áudio de referência（com transcrição automática Whisper）
- **Suporte para RTX série 50**: PyTorch nightly build（cu128）

### Funcionalidades adicionadas（pré-processamento japonês）

- **Conversão automática kanji→kana**: Converte para hiragana para TTS usando MeCab + pyopenjtalk-plus
- **Exibição de acento**: Visualizar leitura com marcadores `↑`（ascendente）`↓`（descendente）— editável
- **Dicionário do usuário**: Registro de nomes próprios em `user_dict.json` com leitura e acento corretos
- **Integração de dicionário de acento**: Detecção automática de `.dic` compilado pelo [MeCab_accent_tool](https://github.com/mark10als/MeCab_accent_tool)
- **Inserção de silêncio**: Silêncio completo após `……` e metade após `。！？`

---

## Requisitos do sistema

- **SO**: Windows 10/11（ambiente nativo）
- **GPU**: GPU NVIDIA（compatível com CUDA）
  - RTX série 30/40: PyTorch versão estável
  - RTX série 50（Blackwell）: PyTorch nightly（cu128）
- **Python**: 3.10 ou superior
- **VRAM**: 8 GB ou mais recomendados
- **MeCab**: Instalação separada necessária（ver abaixo）

---

## Instalação

### Passo 1: Instalar MeCab（obrigatório, separado）

O MeCab deve ser instalado como aplicação do sistema, independente do ambiente virtual.

1. Baixar e instalar de:  
   👉 **https://github.com/ikegami-yukino/mecab/releases**  
   （Selecionar `mecab-64-*.exe`; escolher **UTF-8** para codificação de caracteres durante a instalação）

2. Verificar a instalação:
   ```cmd
   mecab --version
   ```

3. Caminho de instalação padrão:
   ```
   C:\Program Files\MeCab\
   C:\Program Files\MeCab\dic\ipadic\   ← diretório do dicionário
   ```

### Passo 2: Clonar o repositório

```bash
git clone https://github.com/mark10als/Qwen3-TTS-JP-MeCab.git
cd Qwen3-TTS-JP-MeCab
```

### Passo 3: Criar ambiente virtual e instalar pacotes base

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
pip install faster-whisper
```

### Passo 4: Instalar PyTorch（versão CUDA）

```bash
# Para CUDA 12.x
.venv\Scripts\pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# Para RTX série 50（sm_120）
.venv\Scripts\pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128
```

### Passo 5: Instalar pacotes de pré-processamento japonês（no Python do sistema）

> **Importante**: O lançador `launch_gui-2.py` usa Python do sistema.  
> Instale os pacotes de pré-processamento japonês no Python do sistema（não no venv）.

```cmd
:: Verificar caminho do Python do sistema
where python

:: Executar com Python do sistema（NÃO ativar venv）
python -m pip install mecab-python3
python -m pip install pyopenjtalk-plus

:: marine requer PYTHONUTF8=1 para evitar erros de codificação no Windows
set PYTHONUTF8=1
python -m pip install marine
set PYTHONUTF8=
```

Verificar a instalação:

```python
python -c "import MeCab; print('MeCab: OK')"
python -c "import pyopenjtalk; print('pyopenjtalk-plus: OK')"
python -c "import marine; print('marine: OK')"
```

### Passo 6: Configurar MeCab_accent_tool（recomendado）

Ferramenta complementar para gerenciar informações de acento de nomes próprios.

```bash
git clone https://github.com/mark10als/MeCab_accent_tool.git
```

Consulte o [README do MeCab_accent_tool](https://github.com/mark10als/MeCab_accent_tool) para mais detalhes.

---

## Uso

### Iniciar a GUI

Clique duas vezes em `launch_gui-2.py`, ou:

```bash
python launch_gui-2.py
```

O navegador abre automaticamente em `http://127.0.0.1:7860`.

> **Nota**: Execute com **Python do sistema**, não com `.venv\Scripts\python.exe`.  
> pyopenjtalk-plus está instalado no Python do sistema.

### Procedimento de TTS japonês

1. Abrir a aba Voice Clone / Custom Voice / Voice Design
2. Inserir texto japonês em "Texto a sintetizar"
3. Ao detectar japonês, a caixa de seleção **"Pré-processamento MeCab"** é automaticamente ativada e marcada
4. Clicar em **"Converter e analisar"**
   - "Texto convertido": Leitura em hiragana para TTS（editável）
   - "Leitura com marcadores de acento": Exibe a leitura com marcadores `↑`/`↓`（editável）
5. Editar o texto se necessário
6. Clicar em **"Gerar áudio"**

### Inserção de silêncio

| Símbolo | Duração do silêncio |
|---|---|
| `……`（reticências） | Valor do controle deslizante（segundos） |
| `。` `！` `？` | Valor do controle deslizante × 0.5（segundos） |

Ajustar com o controle deslizante **"Duração do silêncio"**（0–3 segundos）.

### Dicionário do usuário

Registrar nomes próprios em `user_dict.json`:

```json
{
  "伝の心": {
    "reading": "でんのしん",
    "accent_type": 3,
    "note": "Dispositivo de comunicação para pessoas com deficiência grave"
  }
}
```

Valores do tipo de acento:
- `0`: Plano（heiban）— por exemplo, お↑かね
- `1`: Alto inicial（atamadaka）— por exemplo, あ↓たま
- `N`: Cai após a N-ésima mora — por exemplo, `3` → で↑んの↓しん

---

## Integração com MeCab_accent_tool

Quando um `.dic` é compilado pelo [MeCab_accent_tool](https://github.com/mark10als/MeCab_accent_tool),  
este repositório o detecta e usa automaticamente.

```
MeCab_accent_tool/ → compila → output/mecab_accent.dic
Qwen3-TTS-JP-MeCab/ preprocess_block.py → detecta automaticamente mecab_accent.dic
    → lê o tipo de acento do 14º campo das entradas MeCab
```

Coloque `mecab_accent.dic` na raiz do projeto para detecção automática.

---

## Pacotes relacionados

| Pacote | Versão | Propósito | Local de instalação |
|---|---|---|---|
| [mecab-python3](https://github.com/SamuraiT/mecab-python3) | 1.0+ | Ligações MeCab para Python | Python do sistema |
| [pyopenjtalk-plus](https://github.com/tsukumijima/pyopenjtalk) | 0.4+ | Conversão de leitura + previsão de acento | Python do sistema |
| [marine](https://github.com/6gsn/marine) | 0.0.6+ | Previsão de acento DNN（precisão aprimorada） | Python do sistema |
| [gradio](https://github.com/gradio-app/gradio) | 6.0+ | Web UI | venv |
| [torch](https://pytorch.org/) | 2.4+ | Motor de inferência | venv |
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | - | Transcrição automática | venv |

---

## Solução de problemas

| Sintoma | Causa | Solução |
|---|---|---|
| `pyopenjtalk-plus carregamento falhou` | Não instalado no Python do sistema | Executar `python -m pip install pyopenjtalk-plus` com Python do sistema |
| Caixa `Pré-processamento MeCab` não mostrada | MeCab ou pyopenjtalk não instalados | Verificar os passos 1 e 5 |
| Erro DLL `torch_library_impl` | Iniciado com venv Python | Usar `launch_gui-2.py`（Python do sistema） |
| `FlashAttention2 cannot be used` | FlashAttention não suportado no Windows | Garantir que a opção `--no-flash-attn` esteja configurada |
| `SoX could not be found` | SoX não instalado | Pode ser ignorado（sem impacto na funcionalidade principal） |
| Acento não exibido | mecab_accent.dic ausente | Compilar com MeCab_accent_tool |

---

## Licença

Este projeto é publicado sob a [Apache License 2.0](../LICENSE).

### Software de código aberto utilizado

| Software | Licença | Direitos autorais |
|---|---|---|
| [Qwen3-TTS](https://github.com/QwenLM/Qwen3-TTS) | Apache License 2.0 | Copyright 2026 Alibaba Cloud |
| [Qwen3-TTS-JP](https://github.com/hiroki-abe-58/Qwen3-TTS-JP) | Apache License 2.0 | Copyright hiroki-abe-58 |
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | MIT License | Copyright SYSTRAN |
| [mecab-python3](https://github.com/SamuraiT/mecab-python3) | BSD License | Copyright SamuraiT |
| [pyopenjtalk-plus](https://github.com/tsukumijima/pyopenjtalk) | MIT License | Copyright tsukumijima |
| [marine](https://github.com/6gsn/marine) | Apache License 2.0 | Copyright 6gsn |

Para mais detalhes, consulte o arquivo [NOTICE](../NOTICE).

---

## Isenção de responsabilidade

- O áudio gerado é produzido automaticamente por um modelo de IA e pode conter conteúdo impreciso
- **Clonar ou usar a voz de outra pessoa sem seu consentimento pode violar os direitos de imagem e publicidade**
- Os desenvolvedores não assumem responsabilidade por quaisquer danos decorrentes do uso deste software

---

## Agradecimentos

- Qwen3-TTS original: [Alibaba Cloud Qwen Team](https://github.com/QwenLM)
- Base do fork para Windows: [Qwen3-TTS-JP](https://github.com/hiroki-abe-58/Qwen3-TTS-JP) por hiroki-abe-58
