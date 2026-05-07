"""
TTS 前処理: MeCab (Pass 1) + pyopenjtalk-plus (Pass 2) の 2 パス処理

Pass 1: MeCab で形態素解析し、未知語・固有名詞・ユーザー辞書マッチを検出
Pass 2: user_dict.json を適用後、pyopenjtalk-plus で読み変換＋アクセント解析
"""

import json
import os
import re
import sys

# ── MeCab (Pass 1) ──────────────────────────────────────────
MECAB_BIN_DIR = r"C:\Program Files\MeCab\bin"
MECAB_DIC_DIR = r"C:\Program Files\MeCab\dic\ipadic"

if sys.platform == "win32" and os.path.exists(MECAB_BIN_DIR):
    current = os.environ.get("PATH", "")
    if MECAB_BIN_DIR not in current:
        os.environ["PATH"] = MECAB_BIN_DIR + os.pathsep + current

try:
    import MeCab
    MECAB_AVAILABLE = True
except ImportError:
    MECAB_AVAILABLE = False

# ── pyopenjtalk-plus (Pass 2) ───────────────────────────────
try:
    import pyopenjtalk
    OPENJTALK_AVAILABLE = True
except ImportError:
    OPENJTALK_AVAILABLE = False


# ══════════════════════════════════════════════════════════════
#  ユーティリティ（モーラ・アクセント）
# ══════════════════════════════════════════════════════════════

_SMALL_KANA = set("ぁぃぅぇぉっゃゅょァィゥェォッャュョ")


def _katakana_to_hiragana(text):
    return "".join(
        chr(ord(ch) - 0x60) if 0x30A1 <= ord(ch) <= 0x30F6 else ch
        for ch in text
    )


def _split_morae(kana):
    """かな文字列をモーラのリストに分割する（拗音は前の文字に結合）"""
    morae, i = [], 0
    while i < len(kana):
        mora = kana[i]
        i += 1
        while i < len(kana) and kana[i] in _SMALL_KANA:
            mora += kana[i]
            i += 1
        morae.append(mora)
    return morae


def _make_pitch_list(accent_type, mora_count):
    """
    アクセント型からモーラごとの H/L ピッチ列を返す。

    東京式アクセントの規則:
      type 0 (平板型) : L H H H ... H
      type 1 (頭高型) : H L L L ... L
      type N (N>=2)   : L H H...H L L ... L  (N拍目まで H)
    """
    n = mora_count
    if n == 0:
        return []
    if accent_type == 0:
        return ["L"] + ["H"] * (n - 1)
    if accent_type == 1:
        return ["H"] + ["L"] * (n - 1)
    acc = min(accent_type, n)
    return ["L"] + ["H"] * (acc - 1) + ["L"] * (n - acc)


def _mark_accent(kana, accent_type):
    """かな文字列にピッチ変化マーク（↑↓）を付与して返す"""
    morae = _split_morae(kana)
    n = len(morae)
    if n == 0:
        return kana

    pitches = _make_pitch_list(accent_type, n)
    result = [morae[0]]
    for i in range(1, n):
        if pitches[i - 1] == "L" and pitches[i] == "H":
            result.append("↑")
        elif pitches[i - 1] == "H" and pitches[i] == "L":
            result.append("↓")
        result.append(morae[i])
    return "".join(result)


def _accent_type_name(accent_type, mora_count):
    if accent_type == 0:
        return "平板型"
    if accent_type == 1:
        return "頭高型"
    if accent_type >= mora_count:
        return "尾高型"
    return f"中高型({accent_type}拍)"


def _extract_phrase_info(labels):
    """
    HTS ラベルリストから [(accent_type, mora_count), ...] を抽出する。

    A フィールド書式: /A:accent_type+mora_pos+mora_count/
    mora_pos が 1 にリセットされたタイミングで新フレーズ開始と判定する。
    """
    phrases = []
    last_mora_pos = -1

    for label in labels:
        if not label.strip():
            continue
        if "-sil" in label or "-pau" in label:
            last_mora_pos = -1
            continue

        m = re.search(r"/A:(\d+)\+(\d+)\+(\d+)/", label)
        if not m:
            continue

        accent_type = int(m.group(1))
        mora_pos    = int(m.group(2))
        mora_count  = int(m.group(3))

        if mora_pos == 1 and last_mora_pos != 1:
            phrases.append((accent_type, mora_count))

        last_mora_pos = mora_pos

    return phrases


def get_accent_phrases(text):
    """
    テキストのアクセント句情報を返す。

    Returns:
        list of {kana, accent_type, mora_count, marked_kana, type_name}
    """
    if not OPENJTALK_AVAILABLE:
        return []

    labels   = pyopenjtalk.extract_fullcontext(text)
    kana_all = _katakana_to_hiragana(pyopenjtalk.g2p(text, kana=True))

    phrase_info = _extract_phrase_info(labels)
    morae_all   = _split_morae(kana_all)

    result, idx = [], 0
    for accent_type, mora_count in phrase_info:
        chunk = morae_all[idx : idx + mora_count]
        if chunk:
            kana = "".join(chunk)
            result.append({
                "kana":       kana,
                "accent_type": accent_type,
                "mora_count":  len(chunk),
                "marked_kana": _mark_accent(kana, accent_type),
                "type_name":   _accent_type_name(accent_type, len(chunk)),
            })
        idx += mora_count

    # モーラ数ズレの吸収
    if idx < len(morae_all):
        tail = "".join(morae_all[idx:])
        if result:
            result[-1]["kana"] += tail
            result[-1]["marked_kana"] = _mark_accent(result[-1]["kana"], result[-1]["accent_type"])
        else:
            result.append({
                "kana": tail, "accent_type": 0, "mora_count": len(morae_all[idx:]),
                "marked_kana": tail, "type_name": "平板型",
            })

    return result


# ══════════════════════════════════════════════════════════════
#  TTSPreprocessor
# ══════════════════════════════════════════════════════════════

class TTSPreprocessor:
    """
    2 パス TTS 前処理クラス。

    使い方:
        pre = TTSPreprocessor("user_dict.json")
        pre.print_analysis(text)          # Pass 1: 要確認語を表示
        tts_text = pre.convert(text)      # Pass 2: 読み変換
        pre.show_accent(tts_text)         # アクセント解析表示
    """

    def __init__(self, user_dict_path="user_dict.json"):
        self.user_dict_path = user_dict_path
        self.user_dict = self._load_user_dict(user_dict_path)

    # ── 辞書 ──────────────────────────────────────────────

    def _load_user_dict(self, path):
        if not os.path.exists(path):
            return {}
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            return {k: v for k, v in data.items() if not k.startswith("_")}
        except Exception as e:
            print(f"ユーザー辞書読み込みエラー: {e}")
            return {}

    def reload_user_dict(self):
        """user_dict.json を再読み込みする（単語登録後に呼ぶ）"""
        self.user_dict = self._load_user_dict(self.user_dict_path)
        print(f"✅ ユーザー辞書を再読み込みしました（{len(self.user_dict)} 件）")

    def _find_user_dict_matches(self, text):
        """テキストにマッチするユーザー辞書エントリを長い順で返す"""
        return [k for k in sorted(self.user_dict, key=len, reverse=True) if k in text]

    # ── Pass 1: MeCab 形態素解析 ───────────────────────────

    def _create_tagger(self):
        if os.path.exists(MECAB_DIC_DIR):
            return MeCab.Tagger(f"-d {MECAB_DIC_DIR}")
        return MeCab.Tagger()

    def analyze_text(self, text):
        """
        Pass 1: MeCab で形態素解析し、形態素リストを返す。

        各要素: {surface, reading, pos, needs_review, reason}
        """
        if not MECAB_AVAILABLE:
            return []

        tagger = self._create_tagger()
        node   = tagger.parseToNode(text)
        result = []

        while node:
            surface = node.surface
            if not surface:
                node = node.next
                continue

            feats   = node.feature.split(",")
            pos     = feats[0] if feats else "?"
            pos2    = feats[1] if len(feats) > 1 else "?"
            reading = feats[7] if len(feats) >= 8 and feats[7] not in ("*", "") else None

            reasons = []
            if reading is None:
                reasons.append("読み不明（未知語）")
            if pos == "名詞" and pos2 == "固有名詞":
                reasons.append("固有名詞")

            result.append({
                "surface":      surface,
                "reading":      reading or "?",
                "pos":          f"{pos}-{pos2}",
                "needs_review": bool(reasons),
                "reason":       " / ".join(reasons),
            })
            node = node.next

        return result

    def print_analysis(self, text):
        """Pass 1 の解析結果・要確認語・ユーザー辞書マッチを表示する"""
        print("\n" + "=" * 60)
        print("[Pass 1] MeCab 形態素解析")
        print("=" * 60)

        if not MECAB_AVAILABLE:
            print("⚠️  MeCab が利用できません")
            return

        morphemes = self.analyze_text(text)
        issues    = []

        for m in morphemes:
            mark = "⚠️ " if m["needs_review"] else "   "
            line = f"  {mark}{m['surface']:12}{m['reading']:12}[{m['pos']}]"
            if m["reason"]:
                line += f"  ← {m['reason']}"
            print(line)
            if m["needs_review"]:
                issues.append(m)

        # ユーザー辞書マッチ
        matches = self._find_user_dict_matches(text)
        if matches:
            print()
            print("  [ユーザー辞書マッチ]")
            for k in matches:
                e = self.user_dict[k]
                note = e.get("note", "")
                print(f"    「{k}」→「{e['reading']}」  {note}")

        print()
        if issues:
            print(f"  ⚠️  要確認語: {len(issues)} 件")
            print(f"  → {self.user_dict_path} に正しい読みを登録後、reload_user_dict() を呼んでください")
        else:
            print("  ✅ 要確認語なし")

        print("=" * 60)

    # ── Pass 2: 読み変換 ──────────────────────────────────

    def convert(self, text, verbose=True):
        """
        Pass 2: ユーザー辞書を適用し、pyopenjtalk-plus で読み変換する。

        Returns:
            str: TTS 用ひらがなテキスト
        """
        if verbose:
            print("\n" + "=" * 60)
            print("[Pass 2] 読み変換")
            print("=" * 60)

        # Step 1: ユーザー辞書を最長マッチで適用
        result = text
        for key in sorted(self.user_dict, key=len, reverse=True):
            if key in result:
                reading = self.user_dict[key]["reading"]
                result  = result.replace(key, reading)
                if verbose:
                    print(f"  ユーザー辞書: 「{key}」→「{reading}」")

        # Step 2: pyopenjtalk-plus で残りを変換
        if OPENJTALK_AVAILABLE:
            try:
                kana   = pyopenjtalk.g2p(result, kana=True)
                result = _katakana_to_hiragana(kana)
            except Exception as e:
                print(f"  ⚠️  pyopenjtalk エラー: {e}")
        elif verbose:
            print("  ⚠️  pyopenjtalk-plus が利用できません。ユーザー辞書適用のみ実施")

        if verbose:
            print(f"  変換結果: 「{result}」")
            print("=" * 60)

        return result

    # ── アクセント解析 ────────────────────────────────────

    def show_accent(self, text):
        """テキストのアクセント句を解析して↑↓マーク付きで表示する"""
        print("\n" + "=" * 60)
        print("[アクセント解析]  （↑=ピッチ上昇  ↓=ピッチ下降）")
        print("=" * 60)

        if not OPENJTALK_AVAILABLE:
            print("⚠️  pyopenjtalk-plus が利用できません")
            print("=" * 60)
            return

        try:
            phrases = get_accent_phrases(text)
            if not phrases:
                print("  (解析結果なし)")
            else:
                for p in phrases:
                    print(
                        f"  {p['marked_kana']:25}  {p['type_name']:12}"
                        f"  [type={p['accent_type']}, {p['mora_count']}mora]"
                    )
        except Exception as e:
            print(f"  アクセント解析エラー: {e}")

        print("=" * 60)


# ══════════════════════════════════════════════════════════════
#  動作確認
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    TEST_TEXT = "伝の心やオペレートナビは重度障害者用意思伝達装置です。"

    pre = TTSPreprocessor("user_dict.json")

    # Pass 1
    pre.print_analysis(TEST_TEXT)

    # Pass 2
    tts_text = pre.convert(TEST_TEXT)

    # アクセント
    pre.show_accent(tts_text)
