"""
pyopenjtalk-plus を使った日本語テキスト前処理ユーティリティ

pyopenjtalk-plus (tsukumijima/pyopenjtalk-plus) は OpenJTalk の Python ラッパーで
MeCab より高精度なアクセント解析と読み変換が可能。
marine (DNN アクセント予測) をインストールすると更に高精度になる。

インストール:
    pip install pyopenjtalk-plus          # 基本
    pip install pyopenjtalk-plus marine   # DNN アクセント予測も使う場合
"""

try:
    import pyopenjtalk
    OPENJTALK_AVAILABLE = True
except ImportError:
    OPENJTALK_AVAILABLE = False
    print("警告: pyopenjtalk-plus が見つかりません。")
    print("  pip install pyopenjtalk-plus  でインストールしてください。")

# marine (DNN アクセント予測) の有無を確認
try:
    import marine  # noqa: F401
    MARINE_AVAILABLE = True
except ImportError:
    MARINE_AVAILABLE = False


def katakana_to_hiragana(text):
    """カタカナをひらがなに変換する（長音符・半濁音などはそのまま）"""
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
    pyopenjtalk-plus で日本語テキストを読み仮名に変換する。

    g2p(kana=True) でカタカナ読みを取得し、必要に応じてひらがなに変換する。
    アクセント辞書は jpreprocess 改善版 naist-jdic を使用。
    marine がインストール済みなら DNN ベースのアクセント予測が有効になる。

    Args:
        text: 変換対象の日本語テキスト
        use_hiragana: True=ひらがな出力 / False=カタカナ出力

    Returns:
        読み仮名に変換されたテキスト。pyopenjtalk-plus 未使用時は原文を返す。
    """
    if not OPENJTALK_AVAILABLE:
        return text

    try:
        kana = pyopenjtalk.g2p(text, kana=True)
        if use_hiragana:
            return katakana_to_hiragana(kana)
        return kana

    except Exception as e:
        print(f"pyopenjtalk 変換エラー: {e}")
        return text


def preprocess_for_tts(text, convert_kanji=True, verbose=False):
    """
    TTS 入力テキストを pyopenjtalk-plus で前処理する。

    漢字・数字・記号を含む文章を読み仮名に変換することで
    TTS モデルの誤読（音読み/訓読みの混同、数字読み間違いなど）を防ぐ。

    Args:
        text: 処理する日本語テキスト
        convert_kanji: True のとき読み仮名変換を実行する
        verbose: True のとき変換前後のテキストを表示する

    Returns:
        前処理済みテキスト
    """
    if not convert_kanji or not OPENJTALK_AVAILABLE:
        return text

    converted = convert_to_yomi(text, use_hiragana=True)

    if verbose:
        print(f"[pyopenjtalk] 変換前: {text}")
        print(f"[pyopenjtalk] 変換後: {converted}")

    return converted


def check_openjtalk():
    """pyopenjtalk-plus の動作確認を行いバージョンと機能情報を表示する"""
    if not OPENJTALK_AVAILABLE:
        print("❌ pyopenjtalk-plus が利用できません")
        return False

    try:
        test_cases = [
            ("漢字の読み方を確認します",   "かんじのよみかたをかくにんします"),
            ("東京都知事",               "とうきょうとちじ"),
            ("私は橋の上に立った",         "わたしははしのうえにたった"),
            ("今日は2025年5月3日です",     "きょうはにせんにじゅうごねんごがつみっかです"),
        ]

        print(f"✅ pyopenjtalk-plus 動作確認OK")
        print(f"   marine (DNN アクセント予測): {'有効' if MARINE_AVAILABLE else '無効（pip install marine で追加可能）'}")
        print()
        print("   変換テスト:")
        all_ok = True
        for src, expected in test_cases:
            result = convert_to_yomi(src, use_hiragana=True)
            ok = result == expected
            mark = "✅" if ok else "⚠️"
            print(f"   {mark} 「{src}」")
            print(f"      → 「{result}」")
            if not ok:
                print(f"      期待: 「{expected}」")
                all_ok = False

        return all_ok

    except Exception as e:
        print(f"❌ pyopenjtalk エラー: {e}")
        return False


if __name__ == "__main__":
    check_openjtalk()
