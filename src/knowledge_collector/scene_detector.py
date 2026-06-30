"""Video scene detection and frame OCR pipeline.

Optional dependencies: PySceneDetect (CLI), PaddleOCR (Python), tesseract (CLI).
"""

from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any


def detect_scenes(video_path: str, threshold: float = 27.0, min_scene_length: int = 15) -> list[dict[str, Any]]:
    try:
        result = subprocess.run(
            ["scenedetect", "-i", video_path, "detect-content",
             "-t", str(threshold), "-m", str(min_scene_length),
             "list-scenes", "-q"],
            capture_output=True, text=True, timeout=300,
        )
        if result.returncode != 0:
            return []
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []

    import re
    scenes = []
    pattern = re.compile(r"(\d+:\d{2}:\d{2}\.\d+)\s*\[.*?\]\s*->\s*(\d+:\d{2}:\d{2}\.\d+)")
    for line in result.stdout.splitlines():
        match = pattern.search(line)
        if match:
            scenes.append({
                "start": _time_to_seconds(match.group(1)),
                "end": _time_to_seconds(match.group(2)),
                "start_str": match.group(1),
                "end_str": match.group(2),
            })
    return scenes


def select_keyframes(video_path: str, scenes: list[dict], max_frames: int = 20) -> list[str]:
    if not scenes:
        return []
    keyframes = []
    with tempfile.TemporaryDirectory(prefix="kmm-frames-") as tmpdir:
        for i, scene in enumerate(scenes[:max_frames]):
            mid = (scene["start"] + scene["end"]) / 2
            mid_str = _seconds_to_time(mid)
            frame_path = os.path.join(tmpdir, f"frame_{i:04d}.jpg")
            try:
                result = subprocess.run(
                    ["ffmpeg", "-ss", mid_str, "-i", video_path,
                     "-vframes", "1", "-q:v", "3", frame_path, "-y"],
                    capture_output=True, text=True, timeout=30,
                )
                if result.returncode == 0 and os.path.exists(frame_path):
                    keyframes.append(frame_path)
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue
    return keyframes


def extract_timeline_chunks(
    transcript: str, scenes: list[dict], keyframes: list[str]
) -> list[dict[str, Any]]:
    if not scenes:
        return [{"start": 0, "end": 0, "summary": "No scenes detected.", "keyframe": "", "ocr_text": "", "transcript": transcript[:2000]}]

    chunks = []
    for i, scene in enumerate(scenes[:12]):
        ocr_text = ""
        if i < len(keyframes):
            ocr_text = ocr_frame(keyframes[i])
        chunks.append({
            "start": scene["start"],
            "end": scene["end"],
            "timestamp": _seconds_to_time(scene["start"]),
            "keyframe": keyframes[i] if i < len(keyframes) else "",
            "ocr_text": ocr_text,
            "transcript": transcript[int(scene["start"] * 3):int(scene["end"] * 3 + 3)][:500],
        })
    return chunks


def ocr_frame(frame_path: str) -> str:
    try:
        from paddleocr import PaddleOCR
        ocr = PaddleOCR(lang="ch", use_angle_cls=True, show_log=False)
        result = ocr.ocr(frame_path)
        if result and result[0]:
            return " ".join(line[1][0] for line in result[0] if len(line) > 1)
    except ImportError:
        pass
    try:
        result = subprocess.run(
            ["tesseract", frame_path, "stdout", "-l", "chi_sim+eng"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return ""


def _time_to_seconds(ts: str) -> float:
    parts = ts.replace(",", ".").split(":")
    if len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
    if len(parts) == 2:
        return int(parts[0]) * 60 + float(parts[1])
    return float(parts[0])


def _seconds_to_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}"
