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
    print(f"[INFO] pyopenjtalk-plus 読み込み完了")
except Exception as _ojt_err:
    OPENJTALK_AVAILABLE = False
    print(f"[WARNING] pyopenjtalk-plus 読み込み失敗: {type(_ojt_err).__name__}: {_ojt_err}")


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
    A フィールドが 'xx' の場合はスキップして次のラベルを処理する。
    """
    phrases = []
    last_mora_pos = -1

    for label in labels:
        if not label.strip():
            continue

        # 現在音素を取得してサイレンス判定
        p_part = label.split("/")[0]
        try:
            current_phone = p_part.split("-")[1].split("+")[0]
        except (IndexError, AttributeError):
            continue
        if current_phone in ("sil", "pau", "xx", ""):
            last_mora_pos = -1
            continue

        # A フィールドは数値のみ受け付ける（xx は無視）
        m = re.search(r"/A:(-?\d+)\+(\d+)\+(\d+)/", label)
        if not m:
            continue

        accent_type = max(0, int(m.group(1)))
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

    def apply_user_dict_only(self, text: str) -> str:
        """
        ユーザー辞書の読み置換のみを適用する（pyopenjtalk の g2p 変換は行わない）。

        アクセント解析用途で使用。漢字はそのまま残し、登録済み固有名詞の
        表記だけ読み仮名に置換することで、MeCab の単語境界解析を正確に保つ。
        """
        result = text
        for key in sorted(self.user_dict, key=len, reverse=True):
            if key in result:
                result = result.replace(key, self.user_dict[key]["reading"])
        return result

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

    def _create_tagger(self, user_dic: str = None):
        """
        MeCab Tagger を作成する。
        Windows の "Program Files" パス（スペース含む）問題を避けるため引数なしで初期化。
        user_dic が指定された場合は -u オプションでユーザー辞書を追加。
        """
        try:
            if user_dic and os.path.exists(user_dic):
                return MeCab.Tagger(f'-u "{user_dic}"')
            return MeCab.Tagger()
        except Exception:
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

        # Step 3: 疑問文の末尾「?」「？」を保持してTTSへ上昇イントネーションを伝える
        # pyopenjtalk.g2p() は句読点を除去するため、元テキストが疑問符で終わる場合に「？」を再付与する
        orig_stripped = text.strip() if text else ""
        if orig_stripped.endswith(("?", "？")):
            if not result.endswith("？"):
                result = result.rstrip() + "？"
            if verbose:
                print("  ✅  疑問文を検出: TTS用テキスト末尾に「？」を保持")

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
#  全文アクセント記号付き文字列
# ══════════════════════════════════════════════════════════════

def get_full_accent_text(text: str) -> str:
    """
    テキスト全体のアクセント記号付きひらがな文字列を返す。
    アクセント句が検出できない場合はひらがな読みのみを返す。
    """
    if not OPENJTALK_AVAILABLE:
        return ""
    try:
        kana_all = _katakana_to_hiragana(pyopenjtalk.g2p(text, kana=True))
    except Exception:
        return ""
    try:
        phrases = get_accent_phrases(text)
        if phrases:
            return "　".join(p["marked_kana"] for p in phrases)
        return kana_all
    except Exception:
        return kana_all


# 除去する括弧類（アクセント解析前に除去してフレーズ分割を防ぐ）
_JP_BRACKETS = re.compile(r'[「」『』【】〔〕〈〉《》]')


def get_accent_text_with_user_dict(original_text: str, user_dict: dict = None) -> str:
    """
    user_dict を考慮した正確なアクセント記号付きテキストを生成する。

    元のテキスト（漢字混じり）を user_dict キーで分割し:
      - user_dict エントリ … accent_type を直接使ってアクセントマーク生成
      - それ以外のセグメント … pyopenjtalk（MeCab）で解析
    「」などの括弧類は除去してから pyopenjtalk に渡す。
    """
    if not OPENJTALK_AVAILABLE or not original_text.strip():
        return ""

    if not user_dict:
        return get_full_accent_text(original_text)

    # ① user_dict キーを長い順にソート（最長マッチ優先）
    sorted_keys = sorted(user_dict.keys(), key=len, reverse=True)

    # ② テキストを user_dict キー位置で分割
    segments = []   # [(text, is_dict_word, key_or_None), ...]
    remaining = original_text

    while remaining:
        earliest_idx = len(remaining)
        earliest_key = None

        for key in sorted_keys:
            idx = remaining.find(key)
            if 0 <= idx < earliest_idx:
                earliest_idx = idx
                earliest_key = key

        if earliest_key is None:
            segments.append((remaining, False, None))
            break

        if earliest_idx > 0:
            segments.append((remaining[:earliest_idx], False, None))
        segments.append((
            remaining[earliest_idx : earliest_idx + len(earliest_key)],
            True, earliest_key,
        ))
        remaining = remaining[earliest_idx + len(earliest_key):]

    # ③ 各セグメントを処理して結合
    result_parts = []

    for seg_text, is_dict, key in segments:
        if is_dict:
            entry       = user_dict[key]
            reading     = entry.get("reading", "")
            accent_type = int(entry.get("accent_type", 0))
            if reading:
                result_parts.append(_mark_accent(reading, accent_type))
        else:
            # 括弧類を除去してから pyopenjtalk に渡す
            clean = _JP_BRACKETS.sub("", seg_text).strip()
            if clean:
                try:
                    part = get_full_accent_text(clean)
                    if part:
                        result_parts.append(part)
                except Exception:
                    pass

    return "　".join(p for p in result_parts if p)


# ══════════════════════════════════════════════════════════════
#  MeCab アクセント辞書を使ったアクセント解析
#  （mecab_accent_tool.py でコンパイルした .dic を使用）
# ══════════════════════════════════════════════════════════════

def get_accent_from_mecab_dic(text: str, user_dic_path: str = None) -> str:
    """
    MeCab + アクセント辞書（.dic）でテキストを解析し、
    アクセント記号付きひらがな文字列を返す。

    - .dic に登録された単語: 14番目フィールド（accent_type）を直接使用
    - 未登録の単語:          pyopenjtalk でアクセント予測（利用可能な場合）

    Args:
        text:          解析対象テキスト
        user_dic_path: mecab_accent.dic のパス（None の場合は標準 MeCab のみ）

    Returns:
        str: 「　」区切りのアクセント記号付きひらがな（例: "で↑んのし↓ん　で↑す"）
             MeCab が利用できない場合は空文字列
    """
    if not MECAB_AVAILABLE or not text or not text.strip():
        return ""

    # MeCab Tagger 作成（引数なしでシステムデフォルト辞書を使用）
    try:
        if user_dic_path and os.path.exists(user_dic_path):
            tagger = MeCab.Tagger(f'-u "{user_dic_path}"')
        else:
            tagger = MeCab.Tagger()
    except Exception as e:
        print(f"[ERROR] MeCab Tagger 初期化失敗: {e}")
        return ""

    node = tagger.parseToNode(text)
    morphemes = []

    while node:
        surface = node.surface
        if not surface:
            node = node.next
            continue
        feats  = node.feature.split(",")
        pos    = feats[0] if feats else "?"
        if pos in ("BOS/EOS",):
            node = node.next
            continue
        # 読み（カタカナ → ひらがな）
        reading = feats[7] if len(feats) >= 8 and feats[7] not in ("*", "") else None
        # 14番目フィールド（index 13）= アクセント型
        accent_from_dic = None
        if len(feats) >= 14 and feats[13].lstrip("-").isdigit():
            accent_from_dic = max(0, int(feats[13]))
        morphemes.append({
            "surface":     surface,
            "reading":     reading,
            "accent_type": accent_from_dic,
        })
        node = node.next

    if not morphemes:
        return ""

    # 各形態素のアクセント記号付き読みを生成
    result_parts = []
    for m in morphemes:
        reading = m["reading"]
        if not reading:
            # 読みなし → 表層形そのまま
            result_parts.append(m["surface"])
            continue

        reading_hira = _katakana_to_hiragana(reading)

        if m["accent_type"] is not None:
            # MeCab 辞書にアクセント型あり → 直接使用
            result_parts.append(_mark_accent(reading_hira, m["accent_type"]))
        elif OPENJTALK_AVAILABLE:
            # アクセント型なし → pyopenjtalk で予測
            try:
                labels   = pyopenjtalk.extract_fullcontext(reading_hira)
                phrases  = _extract_phrase_info(labels)
                if phrases:
                    accent_type, _ = phrases[0]
                    result_parts.append(_mark_accent(reading_hira, accent_type))
                else:
                    result_parts.append(reading_hira)
            except Exception:
                result_parts.append(reading_hira)
        else:
            result_parts.append(reading_hira)

    return "　".join(result_parts)


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
