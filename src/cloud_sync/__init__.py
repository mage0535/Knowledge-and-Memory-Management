"""
Cloud Sync Engine — 云盘同步引擎

基于 rclone 的统一云存储同步层。
支持 12+ 云盘：OneDrive / Google Drive / 阿里云盘 / 百度云盘 / 坚果云 / Dropbox / Mega / 天翼云 / iCloud / Nextcloud / 115 / 夸克
"""

import subprocess
import os
from pathlib import Path

DRIVERS = {
    "onedrive": {"type": "onedrive", "auth": "oauth", "setup": "rclone config"},
    "googledrive": {"type": "drive", "auth": "oauth", "setup": "rclone config"},
    "aliyundrive": {"type": "aliyundrive", "auth": "token", "setup": "见 docs/cloud-sync.md"},
    "baidu": {"type": "baidunetdisk", "auth": "oauth", "setup": "见 docs/cloud-sync.md"},
    "dropbox": {"type": "dropbox", "auth": "oauth", "setup": "rclone config"},
    "mega": {"type": "mega", "auth": "password", "setup": "rclone config"},
    "jianguo": {"type": "webdav", "auth": "password", "setup": "坚果云应用密码"},
    "nextcloud": {"type": "webdav", "auth": "password", "setup": "WebDAV URL"},
    "icloud": {"type": "iclouddrive", "auth": "oauth+2fa", "setup": "需 Apple ID"},
    "tianyi": {"type": "cloud189", "auth": "password", "setup": "手机号+密码"},
    "p115": {"type": "115", "auth": "cookie", "setup": "需 cookie"},
    "quark": {"type": "webdav", "auth": "token", "setup": "需 WebDAV 桥接"},
}

class CloudSyncEngine:
    """云盘同步引擎"""
    
    def __init__(self):
        self._check_rclone()
    
    def _check_rclone(self):
        result = subprocess.run(["rclone", "version"], capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError("rclone 未安装")
    
    def list_remotes(self):
        """列出已配置的云盘"""
        result = subprocess.run(["rclone", "listremotes"], capture_output=True, text=True)
        return [r.strip().rstrip(":") for r in result.stdout.splitlines() if r.strip()]
    
    def sync_to(self, local_path, remote, remote_path, flags=None):
        """同步本地目录到云盘"""
        cmd = ["rclone", "copy", local_path, f"{remote}:{remote_path}", "--progress"]
        if flags:
            cmd.extend(flags)
        return subprocess.run(cmd)
    
    def sync_from(self, remote, remote_path, local_path):
        """从云盘同步到本地"""
        cmd = ["rclone", "copy", f"{remote}:{remote_path}", local_path, "--progress"]
        return subprocess.run(cmd)
    
    def bidirectional_sync(self, local_path, remote_path):
        """双向同步"""
        cmd = ["rclone", "bisync", local_path, remote_path, "--resync"]
        return subprocess.run(cmd)
    
    def available_drivers(self):
        """返回当前已配置的云盘驱动列表"""
        return self.list_remotes()
