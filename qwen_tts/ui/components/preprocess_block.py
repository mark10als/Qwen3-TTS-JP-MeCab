# coding=utf-8
"""
共有前処理ブロック: MeCab + pyopenjtalk-plus による日本語テキスト前処理

全タブから使用する共通コンポーネント:
  create_preprocess_block()         ... UI コンポーネントを生成して返す
  wire_jp_detection()               ... 日本語検出による自動有効化を設定する
  run_preprocess()                  ... 変換と解析を実行して結果を返す
  preprocess_text_only()            ... TTS 用変換テキストのみを返す
  split_text_with_silence()         ... …… と句点でテキストを分割してセグメントリストを返す
  generate_audio_with_silence()     ... セグメントごとに生成して無音を挿入して結合する
"""

import os
import re
import sys

import gradio as gr
import numpy as np

# ── プロジェクトルートを sys.path に追加 ───────────────────────────
_pkg_dir      = os.path.dirname(os.path.abspath(__file__))           # .../ui/components
_project_root = os.path.normpath(os.path.join(_pkg_dir, "..", "..", ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

try:
    from tts_preprocess import (
        TTSPreprocessor,
        get_accent_phrases as _get_accent_phrases,
        get_full_accent_text as _get_full_accent_text,
        get_accent_text_with_user_dict as _get_accent_text_with_user_dict,
        get_accent_from_mecab_dic as _get_accent_from_mecab_dic,
    )
    _user_dict_path   = os.path.join(_project_root, "user_dict.json")
    _mecab_accent_dic = os.path.join(_project_root, "mecab_accent.dic")
    _preprocessor     = TTSPreprocessor(_user_dict_path)
    PREPROCESS_AVAILABLE = True
    _mecab_dic_available = os.path.exists(_mecab_accent_dic)
    if _mecab_dic_available:
        print(f"[INFO] 前処理モジュール読み込み完了 (mecab_accent.dic あり: {_mecab_accent_dic})")
    else:
        print(f"[INFO] 前処理モジュール読み込み完了 (user_dict: {_user_dict_path})")
except Exception as _pre_err:
    PREPROCESS_AVAILABLE = False
    _mecab_dic_available  = False
    _mecab_accent_dic     = None
    _preprocessor                   = None
    _get_accent_phrases             = None
    _get_full_accent_text           = None
    _get_accent_text_with_user_dict = None
    _get_accent_from_mecab_dic      = None
    print(f"[WARNING] 前処理モジュール読み込み失敗: {_pre_err}")

# 日本語文字（ひらがな・カタカナ・漢字・半角カナ）の判定パターン
_JP_RE = re.compile(r"[぀-鿿ｦ-￯]")

# 文末記号で分割（記号は直前の文に残す）
_SENTENCE_END_RE = re.compile(r"(?<=[。！？])")

# 無音マーカー
_ELLIPSIS_MARKER = "……"


# ══════════════════════════════════════════════════════════════
#  日本語判定
# ══════════════════════════════════════════════════════════════

def _is_japanese(text: str, lang_disp: str, lang_map: dict) -> bool:
    """テキストまたは言語選択が日本語かどうかを判定する"""
    lang_code = lang_map.get(lang_disp, "").lower()
    if "japanese" in lang_code or lang_code in ("ja", "jpn"):
        return True
    return bool(text and _JP_RE.search(text))


# ══════════════════════════════════════════════════════════════
#  前処理実行
# ══════════════════════════════════════════════════════════════

def run_preprocess(text: str, use_preprocess: bool = True):
    """
    前処理を実行して (変換後テキスト, アクセント記号付き読み) を返す。

    Returns:
        (converted_text, accent_full_string)
        accent_full_string は「　」区切りのアクセント記号付きひらがな文字列
    """
    if not PREPROCESS_AVAILABLE or not text or not text.strip():
        return "", ""
    if not use_preprocess:
        return "", ""

    # Step 1: TTS 用テキスト（user_dict + g2p で全ひらがな変換）
    try:
        _preprocessor.reload_user_dict()
        converted = _preprocessor.convert(text.strip(), verbose=False)
        print(f"[PREPROCESS] TTS用: '{converted[:80]}'" if len(converted) > 80 else f"[PREPROCESS] TTS用: '{converted}'")
    except Exception as e:
        print(f"[PREPROCESS ERROR] 変換失敗: {e}")
        return f"変換エラー: {e}", ""

    # Step 2: アクセント解析
    # mecab_accent.dic があれば MeCab で直接解析（最高精度）
    # なければ user_dict + pyopenjtalk で解析
    accent_display = ""
    try:
        if _mecab_dic_available and _get_accent_from_mecab_dic is not None:
            # MeCab アクセント辞書を使用（.dic の 14番目フィールドから accent_type を取得）
            accent_display = _get_accent_from_mecab_dic(
                text.strip(),
                user_dic_path=_mecab_accent_dic,
            )
            print(f"[PREPROCESS] アクセント(MeCab辞書): '{accent_display[:80]}'" if accent_display else "[PREPROCESS] アクセント(MeCab辞書): (空)")
        elif _get_accent_text_with_user_dict is not None:
            # フォールバック: user_dict + pyopenjtalk
            accent_display = _get_accent_text_with_user_dict(
                text.strip(),
                user_dict=_preprocessor.user_dict,
            )
            print(f"[PREPROCESS] アクセント(pyopenjtalk): '{accent_display[:80]}'" if accent_display else "[PREPROCESS] アクセント(pyopenjtalk): (空)")
    except Exception as ae:
        print(f"[PREPROCESS ERROR] アクセント解析失敗: {ae}")
        accent_display = f"アクセント解析エラー: {ae}"

    return converted, accent_display


def accent_only(text: str) -> str:
    """変換済みテキストのアクセント解析のみを実行して返す（生成ボタン用）"""
    if not PREPROCESS_AVAILABLE or not text or not text.strip():
        return ""
    try:
        # mecab_accent.dic があれば優先使用
        if _mecab_dic_available and _get_accent_from_mecab_dic is not None:
            result = _get_accent_from_mecab_dic(text.strip(), user_dic_path=_mecab_accent_dic)
        elif _get_full_accent_text is not None:
            result = _get_full_accent_text(text.strip())
        else:
            return ""
        print(f"[PREPROCESS] accent_only: '{result[:80]}'" if result else "[PREPROCESS] accent_only: (空)")
        return result
    except Exception as e:
        return f"アクセント解析エラー: {e}"


def preprocess_text_only(text: str, use_preprocess: bool) -> str:
    """TTS に渡す変換済みテキストのみを返す（生成ボタン用）"""
    if not use_preprocess or not PREPROCESS_AVAILABLE or not text or not text.strip():
        return text.strip() if text else ""
    try:
        _preprocessor.reload_user_dict()
        return _preprocessor.convert(text.strip(), verbose=False)
    except Exception:
        return text.strip()


# ══════════════════════════════════════════════════════════════
#  無音挿入ユーティリティ
# ══════════════════════════════════════════════════════════════

def split_text_with_silence(text: str, silence_sec: float):
    """
    テキストを分割して (segment_text, silence_after_sec) のリストを返す。

    分割規則:
      …… → silence_sec 秒の無音
      。！？ → silence_sec * 0.5 秒の無音
    """
    if silence_sec <= 0:
        return [(text, 0.0)]

    segments = []
    ellipsis_parts = text.split(_ELLIPSIS_MARKER)

    for e_idx, part in enumerate(ellipsis_parts):
        if not part.strip():
            continue
        is_last_ellipsis = (e_idx == len(ellipsis_parts) - 1)

        # 文末記号で分割（記号はその文に含む）
        sentences = _SENTENCE_END_RE.split(part)
        non_empty = [s for s in sentences if s.strip()]

        for s_idx, sent in enumerate(non_empty):
            is_last_sentence = (s_idx == len(non_empty) - 1)

            if not is_last_sentence:
                sil = silence_sec * 0.5
            elif not is_last_ellipsis:
                sil = silence_sec
            else:
                sil = 0.0

            segments.append((sent.strip(), sil))

    return segments if segments else [(text.strip(), 0.0)]


def generate_audio_with_silence(generate_one_fn, text: str, silence_sec: float):
    """
    テキストを分割して各セグメントの音声を生成し、無音を挿入して結合する。

    Args:
        generate_one_fn: (text) → (wavs_list, sr) を返す callable
        text:            生成対象テキスト
        silence_sec:     …… の無音時間（秒）

    Returns:
        (wav_array, sr)
    """
    segments = split_text_with_silence(text, silence_sec)
    audio_parts = []
    sr_out = 24000

    for seg_text, sil_sec in segments:
        if not seg_text:
            continue
        wavs, sr = generate_one_fn(seg_text)
        sr_out = sr
        wav = np.asarray(wavs[0], dtype=np.float32)
        audio_parts.append(wav)
        if sil_sec > 0:
            silence = np.zeros(int(sil_sec * sr), dtype=np.float32)
            audio_parts.append(silence)

    if not audio_parts:
        return np.array([], dtype=np.float32), sr_out

    return np.concatenate(audio_parts), sr_out


# ══════════════════════════════════════════════════════════════
#  UI コンポーネント
# ══════════════════════════════════════════════════════════════

def create_preprocess_block():
    """
    前処理 UI ブロック（チェックボックス・ボタン・結果欄・無音スライダー）を生成する。

    Returns:
        (use_preprocess_cb, analyze_btn, converted_out, accent_out, silence_sec_slider)
    """
    use_preprocess = gr.Checkbox(
        label="MeCab前処理（漢字読み変換 + アクセント解析）",
        value=False,
        interactive=False,
        info=(
            "テキストが日本語のときに有効になります。"
            "pyopenjtalk-plus で漢字を読み仮名に変換します。"
            if PREPROCESS_AVAILABLE
            else "tts_preprocess モジュールが見つかりません"
        ),
    )
    analyze_btn = gr.Button(
        "変換と解析",
        variant="secondary",
        interactive=False,
    )
    converted_out = gr.Textbox(
        label="変換後テキスト（編集可・この内容で生成されます）",
        lines=2,
        interactive=True,
    )
    accent_out = gr.Textbox(
        label="アクセント記号付き読み（↑=上昇　↓=下降、編集可）",
        lines=2,
        interactive=True,
    )
    silence_sec = gr.Slider(
        label="無音時間（秒）— …… と句点の後に挿入",
        minimum=0.0,
        maximum=3.0,
        value=0.5,
        step=0.1,
        interactive=False,
        info="…… で silence_sec 秒、句点（。！？）で silence_sec×0.5 秒の無音を挿入",
    )
    return use_preprocess, analyze_btn, converted_out, accent_out, silence_sec


def wire_jp_detection(
    text_in, lang_in, lang_map,
    use_preprocess, analyze_btn,
    silence_sec=None,
    converted_out=None, accent_out=None,
):
    """
    text_in・lang_in の変化を監視して:
      - 日本語なら前処理コントロールを有効化＋チェックボックスを自動オン
      - 日本語テキストが入力されたら変換・解析を自動実行して結果を表示
    """
    def _update_state(text, lang_disp):
        enabled = _is_japanese(text or "", lang_disp or "", lang_map) and PREPROCESS_AVAILABLE
        updates = [
            gr.update(interactive=enabled, value=enabled),
            gr.update(interactive=enabled),
        ]
        if silence_sec is not None:
            updates.append(gr.update(interactive=enabled))
        return updates

    ctrl_outputs = [use_preprocess, analyze_btn]
    if silence_sec is not None:
        ctrl_outputs.append(silence_sec)

    text_in.change(fn=_update_state, inputs=[text_in, lang_in], outputs=ctrl_outputs)
    lang_in.change(fn=_update_state, inputs=[text_in, lang_in], outputs=ctrl_outputs)

    # テキストが変わったら自動で変換・解析を実行（converted_out / accent_out が渡された場合）
    if converted_out is not None and accent_out is not None:
        def _auto_preprocess(text, lang_disp):
            enabled = _is_japanese(text or "", lang_disp or "", lang_map) and PREPROCESS_AVAILABLE
            if not enabled:
                return "", ""
            return run_preprocess(text, True)

        text_in.change(
            fn=_auto_preprocess,
            inputs=[text_in, lang_in],
            outputs=[converted_out, accent_out],
        )
        lang_in.change(
            fn=_auto_preprocess,
            inputs=[text_in, lang_in],
            outputs=[converted_out, accent_out],
        )
