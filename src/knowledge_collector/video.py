"""
视频采集 — 全工具清单

从抖音、YouTube、社交平台及通用视频源中提取画面和声音内容。
"""

from __future__ import annotations

from urllib.parse import parse_qs, urlparse

from runtime_support import CollectionResult
from .note_generator import generate_note

class VideoCollector:
    """视频知识采集 — 8 种引擎/工具"""

    ENGINES = {
        # ─── 专用视频采集脚本 ───
        "douyin_video_intake": {
            "type": "script",
            "level": "⭐⭐⭐⭐⭐",
            "description": "抖音视频元数据+字幕+ASR采集 — 通过浏览器态或Cookie获取",
            "script": "scripts/douyin_video_intake.py",
            "features": [
                "视频元数据提取（标题/作者/播放量/点赞/评论）",
                "字幕/弹幕提取",
                "音频转写（Whisper ASR）",
            ],
            "status": "已部署 · 生产中",
        },
        "social_video_intake": {
            "type": "script",
            "level": "⭐⭐⭐⭐⭐",
            "description": "通用社交媒体视频采集 — 统一入口",
            "script": "scripts/social_video_intake.py",
            "features": [
                "多平台支持（抖音/TikTok/快手等）",
                "元数据+字幕+ASR 全链路",
                "登录态管理",
            ],
            "status": "已部署 · 生产中",
        },
        "universal_video_analyzer": {
            "type": "skill",
            "level": "⭐⭐⭐⭐⭐",
            "description": "通用视频内容分析引擎 — 多语言OCR/人脸/质量/BGM/多渠道",
            "skill": "universal-video-content-analyzer",
            "features": [
                "多语言语音识别 (Whisper)",
                "画面 OCR (EasyOCR)",
                "人脸检测",
                "画质评估",
                "BGM 识别",
                "场景切分",
                "情感分析",
            ],
            "status": "已部署 · 生产中",
        },

        # ─── 基础视频工具 ───
        "yt_dlp": {
            "type": "cli",
            "level": "⭐⭐⭐⭐",
            "description": "通用视频/音频下载 — 支持YouTube/B站/抖音等数千网站",
            "cli": "yt-dlp",
            "features": [
                "视频下载（MP4/WebM）",
                "音频提取（MP3/WAV）",
                "字幕下载",
                "元数据获取",
            ],
            "status": "已部署",
        },
        "whisper_asr": {
            "type": "engine",
            "level": "⭐⭐⭐⭐",
            "description": "OpenAI Whisper 语音识别 — 多语言，高精度",
            "features": [
                "99+ 语言支持",
                "多模型大小（tiny/base/small/medium/large）",
                "自动语言检测",
                "时间戳对齐",
            ],
            "status": "已部署",
        },
        "easy_ocr": {
            "type": "engine",
            "level": "⭐⭐⭐",
            "description": "EasyOCR — 视频关键帧画面文字提取",
            "features": [
                "80+ 语言支持",
                "中英文高精度",
                "GPU 加速可选",
            ],
            "status": "已部署",
        },
        "ffmpeg": {
            "type": "cli",
            "level": "⭐⭐⭐",
            "description": "FFmpeg 多媒体处理 — 视频切分/转码/截图/音频提取",
            "features": [
                "视频/音频格式转换",
                "关键帧提取",
                "场景切分",
                "片段剪辑",
                "字幕烧录",
            ],
            "status": "已部署",
        },
        "tesseract_ocr": {
            "type": "cli",
            "level": "⭐⭐⭐",
            "description": "Tesseract OCR — 开源文字识别，中文需chi_sim语言包",
            "cli": "tesseract",
            "features": [
                "100+ 语言支持",
                "中文简体/繁体",
                "版面分析",
            ],
            "status": "已部署",
        },

        # ─── 平台分析 ───
        "youtube_analytics": {
            "type": "skill",
            "level": "⭐⭐⭐⭐",
            "description": "YouTube Data API v3 分析工具",
            "skill": "youtube-analytics",
            "features": [
                "频道数据分析",
                "视频统计",
                "评论分析",
                "趋势跟踪",
            ],
            "status": "已部署",
        },
        "douyin_daily_analysis": {
            "type": "skill",
            "level": "⭐⭐⭐⭐",
            "description": "抖音每日自动化分析工作流",
            "skill": "douyin-daily-analysis-workflow",
            "features": [
                "账号每日数据",
                "视频表现分析",
                "内容主题变化趋势",
            ],
            "status": "已部署",
        },
        "douyin_hot": {
            "type": "skill",
            "level": "⭐⭐⭐",
            "description": "抖音热榜/热搜数据获取",
            "skill": "douyin-hot",
            "features": [
                "热榜视频",
                "挑战赛",
                "音乐热点",
                "多领域热门",
            ],
            "status": "已部署",
        },
    }

    def collect(self, url: str) -> CollectionResult:
        parsed = urlparse(url)
        host = parsed.netloc or "video"
        video_id = parse_qs(parsed.query).get("v", [""])[0]
        if not video_id and parsed.path:
            video_id = parsed.path.strip("/").split("/")[-1]
        title = f"Video capture from {host}"
        body = (
            f"URL: {url}\n"
            f"Video ID: {video_id or 'unknown'}\n\n"
            "Public KMM stores a structured capture note for this video URL. "
            "Server-side OCR/ASR pipelines can enrich this note later."
        )
        note = generate_note(
            {
                "title": title,
                "content": body,
                "source_type": "video",
                "source_ref": url,
                "metadata": {"host": host, "video_id": video_id},
            },
            template="video",
        )
        return CollectionResult(
            source_type="video",
            title=title,
            content_preview=body[:500],
            url=url,
            note_path=note["note_path"],
            gbrain_slug=note["note_id"],
            metadata={"host": host, "video_id": video_id},
            subtitles=[],
            frames=[],
        )


def collect_video(url: str) -> CollectionResult:
    return VideoCollector().collect(url)
