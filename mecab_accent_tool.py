# coding=utf-8
"""
MeCab アクセント辞書エディタ
=====================================
単語のアクセント情報を管理し、MeCab ユーザー辞書（.dic）に登録するツール。

起動方法:
  python mecab_accent_tool.py

機能:
  - 単語の表層形・読み・アクセント型を登録
  - pyopenjtalk-plus / marine でアクセント自動取得
  - MeCab CSV エクスポート → mecab-dict-index でコンパイル
  - user_dict.json からの一括インポート
  - TTS パイプライン（tts_preprocess.py）との連携
"""

import json
import os
import re
import subprocess
import sys

# ══════════════════════════════════════════════════════════════
#  パス設定
# ══════════════════════════════════════════════════════════════

SCRIPT_DIR       = os.path.dirname(os.path.abspath(__file__))
DICT_JSON        = os.path.join(SCRIPT_DIR, "mecab_accent_dict.json")
DICT_CSV         = os.path.join(SCRIPT_DIR, "mecab_accent_dict.csv")
DICT_DIC         = os.path.join(SCRIPT_DIR, "mecab_accent.dic")
USER_DICT_JSON   = os.path.join(SCRIPT_DIR, "user_dict.json")

MECAB_BIN_DIR    = r"C:\Program Files\MeCab\bin"
MECAB_DIC_DIR    = r"C:\Program Files\MeCab\dic\ipadic"
MECAB_DICT_INDEX = os.path.join(MECAB_BIN_DIR, "mecab-dict-index.exe")

# Windows: MeCab の DLL を PATH に追加
if sys.platform == "win32" and os.path.exists(MECAB_BIN_DIR):
    cur = os.environ.get("PATH", "")
    if MECAB_BIN_DIR not in cur:
        os.environ["PATH"] = MECAB_BIN_DIR + os.pathsep + cur

# ══════════════════════════════════════════════════════════════
#  ライブラリ読み込み
# ══════════════════════════════════════════════════════════════

try:
    import MeCab
    MECAB_AVAILABLE = True
except ImportError:
    MECAB_AVAILABLE = False
    print("[WARNING] MeCab が見つかりません")

try:
    import pyopenjtalk
    OPENJTALK_AVAILABLE = True
    print("[INFO] pyopenjtalk-plus 読み込み完了")
except ImportError:
    OPENJTALK_AVAILABLE = False
    print("[WARNING] pyopenjtalk が見つかりません。アクセント自動取得は利用できません")

# ══════════════════════════════════════════════════════════════
#  かな・アクセントユーティリティ
# ══════════════════════════════════════════════════════════════

_SMALL_KANA = set("ぁぃぅぇぉっゃゅょァィゥェォッャュョ")


def _katakana_to_hiragana(text: str) -> str:
    return "".join(
        chr(ord(ch) - 0x60) if 0x30A1 <= ord(ch) <= 0x30F6 else ch
        for ch in text
    )


def _hiragana_to_katakana(text: str) -> str:
    return "".join(
        chr(ord(ch) + 0x60) if 0x3041 <= ord(ch) <= 0x3096 else ch
        for ch in text
    )


def _split_morae(kana: str) -> list:
    morae, i = [], 0
    while i < len(kana):
        mora = kana[i]
        i += 1
        while i < len(kana) and kana[i] in _SMALL_KANA:
            mora += kana[i]
            i += 1
        morae.append(mora)
    return morae


def _make_pitch_list(accent_type: int, mora_count: int) -> list:
    n = mora_count
    if n == 0:
        return []
    if accent_type == 0:
        return ["L"] + ["H"] * (n - 1)
    if accent_type == 1:
        return ["H"] + ["L"] * (n - 1)
    acc = min(accent_type, n)
    return ["L"] + ["H"] * (acc - 1) + ["L"] * (n - acc)


def mark_accent(kana: str, accent_type: int) -> str:
    """かな文字列にアクセント記号（↑↓）を付与して返す"""
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


def accent_type_name(accent_type: int, mora_count: int) -> str:
    if accent_type == 0:
        return "平板型"
    if accent_type == 1:
        return "頭高型"
    if mora_count > 0 and accent_type >= mora_count:
        return "尾高型"
    return f"中高型({accent_type}拍)"


def count_morae(kana: str) -> int:
    return len(_split_morae(kana))


# ══════════════════════════════════════════════════════════════
#  アクセント自動取得（pyopenjtalk-plus）
# ══════════════════════════════════════════════════════════════

def _extract_phrase_info_from_labels(labels: list) -> list:
    """HTS ラベルから (accent_type, mora_count) のリストを抽出"""
    phrases = []
    last_mora_pos = -1
    for label in labels:
        if not label.strip():
            continue
        p_part = label.split("/")[0]
        try:
            current_phone = p_part.split("-")[1].split("+")[0]
        except (IndexError, AttributeError):
            continue
        if current_phone in ("sil", "pau", "xx", ""):
            last_mora_pos = -1
            continue
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


def get_accent_suggestion(reading_hiragana: str) -> tuple:
    """
    ひらがな読みからアクセント型を推定する。

    Returns:
        (accent_type: int, marked_kana: str, method: str)
    """
    if not OPENJTALK_AVAILABLE or not reading_hiragana.strip():
        return 0, reading_hiragana, "未取得（pyopenjtalk なし）"

    try:
        labels   = pyopenjtalk.extract_fullcontext(reading_hiragana)
        phrases  = _extract_phrase_info_from_labels(labels)
        kana_all = _katakana_to_hiragana(pyopenjtalk.g2p(reading_hiragana, kana=True))

        if phrases:
            accent_type, _ = phrases[0]
            marked = mark_accent(kana_all, accent_type)
            return accent_type, marked, "pyopenjtalk-plus"
        else:
            return 0, kana_all, "pyopenjtalk-plus (フレーズ未検出、平板型)"
    except Exception as e:
        return 0, reading_hiragana, f"エラー: {e}"


def get_accent_all_phrases(reading_hiragana: str) -> list:
    """
    全アクセント句の情報を返す（長い語や複合語向け）

    Returns:
        list of (accent_type, marked_kana, mora_count)
    """
    if not OPENJTALK_AVAILABLE or not reading_hiragana.strip():
        return []
    try:
        labels   = pyopenjtalk.extract_fullcontext(reading_hiragana)
        phrases  = _extract_phrase_info_from_labels(labels)
        kana_all = _katakana_to_hiragana(pyopenjtalk.g2p(reading_hiragana, kana=True))
        morae    = _split_morae(kana_all)

        result, idx = [], 0
        for accent_type, mora_count in phrases:
            chunk = morae[idx : idx + mora_count]
            if chunk:
                kana   = "".join(chunk)
                marked = mark_accent(kana, accent_type)
                result.append((accent_type, marked, len(chunk)))
            idx += mora_count
        return result
    except Exception:
        return []


# ══════════════════════════════════════════════════════════════
#  辞書ファイル管理
# ══════════════════════════════════════════════════════════════

def load_dict() -> dict:
    """mecab_accent_dict.json を読み込む"""
    if not os.path.exists(DICT_JSON):
        return {}
    try:
        with open(DICT_JSON, encoding="utf-8") as f:
            data = json.load(f)
        return data.get("entries", {})
    except Exception as e:
        print(f"[ERROR] 辞書読み込みエラー: {e}")
        return {}


def save_dict(entries: dict):
    """辞書を mecab_accent_dict.json に保存する"""
    data = {"_version": "1.0", "_comment": "MeCab アクセント辞書", "entries": entries}
    with open(DICT_JSON, encoding="utf-8", mode="w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[INFO] 辞書保存: {DICT_JSON} ({len(entries)} 件)")


def import_from_user_dict_json(path: str, entries: dict) -> tuple:
    """
    既存の user_dict.json から一括インポートする

    Returns:
        (entries, status_message)
    """
    path = path.strip()
    if not os.path.exists(path):
        return entries, f"❌ ファイルが見つかりません: {path}"
    try:
        with open(path, encoding="utf-8") as f:
            user_dict = json.load(f)
    except Exception as e:
        return entries, f"❌ 読み込みエラー: {e}"

    imported = skipped = 0
    for surface, info in user_dict.items():
        if surface.startswith("_"):
            continue
        reading_hira = info.get("reading", "").strip()
        if not reading_hira:
            skipped += 1
            continue
        reading_kata = _hiragana_to_katakana(reading_hira)
        accent_type  = int(info.get("accent_type", 0))
        mora_count   = count_morae(reading_hira)
        marked       = mark_accent(reading_hira, accent_type)

        entries[surface] = {
            "surface":          surface,
            "reading_hiragana": reading_hira,
            "reading_katakana": reading_kata,
            "pos":              "名詞,固有名詞,一般",
            "left_id":          1288,
            "right_id":         1288,
            "cost":             5000,
            "accent_type":      accent_type,
            "mora_count":       mora_count,
            "marked_kana":      marked,
            "type_name":        accent_type_name(accent_type, mora_count),
            "note":             info.get("note", ""),
        }
        imported += 1

    return entries, f"✅ {imported} 件インポート完了（スキップ: {skipped} 件）"


# ══════════════════════════════════════════════════════════════
#  MeCab CSV エクスポート & コンパイル
# ══════════════════════════════════════════════════════════════

# 品詞 → (left_id, right_id) マッピング（ipadic 標準値）
_POS_IDS = {
    "名詞,固有名詞,一般":   (1288, 1288),
    "名詞,固有名詞,人名":   (1289, 1289),
    "名詞,固有名詞,地名":   (1293, 1293),
    "名詞,一般":            (1285, 1285),
    "名詞,サ変接続":        (1282, 1282),
    "名詞,形容動詞語幹":    (1283, 1283),
}


def export_csv(entries: dict) -> str:
    """
    MeCab ユーザー辞書 CSV を生成して DICT_CSV に保存する。

    CSV フォーマット（ipadic 拡張、14フィールド）:
      表層形,左ID,右ID,コスト,品詞,品詞細分類1,品詞細分類2,品詞細分類3,
      活用型,活用形,原形,読み（カタカナ）,発音（カタカナ）,アクセント型
    """
    lines = []
    for surface, e in sorted(entries.items(), key=lambda x: x[0]):
        pos_str   = e.get("pos", "名詞,固有名詞,一般")
        pos_parts = pos_str.split(",")
        while len(pos_parts) < 6:
            pos_parts.append("*")

        left_id  = e.get("left_id",  _POS_IDS.get(pos_str, (1288, 1288))[0])
        right_id = e.get("right_id", _POS_IDS.get(pos_str, (1288, 1288))[1])

        row = [
            e["surface"],           # 表層形
            str(left_id),           # 左文脈ID
            str(right_id),          # 右文脈ID
            str(e.get("cost", 5000)), # コスト
            pos_parts[0],           # 品詞
            pos_parts[1] if len(pos_parts) > 1 else "*",  # 品詞細分類1
            pos_parts[2] if len(pos_parts) > 2 else "*",  # 品詞細分類2
            pos_parts[3] if len(pos_parts) > 3 else "*",  # 品詞細分類3
            "*",                    # 活用型
            "*",                    # 活用形
            e["surface"],           # 原形
            e.get("reading_katakana", ""),   # 読み
            e.get("reading_katakana", ""),   # 発音
            str(e.get("accent_type", 0)),    # ★ アクセント型（14番目）
        ]
        lines.append(",".join(row))

    csv_text = "\n".join(lines)
    with open(DICT_CSV, encoding="utf-8", mode="w", newline="\n") as f:
        f.write(csv_text)
    return csv_text


def compile_dic() -> str:
    """
    mecab-dict-index を使って CSV → .dic ファイルにコンパイルする。
    """
    if not os.path.exists(MECAB_DICT_INDEX):
        return (
            f"❌ mecab-dict-index が見つかりません:\n{MECAB_DICT_INDEX}\n"
            f"MeCab がインストールされているか確認してください。"
        )
    if not os.path.exists(DICT_CSV):
        return "❌ CSV ファイルが見つかりません。先に「CSV を生成」してください。"
    if not os.path.exists(MECAB_DIC_DIR):
        return f"❌ MeCab 辞書ディレクトリが見つかりません:\n{MECAB_DIC_DIR}"

    cmd = [
        MECAB_DICT_INDEX,
        "-d", MECAB_DIC_DIR,
        "-u", DICT_DIC,
        "-f", "utf-8",
        "-t", "utf-8",
        DICT_CSV,
    ]
    print(f"[INFO] コンパイル実行: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True,
            encoding="utf-8", errors="replace",
        )
        if result.returncode == 0:
            size = os.path.getsize(DICT_DIC)
            return (
                f"✅ コンパイル成功！\n"
                f"出力: {DICT_DIC}\n"
                f"サイズ: {size:,} バイト\n\n"
                f"次のステップ:\n"
                f"tts_preprocess.py の MeCab 呼び出しに以下を追加します:\n"
                f"  MeCab.Tagger(\"-d {MECAB_DIC_DIR} -u {DICT_DIC}\")"
            )
        else:
            return f"❌ コンパイルエラー:\n{result.stderr or result.stdout}"
    except Exception as e:
        return f"❌ 実行エラー: {type(e).__name__}: {e}"


# ══════════════════════════════════════════════════════════════
#  MeCab アクセント読み取り（TTS パイプライン連携）
# ══════════════════════════════════════════════════════════════

def get_accent_from_mecab(text: str, user_dic_path: str = None) -> str:
    """
    MeCab でテキストを解析し、アクセント記号付きひらがな文字列を返す。

    - MeCab ユーザー辞書（14番目フィールド）にアクセント型がある単語:
        その値を使用
    - アクセント型がない単語:
        pyopenjtalk で予測（利用可能な場合）

    Returns:
        str: アクセント記号付きひらがな（例: "で↑んの↓しん"）
    """
    if not MECAB_AVAILABLE:
        return ""

    # MeCab Tagger 作成
    tagger_args = f"-d {MECAB_DIC_DIR}"
    if user_dic_path and os.path.exists(user_dic_path):
        tagger_args += f" -u {user_dic_path}"
    try:
        tagger = MeCab.Tagger(tagger_args)
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

        feats   = node.feature.split(",")
        pos     = feats[0] if feats else "?"
        reading = feats[7] if len(feats) >= 8 and feats[7] not in ("*", "") else None
        # 14番目フィールド（インデックス 13）= アクセント型（ユーザー辞書で付与）
        accent_from_dic = None
        if len(feats) >= 14 and feats[13].lstrip("-").isdigit():
            accent_from_dic = max(0, int(feats[13]))

        if pos in ("BOS/EOS",):
            node = node.next
            continue

        morphemes.append({
            "surface":       surface,
            "reading":       reading,
            "pos":           pos,
            "accent_type":   accent_from_dic,
        })
        node = node.next

    # 各形態素のアクセント記号付き読みを生成
    result_parts = []
    for m in morphemes:
        reading = m["reading"]
        if not reading:
            result_parts.append(m["surface"])
            continue

        reading_hira = _katakana_to_hiragana(reading)

        if m["accent_type"] is not None:
            # MeCab 辞書にアクセント型あり → そのまま使用
            marked = mark_accent(reading_hira, m["accent_type"])
            result_parts.append(marked)
        elif OPENJTALK_AVAILABLE:
            # アクセント型なし → pyopenjtalk で予測
            try:
                accent_type, marked, _ = get_accent_suggestion(reading_hira)
                result_parts.append(marked)
            except Exception:
                result_parts.append(reading_hira)
        else:
            result_parts.append(reading_hira)

    return "　".join(result_parts)


# ══════════════════════════════════════════════════════════════
#  Gradio UI
# ══════════════════════════════════════════════════════════════

import gradio as gr

# グローバル辞書ステート
_entries: dict = load_dict()


def _format_table(entries: dict) -> list:
    """辞書エントリをテーブル用リストに変換"""
    rows = []
    for surface, e in sorted(entries.items()):
        rows.append([
            surface,
            e.get("reading_hiragana", ""),
            str(e.get("accent_type", 0)),
            e.get("marked_kana", ""),
            e.get("type_name", ""),
            e.get("note", ""),
        ])
    return rows


POS_CHOICES = [
    "名詞,固有名詞,一般",
    "名詞,固有名詞,人名",
    "名詞,固有名詞,地名",
    "名詞,一般",
    "名詞,サ変接続",
]


def ui_auto_accent(reading_hira: str):
    reading_hira = reading_hira.strip()
    if not reading_hira:
        return "0", "", "", "読みを入力してください"

    accent_type, marked, method = get_accent_suggestion(reading_hira)
    mora_count = count_morae(reading_hira)
    type_name  = accent_type_name(accent_type, mora_count)

    # 全フレーズ情報も取得
    phrases = get_accent_all_phrases(reading_hira)
    phrase_info = ""
    if len(phrases) > 1:
        phrase_info = "\n全フレーズ: " + " / ".join(
            f"{mk}（type={at},{mc}mora）" for at, mk, mc in phrases
        )

    return (
        str(accent_type),
        marked,
        f"{type_name}（{mora_count}拍）{phrase_info}",
        f"取得方法: {method}",
    )


def ui_preview(reading_hira: str, accent_str: str):
    reading_hira = (reading_hira or "").strip()
    if not reading_hira:
        return ""
    try:
        at = int(accent_str)
    except (ValueError, TypeError):
        return ""
    mc = count_morae(reading_hira)
    return f"{mark_accent(reading_hira, at)}  [{accent_type_name(at, mc)}, {mc}拍]"


def ui_add_entry(surface, reading_hira, accent_str, pos, note):
    """追加/更新して (status, table, table) を返す（Tab①・Tab②の両テーブル更新用）"""
    global _entries
    surface      = (surface or "").strip()
    reading_hira = (reading_hira or "").strip()

    if not surface:
        t = _format_table(_entries)
        return "❌ 表層形を入力してください", t, t
    if not reading_hira:
        t = _format_table(_entries)
        return "❌ 読み（ひらがな）を入力してください", t, t

    try:
        accent_type = int(accent_str)
    except (ValueError, TypeError):
        t = _format_table(_entries)
        return "❌ アクセント型は 0 以上の整数で入力してください", t, t

    reading_kata = _hiragana_to_katakana(reading_hira)
    mora_count   = count_morae(reading_hira)
    marked       = mark_accent(reading_hira, accent_type)
    type_name    = accent_type_name(accent_type, mora_count)
    left_id, right_id = _POS_IDS.get(pos, (1288, 1288))

    _entries[surface] = {
        "surface":          surface,
        "reading_hiragana": reading_hira,
        "reading_katakana": reading_kata,
        "pos":              pos,
        "left_id":          left_id,
        "right_id":         right_id,
        "cost":             5000,
        "accent_type":      accent_type,
        "mora_count":       mora_count,
        "marked_kana":      marked,
        "type_name":        type_name,
        "note":             (note or "").strip(),
    }
    save_dict(_entries)
    t = _format_table(_entries)
    return (
        f"✅ 追加: 「{surface}」→「{marked}」（{type_name}）",
        t,
        t,
    )


def ui_delete_entry(surface: str):
    """削除して (status, table, table) を返す（Tab①・Tab②の両テーブル更新用）"""
    global _entries
    surface = (surface or "").strip()
    t_prev = _format_table(_entries)
    if surface in _entries:
        del _entries[surface]
        save_dict(_entries)
        t = _format_table(_entries)
        return f"✅ 削除: 「{surface}」", t, t
    return f"❌ 見つかりません: 「{surface}」", t_prev, t_prev


def ui_import(path: str):
    """インポートして (status, table, table) を返す（Tab①・Tab②の両テーブル更新用）"""
    global _entries
    _entries, msg = import_from_user_dict_json(path, _entries)
    save_dict(_entries)
    t = _format_table(_entries)
    return msg, t, t


def ui_export():
    global _entries
    if not _entries:
        return "❌ 辞書が空です。単語を追加してください。"
    csv_text = export_csv(_entries)
    lines = csv_text.split("\n")
    preview = "\n".join(lines[:10])
    if len(lines) > 10:
        preview += f"\n... （合計 {len(lines)} 件）"
    return f"✅ CSV 生成完了: {DICT_CSV}\n\n{preview}"


def ui_compile():
    global _entries
    if not _entries:
        return "❌ 辞書が空です。先に CSV を生成してください。"
    # CSV がなければ自動生成
    if not os.path.exists(DICT_CSV):
        export_csv(_entries)
    return compile_dic()


def ui_test_mecab(text: str):
    result = get_accent_from_mecab(text.strip(), DICT_DIC)
    if result:
        return f"MeCab アクセント解析結果:\n{result}"
    return "結果なし（MeCab またはアクセント辞書が利用できません）"


def ui_refresh_table():
    """両テーブル用に同じデータを2つ返す"""
    t = _format_table(_entries)
    return t, t


# ──────────────────────────────────────────────────────────────
#  UI 構築
# ──────────────────────────────────────────────────────────────

_TABLE_HEADERS = ["表層形", "読み（ひらがな）", "アクセント型", "アクセント記号", "型名", "メモ"]

with gr.Blocks(title="MeCab アクセント辞書エディタ", theme=gr.themes.Soft()) as app:

    gr.Markdown(
        "# MeCab アクセント辞書エディタ\n"
        "単語のアクセント情報を管理し、MeCab ユーザー辞書（.dic）に登録します。"
    )

    # ──────────────────────────────────────────
    with gr.Tab("① 単語追加・編集"):
        gr.Markdown("### 単語のアクセント型を登録します")
        with gr.Row():
            with gr.Column(scale=2):
                surface_in   = gr.Textbox(label="表層形（漢字・原文）", placeholder="例: 伝の心")
                reading_in   = gr.Textbox(label="読み（ひらがな）",     placeholder="例: でんのしん")
                with gr.Row():
                    accent_in = gr.Textbox(label="アクセント型（数値）", value="0", scale=1)
                    auto_btn  = gr.Button("pyopenjtalk で自動取得", variant="secondary", scale=2)
                pos_in       = gr.Dropdown(label="品詞", choices=POS_CHOICES, value=POS_CHOICES[0])
                note_in      = gr.Textbox(label="メモ（任意）", placeholder="例: 重度障害者用意思伝達装置")
                add_btn      = gr.Button("辞書に追加 / 更新", variant="primary")
                add_status   = gr.Textbox(label="ステータス", interactive=False)

            with gr.Column(scale=1):
                gr.Markdown("#### アクセント確認")
                accent_preview = gr.Textbox(
                    label="プレビュー（↑=上昇 ↓=下降）",
                    interactive=False,
                    lines=2,
                )
                accent_info  = gr.Textbox(label="型名・モーラ数", interactive=False)
                auto_method  = gr.Textbox(label="取得方法", interactive=False)
                gr.Markdown(
                    "**アクセント型の意味:**\n"
                    "- `0` = 平板型（お↑かねもち）\n"
                    "- `1` = 頭高型（あ↓たま）\n"
                    "- `N` = 中高型（N拍目まで高）\n"
                    "- N=モーラ数 = 尾高型\n\n"
                    "↑ = 低→高（上昇）\n"
                    "↓ = 高→低（下降）"
                )

        # Tab① にも辞書テーブルを表示（追加後すぐ確認できるように）
        entry_table_1 = gr.Dataframe(
            headers=_TABLE_HEADERS,
            value=_format_table(_entries),
            interactive=False,
            label="現在の辞書（追加後に自動更新）",
        )

    # ──────────────────────────────────────────
    with gr.Tab("② 辞書一覧・削除"):
        dict_table = gr.Dataframe(
            headers=_TABLE_HEADERS,
            value=_format_table(_entries),
            interactive=False,
            label="登録済み単語一覧",
        )
        refresh_btn = gr.Button("一覧を更新")

        gr.Markdown("---")
        with gr.Row():
            delete_in  = gr.Textbox(label="削除する表層形", placeholder="例: 伝の心")
            delete_btn = gr.Button("削除", variant="stop")
        delete_status = gr.Textbox(label="削除結果", interactive=False)

        gr.Markdown("---")
        gr.Markdown("### user_dict.json からの一括インポート")
        with gr.Row():
            import_path = gr.Textbox(
                label="user_dict.json のパス",
                value=USER_DICT_JSON,
                scale=3,
            )
            import_btn    = gr.Button("インポート", scale=1)
        import_status = gr.Textbox(label="インポート結果", interactive=False)

    # ──────────────────────────────────────────
    with gr.Tab("③ エクスポート・コンパイル"):
        gr.Markdown(
            "### MeCab ユーザー辞書のビルド手順\n\n"
            "1. **CSV を生成** → 辞書内容を CSV ファイルに書き出す\n"
            "2. **MeCab .dic にコンパイル** → mecab-dict-index で .dic を生成\n"
            "3. **TTS パイプラインで使用** → tts_preprocess.py が .dic を自動読み込み"
        )
        with gr.Row():
            export_btn  = gr.Button("① CSV を生成",           variant="secondary", scale=1)
            compile_btn = gr.Button("② MeCab .dic にコンパイル", variant="primary",   scale=1)
        export_out  = gr.Textbox(label="CSV 生成結果",  lines=8, interactive=False)
        compile_out = gr.Textbox(label="コンパイル結果", lines=6, interactive=False)
        gr.Markdown("---")
        gr.Markdown(
            f"**出力ファイル:**\n"
            f"- CSV: `{DICT_CSV}`\n"
            f"- DIC: `{DICT_DIC}`\n\n"
            f"**コンパイルコマンド（参考）:**\n"
            f"```\n"
            f'"{MECAB_DICT_INDEX}" -d "{MECAB_DIC_DIR}" '
            f'-u "{DICT_DIC}" -f utf-8 -t utf-8 "{DICT_CSV}"\n'
            f"```"
        )

    # ──────────────────────────────────────────
    with gr.Tab("④ TTS テスト"):
        gr.Markdown(
            "### MeCab アクセント辞書を使ったアクセント解析テスト\n"
            "コンパイル済みの `.dic` ファイルを使って、テキストのアクセントを確認できます。"
        )
        test_text_in = gr.Textbox(
            label="テストテキスト",
            lines=3,
            placeholder="例: 伝の心やオペレートナビは意思伝達装置です。",
            value="伝の心やオペレートナビは意思伝達装置です。",
        )
        test_btn = gr.Button("アクセント解析（MeCab）", variant="primary")
        test_out = gr.Textbox(label="解析結果", lines=4, interactive=False)
        gr.Markdown(
            f"使用する辞書: `{DICT_DIC}`\n\n"
            "**注意:** コンパイル済みの .dic ファイルがない場合は結果が出ません。\n"
            "先に「③ エクスポート・コンパイル」タブでコンパイルしてください。"
        )

    # ══════════════════════════════════════════════════════════════
    #  イベントハンドラ（全コンポーネント定義後にまとめて登録）
    # ══════════════════════════════════════════════════════════════

    # Tab① イベント
    auto_btn.click(
        fn=ui_auto_accent,
        inputs=[reading_in],
        outputs=[accent_in, accent_preview, accent_info, auto_method],
    )
    reading_in.change(
        fn=ui_preview,
        inputs=[reading_in, accent_in],
        outputs=[accent_preview],
    )
    accent_in.change(
        fn=ui_preview,
        inputs=[reading_in, accent_in],
        outputs=[accent_preview],
    )
    # 追加 → Tab①・Tab②の両テーブルを更新
    add_btn.click(
        fn=ui_add_entry,
        inputs=[surface_in, reading_in, accent_in, pos_in, note_in],
        outputs=[add_status, entry_table_1, dict_table],
    )

    # Tab② イベント
    refresh_btn.click(fn=ui_refresh_table, outputs=[entry_table_1, dict_table])
    # 削除 → Tab①・Tab②の両テーブルを更新
    delete_btn.click(
        fn=ui_delete_entry,
        inputs=[delete_in],
        outputs=[delete_status, entry_table_1, dict_table],
    )
    # インポート → Tab①・Tab②の両テーブルを更新
    import_btn.click(
        fn=ui_import,
        inputs=[import_path],
        outputs=[import_status, entry_table_1, dict_table],
    )

    # Tab③ イベント
    export_btn.click(fn=ui_export, outputs=[export_out])
    compile_btn.click(fn=ui_compile, outputs=[compile_out])

    # Tab④ イベント
    test_btn.click(fn=ui_test_mecab, inputs=[test_text_in], outputs=[test_out])


if __name__ == "__main__":
    print(f"[INFO] MeCab アクセント辞書エディタ 起動中...")
    print(f"[INFO] 辞書ファイル: {DICT_JSON}")
    print(f"[INFO] 登録済み: {len(_entries)} 件")
    app.launch(server_name="127.0.0.1", server_port=7861)
