# 云盘同步配置指南

## 概述

通过 rclone 统一驱动，支持 12+ 云盘。所有云盘操作语法一致。

## 已配置的云盘查询

```bash
rclone listremotes
```

## 各云盘配置方法

### OneDrive

```bash
rclone config create onedrive onedrive
# 浏览器打开 URL 完成 OAuth 授权
```

### Google Drive

```bash
# 需要先在 Google Cloud Console 创建 OAuth 凭据
rclone config create gdrive drive \
  client_id=<ID> \
  client_secret=<SECRET> \
  scope=drive.file
```

### 阿里云盘

```bash
rclone config create aliyun aliyundrive token=<refresh_token>
```

### 百度云盘

```bash
rclone config create baidu baidunetdisk \
  client_id=<ID> client_secret=<SECRET>
```

### 坚果云 (WebDAV)

```bash
rclone config create jianguo webdav \
  url=https://dav.jianguoyun.com/dav/ \
  vendor=other user=<邮箱> pass=<应用密码>
# ⚠️ 密码是坚果云"应用密码"，非登录密码
```

### Dropbox

```bash
rclone config create dropbox dropbox
```

### Mega

```bash
rclone config create mega mega user=<email> pass=<password>
```

### Nextcloud

```bash
rclone config create nextcloud webdav \
  url=https://<domain>/remote.php/webdav/ \
  vendor=nextcloud user=<user> pass=<password>
```

### iCloud Drive

```bash
rclone config create icloud iclouddrive user=<apple-id>
# 需要双因素认证码
```

### 天翼云盘

```bash
rclone config create tianyi cloud189 user=<phone> pass=<password>
```

### 115 网盘

```bash
rclone config create p115 115 user=<phone> pass=<password>
# 可能需要 cookie 模式
```

### 夸克网盘

需要第三方 WebDAV 桥接服务（如 alist），再走 rclone webdav：

```bash
rclone config create quark webdav \
  url=http://localhost:<port>/dav vendor=other \
  user=<token> pass=<token>
```

## 常用同步命令

```bash
# 本地 → 云盘
rclone copy /local/path remote:远程路径 --progress

# 云盘 → 本地
rclone copy remote:远程路径 /local/path --progress

# 双向同步
rclone bisync /local/path remote:远程路径 --resync

# 挂载为本地目录
rclone mount remote: /mnt/cloud/remote --daemon
```

## 自动同步

安装脚本已注册 crontab，每 30 分钟同步一次：

```bash
*/30 * * * * rclone copy ~/.hermes/knowledge/notes/ onedrive:知识库/笔记/ --ignore-existing --quiet
```

可自行调整：

```bash
crontab -e
```
