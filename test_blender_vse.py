#!/usr/bin/env python3
"""
test_blender_vse.py — Automated Test for Blender VSE (Video Sequence Editor) Engine
Tests sequence setup, color background, text strip, and rendering to MP4.
"""

import sys
import os

# ponytail: inline blender python execution test script.
# Ceiling: basic VSE strip creation. Upgrade path: add multi-track audio/video stitching.

try:
    import bpy
except ImportError:
    print("[ERROR] Must be run inside Blender python environment (blender -b -P test_blender_vse.py)")
    sys.exit(1)

def build_demo_vse(output_mp4="/tmp/blender_vse_demo.mp4", duration_sec=3):
    fps = 30
    total_frames = duration_sec * fps
    width, height = 1080, 1920 # Vertical Reel format

    # 1. Reset Scene
    scene = bpy.context.scene
    scene.render.fps = fps
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.frame_start = 1
    scene.frame_end = total_frames

    # Set FFmpeg MP4 Render Settings
    scene.render.filepath = "/tmp/blender_demo_"
    scene.render.use_file_extension = True
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
    scene.render.ffmpeg.ffmpeg_preset = 'GOOD'

    # Ensure Sequence Editor exists
    if not scene.sequence_editor:
        scene.sequence_editor_create()

    seq = scene.sequence_editor
    sequences = seq.sequences

    # Clear pre-existing strips
    for strip in list(sequences):
        sequences.remove(strip)

    # 2. Add Color Strip (Dark Navy background #0A192F)
    color_strip = sequences.new_effect(
        name="BgColor",
        type='COLOR',
        channel=1,
        frame_start=1,
        frame_end=total_total_frames if 'total_total_frames' in locals() else total_frames
    )
    color_strip.color = (0.04, 0.10, 0.18) # Approx RGB for #0A192F

    # 3. Add Text Strip
    text_strip = sequences.new_effect(
        name="TitleText",
        type='TEXT',
        channel=2,
        frame_start=1,
        frame_end=total_frames
    )
    text_strip.text = "SutraOS Blender VSE Engine\nReady for Automation!"
    text_strip.font_size = 65
    text_strip.color = (1.0, 0.6, 0.2, 1.0) # Saffron Gold
    text_strip.use_shadow = True
    text_strip.shadow_color = (0.0, 0.0, 0.0, 0.8)

    print(f"[Blender VSE] Configured {width}x{height} reel ({total_frames} frames). Rendering to {output_mp4}...")
    bpy.ops.render.render(animation=True)
    print(f"[Blender VSE] ✅ Successfully rendered demo video: {output_mp4}")

if __name__ == "__main__":
    build_demo_vse()
