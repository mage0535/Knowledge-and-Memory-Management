"""
Cloud Sync Engine — 云盘同步引擎

基于 rclone 的统一云存储同步层。
支持 12+ 云盘：OneDrive / Google Drive / 阿里云盘 / 百度云盘 / 坚果云 / Dropbox / Mega / 天翼云 / iCloud / Nextcloud / 115 / 夸克
"""

from __future__ import annotations

import subprocess
import os
from pathlib import Path

from runtime_support import resolve_notes_root

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

    def has_remote(self, remote: str) -> bool:
        return remote.rstrip(":") in self.list_remotes()

    @staticmethod
    def _remote_target(remote: str, remote_path: str = "") -> str:
        remote = remote.rstrip(":")
        if remote_path:
            return f"{remote}:{remote_path}"
        return f"{remote}:"

    def _run(self, cmd: list[str]):
        return subprocess.run(cmd, capture_output=True, text=True)
    
    def sync_to(self, local_path, remote, remote_path, flags=None):
        """同步本地目录到云盘"""
        cmd = ["rclone", "copy", local_path, self._remote_target(remote, remote_path), "--progress"]
        if flags:
            cmd.extend(flags)
        return self._run(cmd)
    
    def sync_from(self, remote, remote_path, local_path):
        """从云盘同步到本地"""
        cmd = ["rclone", "copy", self._remote_target(remote, remote_path), local_path, "--progress"]
        return self._run(cmd)

    def bisync(self, local_path: str, remote: str, remote_path: str = "", *, resync: bool = False, flags=None):
        """双向同步，默认不执行 destructive resync。"""
        cmd = ["rclone", "bisync", local_path, self._remote_target(remote, remote_path)]
        if resync:
            cmd.append("--resync")
        if flags:
            cmd.extend(flags)
        return self._run(cmd)
    
    def bidirectional_sync(self, local_path, remote_path, resync=False):
        """兼容旧接口。remote_path 需使用 remote:path 形式。"""
        remote_name, _, nested_path = remote_path.partition(":")
        if not remote_name:
            raise ValueError("remote_path must be formatted like 'remote:path'")
        return self.bisync(local_path, remote_name, nested_path, resync=resync)
    
    def available_drivers(self):
        """返回当前已配置的云盘驱动列表"""
        return self.list_remotes()


def list_cloud_drives():
    return CloudSyncEngine().list_remotes()


def sync_to_cloud(local: str, remote: str):
    remote_name, _, remote_path = remote.partition(":")
    if not remote_name:
        raise ValueError("remote must be formatted like 'remote:path'")
    return CloudSyncEngine().sync_to(local, remote_name, remote_path)


def sync_from_cloud(remote: str, local: str):
    remote_name, _, remote_path = remote.partition(":")
    if not remote_name:
        raise ValueError("remote must be formatted like 'remote:path'")
    return CloudSyncEngine().sync_from(remote_name, remote_path, local)


def bidirectional_sync(remote: str, local: str | None = None, *, resync: bool = False, flags=None):
    remote_name, _, remote_path = remote.partition(":")
    if not remote_name:
        raise ValueError("remote must be formatted like 'remote:path'")
    local_path = local or str(resolve_notes_root())
    return CloudSyncEngine().bisync(local_path, remote_name, remote_path, resync=resync, flags=flags)


def on_pre_sync(payload: dict | None = None) -> dict:
    payload = dict(payload or {})
    payload.setdefault("status", "ready")
    payload.setdefault("notes_root", str(resolve_notes_root()))
    return payload


__all__ = [
    "CloudSyncEngine",
    "DRIVERS",
    "list_cloud_drives",
    "sync_from_cloud",
    "sync_to_cloud",
    "on_pre_sync",
]
