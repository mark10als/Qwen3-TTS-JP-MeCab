# coding=utf-8
"""UI tab components for Qwen3-TTS."""

from .preprocess_block import (
    create_preprocess_block,
    wire_jp_detection,
    run_preprocess,
    preprocess_text_only,
    accent_only,
    split_text_with_silence,
    generate_audio_with_silence,
)
from .custom_voice_tab import create_custom_voice_tab
from .voice_design_tab import create_voice_design_tab
from .voice_clone_tab import create_voice_clone_tab
from .settings_tab import create_settings_tab

__all__ = [
    "create_preprocess_block",
    "wire_jp_detection",
    "run_preprocess",
    "preprocess_text_only",
    "accent_only",
    "split_text_with_silence",
    "generate_audio_with_silence",
    "create_custom_voice_tab",
    "create_voice_design_tab",
    "create_voice_clone_tab",
    "create_settings_tab",
]
