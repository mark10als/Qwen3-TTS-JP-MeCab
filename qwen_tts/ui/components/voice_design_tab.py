# coding=utf-8
"""Voice Design tab component for Qwen3-TTS UI."""

import time
from typing import Any, Callable, Dict, List, Tuple

import gradio as gr
import numpy as np

from ..i18n_utils import t
from ..model_manager import ModelManager
from .preprocess_block import (
    create_preprocess_block,
    wire_jp_detection,
    run_preprocess,
    generate_audio_with_silence,
    accent_only,
)

# Preset voice design keys (match i18n JSON)
PRESET_KEYS = [
    "calm_male",
    "energetic_female",
    "professional_narrator",
    "gentle_grandmother",
    "powerful_announcer",
    "cute_girl",
]


def _adjust_speed(wav: np.ndarray, sr: int, speed: float) -> Tuple[np.ndarray, int]:
    """Adjust audio playback speed via resampling."""
    if abs(speed - 1.0) < 0.01:
        return wav, sr
    target_length = max(1, int(len(wav) / speed))
    indices = np.linspace(0, len(wav) - 1, target_length)
    resampled = np.interp(indices, np.arange(len(wav)), wav)
    return resampled.astype(np.float32), sr


def create_voice_design_tab(
    manager: ModelManager,
    lang_choices_disp: List[str],
    lang_map: Dict[str, str],
    gen_kwargs_fn: Callable[[], Dict[str, Any]],
) -> None:
    """Create Voice Design tab UI components and event handlers."""

    gr.Markdown(f"### {t('voice_design.title')}\n{t('voice_design.description')}")

    with gr.Row():
        with gr.Column(scale=2):
            text_in = gr.Textbox(
                label=t("voice_design.text_input.label"),
                lines=5,
                max_lines=10,
                placeholder=t("voice_design.text_input.placeholder"),
                value="It's in the top drawer... wait, it's empty? No way, that's impossible! I'm sure I put it there!",
                interactive=True,
            )
            design_in = gr.Textbox(
                label=t("voice_design.voice_description.label"),
                lines=3,
                placeholder=t("voice_design.voice_description.placeholder"),
                info=t("voice_design.voice_description.info"),
                value="Speak in an incredulous tone, but with a hint of panic beginning to creep into your voice.",
                interactive=True,
            )
            with gr.Row():
                lang_in = gr.Dropdown(
                    label=t("voice_design.language_selector.label"),
                    choices=lang_choices_disp,
                    value="Auto",
                    interactive=True,
                )
                speed_in = gr.Slider(
                    label=t("voice_design.speed_slider.label"),
                    minimum=0.5,
                    maximum=2.0,
                    value=1.0,
                    step=0.1,
                    interactive=True,
                )
            # ---- MeCab + pyopenjtalk-plus 前処理 ----
            use_preprocess, analyze_btn, converted_out, accent_out, silence_sec = create_preprocess_block()
            btn = gr.Button(
                t("voice_design.generate_button"),
                variant="primary",
                elem_classes=["primary-btn"],
            )

        with gr.Column(scale=1):
            audio_out = gr.Audio(label=t("voice_design.audio_output"), type="numpy", interactive=False)
            status_out = gr.Textbox(label=t("voice_design.status"), lines=2)

    # Preset voice buttons
    gr.Markdown(f"#### {t('voice_design.presets.title')}")
    with gr.Row():
        preset_btns_row1 = []
        for key in PRESET_KEYS[:3]:
            b = gr.Button(
                t(f"voice_design.presets.{key}.name"),
                elem_classes=["preset-card"],
            )
            preset_btns_row1.append((b, key))
    with gr.Row():
        preset_btns_row2 = []
        for key in PRESET_KEYS[3:]:
            b = gr.Button(
                t(f"voice_design.presets.{key}.name"),
                elem_classes=["preset-card"],
            )
            preset_btns_row2.append((b, key))

    # Wire preset buttons to fill design_in
    for b, key in preset_btns_row1 + preset_btns_row2:
        desc = t(f"voice_design.presets.{key}.description")
        b.click(fn=lambda d=desc: d, outputs=[design_in])

    def run_voice_design(
        text: str, lang_disp: str, design: str, speed: float,
        use_preprocess: bool, converted_text_in: str, accent_in: str, silence_sec: float,
    ):
        converted_display = ""
        accent_display    = ""
        try:
            if not text or not text.strip():
                return None, f"{t('messages.error')}: {t('messages.enter_text')}", "", ""
            if not design or not design.strip():
                return None, f"{t('messages.error')}: {t('messages.enter_voice_description')}", "", ""

            # アクセント記号付き読み欄に内容がある場合は「変換と解析」が実施済み
            # （ユーザーが手動修正した可能性もある）→ 再実行せずそのまま使用
            if use_preprocess and accent_in and accent_in.strip():
                text_for_tts = converted_text_in.strip() if converted_text_in else text.strip()
                converted_display = converted_text_in.strip() if converted_text_in else ""
                accent_display = accent_in.strip()
            else:
                converted_display, accent_display = run_preprocess(text, use_preprocess)
                text_for_tts = converted_display if converted_display else text.strip()

            tts = manager.get_model("voice_design")
            language = lang_map.get(lang_disp, "Auto")
            kwargs = gen_kwargs_fn()
            start = time.time()

            def _gen_one(seg_text):
                return tts.generate_voice_design(
                    text=seg_text,
                    language=language,
                    instruct=design.strip(),
                    **kwargs,
                )

            wav, sr = generate_audio_with_silence(_gen_one, text_for_tts, silence_sec or 0.0)
            elapsed = time.time() - start

            wav, sr = _adjust_speed(wav, sr, speed)
            return (sr, wav), t("messages.generated_detail", elapsed=elapsed), converted_display, accent_display
        except Exception as e:
            import traceback
            traceback.print_exc()
            return None, f"{type(e).__name__}: {e}", converted_display, accent_display

    # Event: 変換と解析ボタン（チェックボックスの状態に関係なく常に実行）
    analyze_btn.click(
        fn=lambda text: run_preprocess(text, True),
        inputs=[text_in],
        outputs=[converted_out, accent_out],
    )

    btn.click(
        run_voice_design,
        inputs=[text_in, lang_in, design_in, speed_in, use_preprocess, converted_out, accent_out, silence_sec],
        outputs=[audio_out, status_out, converted_out, accent_out],
    )

    # Event: 日本語検出 → 前処理コントロールを有効化＋自動変換
    wire_jp_detection(
        text_in, lang_in, lang_map,
        use_preprocess, analyze_btn, silence_sec,
        converted_out=converted_out, accent_out=accent_out,
    )
