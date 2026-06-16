#!/usr/bin/env bash
# 配置 rclone 云盘驱动（交互式）

echo "=== 云盘驱动配置助手 ==="
echo ""

echo "选择要配置的云盘:"
echo "1) OneDrive      2) Google Drive   3) 阿里云盘"
echo "4) 百度云盘      5) 坚果云         6) Dropbox"
echo "7) Mega          8) Nextcloud      9) iCloud Drive"
echo "10) 天翼云盘     11) 115 网盘      12) 夸克网盘"
echo "0) 全部跳过（稍后手动配置）"
echo ""

read -r -p "输入编号: " choice
case "$choice" in
  1) rclone config create onedrive onedrive ;;
  2) rclone config create gdrive drive ;;
  3) read -r -p "阿里云盘 refresh_token: " token; rclone config create aliyun aliyundrive token="$token" ;;
  5) rclone config create jianguo webdav url=https://dav.jianguoyun.com/dav/ vendor=other ;;
  6) rclone config create dropbox dropbox ;;
  7) rclone config create mega mega ;;
  *) echo "跳过。运行 rclone config 手动配置" ;;
esac

echo "当前已配置云盘:"
rclone listremotes
