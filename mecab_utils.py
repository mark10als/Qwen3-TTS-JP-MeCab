"""
MeCabを使った日本語テキスト前処理ユーティリティ
漢字を正しい読み（ひらがな）に変換してTTSの発音精度を向上させる
"""

import os
import sys
import re

# Windows 64ビット版MeCabのインストールパス
MECAB_INSTALL_DIR = r"C:\Program Files\MeCab"
MECAB_BIN_DIR = os.path.join(MECAB_INSTALL_DIR, "bin")
MECAB_DIC_DIR = os.path.join(MECAB_INSTALL_DIR, "dic", "ipadic")


def _setup_mecab_path():
    """Windows環境でMeCabのDLLを見つけられるようにPATHを設定する"""
    if sys.platform == "win32" and os.path.exists(MECAB_BIN_DIR):
        current_path = os.environ.get("PATH", "")
        if MECAB_BIN_DIR not in current_path:
            os.environ["PATH"] = MECAB_BIN_DIR + os.pathsep + current_path


_setup_mecab_path()

try:
    import MeCab
    MECAB_AVAILABLE = True
except ImportError:
    MECAB_AVAILABLE = False
    print("警告: MeCab Pythonバインディングが見つかりません。")
    print("  pip install mecab-python3  でインストールしてください。")


def _create_tagger():
    """MeCabのTaggerインスタンスを生成する（辞書パスを自動検出）"""
    if os.path.exists(MECAB_DIC_DIR):
        # Windows: パスにスペースが含まれるため引数を分割して渡す
        return MeCab.Tagger(f"-d {MECAB_DIC_DIR}")
    return MeCab.Tagger()


def katakana_to_hiragana(text):
    """カタカナをひらがなに変換する（長音符などはそのまま）"""
    result = []
    for ch in text:
        code = ord(ch)
        # ァ(0x30A1) ～ ヶ(0x30F6) の範囲をひらがなに変換
        if 0x30A1 <= code <= 0x30F6:
            result.append(chr(code - 0x60))
        else:
            result.append(ch)
    return "".join(result)


def convert_to_yomi(text, use_hiragana=True):
    """
    MeCabで日本語テキストを読み仮名に変換する。

    IPAdic形式の素性列:
      表層形\\t品詞,品詞細分類1,...,原形,読み,発音
      読み = インデックス 7

    Args:
        text: 変換対象の日本語テキスト
        use_hiragana: True=ひらがな出力 / False=カタカナ出力

    Returns:
        読み仮名に変換されたテキスト。MeCab未使用時は原文を返す。
    """
    if not MECAB_AVAILABLE:
        return text

    try:
        tagger = _create_tagger()
        node = tagger.parseToNode(text)
        result = []

        while node:
            surface = node.surface
            if not surface:
                node = node.next
                continue

            features = node.feature.split(",")
            # 読みフィールド（IPAdic index=7）が存在するか確認
            reading = None
            if len(features) >= 8 and features[7] not in ("*", ""):
                reading = features[7]

            if reading:
                if use_hiragana:
                    reading = katakana_to_hiragana(reading)
                result.append(reading)
            else:
                # 記号・未知語などはそのまま残す
                result.append(surface)

            node = node.next

        return "".join(result)

    except Exception as e:
        print(f"MeCab変換エラー: {e}")
        return text


def preprocess_for_tts(text, convert_kanji=True, verbose=False):
    """
    TTS入力テキストをMeCabで前処理する。

    漢字を含む文章を読み仮名に変換することで、TTSモデルの
    誤読（音読み・訓読みの混同など）を防ぐ。

    Args:
        text: 処理する日本語テキスト
        convert_kanji: Trueのとき読み仮名変換を実行する
        verbose: Trueのとき変換前後のテキストを表示する

    Returns:
        前処理済みテキスト
    """
    if not convert_kanji or not MECAB_AVAILABLE:
        return text

    converted = convert_to_yomi(text, use_hiragana=True)

    if verbose:
        print(f"[MeCab] 変換前: {text}")
        print(f"[MeCab] 変換後: {converted}")

    return converted


def check_mecab():
    """MeCabの動作確認を行いバージョンと辞書情報を表示する"""
    if not MECAB_AVAILABLE:
        print("❌ MeCab Pythonバインディングが利用できません")
        return False

    try:
        tagger = _create_tagger()
        test_text = "漢字の読み方を確認します"
        result = convert_to_yomi(test_text, use_hiragana=True)
        print(f"✅ MeCab 動作確認OK")
        print(f"   辞書パス: {MECAB_DIC_DIR if os.path.exists(MECAB_DIC_DIR) else '(デフォルト)'}")
        print(f"   テスト: 「{test_text}」→「{result}」")
        return True
    except Exception as e:
        print(f"❌ MeCabエラー: {e}")
        return False


if __name__ == "__main__":
    check_mecab()
