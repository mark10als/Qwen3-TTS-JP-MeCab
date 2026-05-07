#!/usr/bin/env python3
"""
Qwen3-TTS Voice Clone スクリプト（2パス前処理 + アクセント解析対応版）

Pass 1: MeCab で形態素解析し、未知語・固有名詞を検出
Pass 2: user_dict.json を適用 → pyopenjtalk-plus で読み変換 → アクセント表示
marine をインストールすると DNN ベースのアクセント予測も利用できる。

使い方:
1. 参照音声（WAV、3秒以上）と対応テキストを用意
2. TEXT_TO_GENERATE に読み上げたいテキストを入力
3. CONVERT_TO_YOMI = True で 2 パス前処理が有効になる
4. 要確認語が出たら user_dict.json に登録して再実行
"""

import torch
import soundfile as sf
from qwen_tts import Qwen3TTSModel
import os
import time

from tts_preprocess import TTSPreprocessor

# ===== 設定 =====

# 参照音声のパス
REF_AUDIO_PATH = "my_voice3.wav"

# 参照音声の内容（録音で話している内容を正確に）
REF_TEXT = "あらゆる技術は、使い方次第で世界を変えられます。今日の天気は晴れ、気温は二十五度の予報です。本当にそう思いますか？私はちょっと違うと思うんですよね。じゃあ、早速始めましょうか！"

# 生成したいテキスト（漢字・固有名詞混じりでOK）
TEXT_TO_GENERATE = "伝の心やオペレートナビは、重度障害者が意思を伝えるための装置です。今の音声をキューエン3のTTSが出力しています。"

# True: 2パス前処理（読み変換 + アクセント解析）を実行する
# False: テキストをそのまま TTS に渡す
CONVERT_TO_YOMI = True

# ユーザー辞書パス
USER_DICT_PATH = "user_dict.json"

# 言語設定
LANGUAGE = "Japanese"

# 出力ファイル名
OUTPUT_FILE = "output.wav"


# ===== メイン処理 =====
def main():
    print("=" * 60)
    print("Qwen3-TTS Voice Clone (2パス前処理 + アクセント解析対応版)")
    print("=" * 60)

    pre = TTSPreprocessor(USER_DICT_PATH)

    # ──────────────────────────────────────────────
    # Pass 1: MeCab 形態素解析・要確認語リストアップ
    # ──────────────────────────────────────────────
    if CONVERT_TO_YOMI:
        pre.print_analysis(TEXT_TO_GENERATE)
        print()
        print("⬆️  上記に要確認語がある場合は user_dict.json に登録後、")
        print("   スクリプトを再実行してください。そのまま続行する場合は Enter を押してください。")
        input("   [Enter で続行] ")

        # ──────────────────────────────────────────
        # Pass 2: ユーザー辞書適用 + 読み変換
        # ──────────────────────────────────────────
        pre.reload_user_dict()
        tts_text = pre.convert(TEXT_TO_GENERATE, verbose=True)

        # アクセント解析表示
        pre.show_accent(tts_text)
    else:
        tts_text = TEXT_TO_GENERATE

    # デバイス設定
    if torch.cuda.is_available():
        device = "cuda"
        print(f"\n✅ デバイス: CUDA (GPU)")
    elif torch.backends.mps.is_available():
        device = "mps"
        print(f"\n✅ デバイス: Apple Silicon (MPS)")
    else:
        device = "cpu"
        print(f"\n⚠️ デバイス: CPU (遅くなります)")

    # 参照音声の確認
    if not os.path.exists(REF_AUDIO_PATH):
        print(f"\n❌ エラー: 参照音声ファイルが見つかりません: {REF_AUDIO_PATH}")
        print("1. 自分の声を3秒以上録音してWAVファイルで保存")
        print("2. ファイル名を 'my_voice3.wav' にするか REF_AUDIO_PATH を変更")
        return

    print(f"\n📂 参照音声: {REF_AUDIO_PATH}")
    print(f"📝 参照テキスト: {REF_TEXT}")
    print(f"🎯 入力テキスト: {TEXT_TO_GENERATE}")
    if CONVERT_TO_YOMI:
        print(f"🔤 変換後テキスト: {tts_text}")
    print(f"🌐 言語: {LANGUAGE}")

    # モデルロード
    print("\n⏳ モデルをロード中...")
    model_load_start = time.time()
    dtype = torch.float32 if device == "mps" else torch.float16
    model = Qwen3TTSModel.from_pretrained(
        "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
        device_map=device,
        dtype=dtype,
    )
    model_load_time = time.time() - model_load_start
    print(f"✅ モデルロード完了 ({model_load_time:.2f}秒)")

    # Voice Clone プロンプト作成
    print("\n⏳ Voice Clone プロンプトを作成中...")
    prompt_start = time.time()
    voice_prompt = model.create_voice_clone_prompt(
        ref_audio=REF_AUDIO_PATH,
        ref_text=REF_TEXT,
    )
    prompt_time = time.time() - prompt_start
    print(f"✅ プロンプト作成完了 ({prompt_time:.2f}秒)")

    # 音声生成
    print("\n⏳ 音声を生成中...")
    generate_start = time.time()
    wavs, sr = model.generate_voice_clone(
        text=tts_text,
        language=LANGUAGE,
        voice_clone_prompt=voice_prompt,
    )
    generate_time = time.time() - generate_start

    sf.write(OUTPUT_FILE, wavs[0], sr)
    audio_duration = len(wavs[0]) / sr

    print(f"\n✅ 完了！出力ファイル: {OUTPUT_FILE}")
    print(f"   サンプルレート: {sr} Hz / 音声の長さ: {audio_duration:.2f}秒")
    print(f"\n⏱️ 処理時間:")
    print(f"   モデルロード: {model_load_time:.2f}秒  プロンプト: {prompt_time:.2f}秒  生成: {generate_time:.2f}秒")
    total = model_load_time + prompt_time + generate_time
    print(f"   合計: {total:.2f}秒  リアルタイム比: {audio_duration / generate_time:.2f}x")


if __name__ == "__main__":
    main()
