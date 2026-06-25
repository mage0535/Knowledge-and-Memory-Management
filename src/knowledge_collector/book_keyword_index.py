#!/usr/bin/env python3
"""
书籍关键词索引 — 离线构建 + 自动补全

从 book_index.json 提取关键词，构建 SQLite FTS5 全文索引 + gbrain 知识图谱，实现自动书名匹配。

用法:
  python3 book_keyword_index.py build          # 从索引构建 FTS5 DB
  python3 book_keyword_index.py search <词>     # 搜索匹配的书
  python3 book_keyword_index.py suggest <词>    # 自动建议模式（返回格式化的候选列表）
  python3 book_keyword_index.py sync-gbrain    # 同步到 gbrain 知识图谱
  python3 book_keyword_index.py scan-updates   # 扫描 OneDrive book/ 更新索引
"""

import json, os, re, sqlite3, subprocess, sys, hashlib, time
from datetime import datetime
from pathlib import Path
from typing import Optional

# 可配置路径（通过环境变量覆盖，默认 ${HOME}/.knowledge/book_cache/）
_DEFAULT_BOOK_DIR = os.path.join(os.environ.get("HOME", "~"), ".knowledge", "book_cache")
_DEFAULT_INDEX_JSON = os.path.join(_DEFAULT_BOOK_DIR, "book_index.json")

INDEX_JSON = os.environ.get("KMM_BOOK_INDEX_JSON", _DEFAULT_INDEX_JSON)
CACHE_DIR = os.path.dirname(INDEX_JSON) if INDEX_JSON else _DEFAULT_BOOK_DIR
DB_PATH = os.path.join(CACHE_DIR, "book_keywords.db")
GBRAIN_SLUG = "note-book-knowledge-base"

os.makedirs(CACHE_DIR, exist_ok=True)


# ── 关键词提取 ──────────────────────────────────────────────

STOP_WORDS = set("的 了 在 是 我 有 和 就 不 人 都 一 一个 上 也 很 到 说 要 去 你 会 着 没有 看 好 自己 这 他 她 它 们 那 这个 那个 什么 怎么 如何 为什么 因为 所以 但是 然而 虽然".split())

def extract_keywords(text: str) -> list[str]:
    """从文件名/分类名中提取有意义的词组"""
    if not text:
        return []
    # 去掉扩展名
    text = re.sub(r'\.(pdf|epub|mobi|azw3|djvu|chm|doc|docx)$', '', text, flags=re.IGNORECASE)
    # 按常见分隔符拆分
    parts = re.split(r'[ \-_（）()\[\]【】《》/\\,，.]+', text)
    keywords = []
    for p in parts:
        p = p.strip()
        if not p or len(p) < 1:
            continue
        # 英文单词拆分
        # 中文词组（2字及以上）
        if re.search(r'[\u4e00-\u9fff]', p):
            # 中文：提取 2-6 字词组
            chars = list(p)
            for i in range(len(chars)):
                for j in range(i+2, min(i+7, len(chars)+1)):
                    phrase = ''.join(chars[i:j])
                    if phrase not in STOP_WORDS:
                        keywords.append(phrase)
        # 英文单词
        for en_word in re.findall(r'[a-zA-Z][a-zA-Z0-9]{1,}', p):
            if en_word.lower() not in {'the', 'and', 'for', 'with', 'from', 'this', 'that', 'book', 'guide', 'manual', 'introduction', 'pdf', 'epub'}:
                keywords.append(en_word.lower())
    
    # 去重，按长度排序（长词在前）
    seen = set()
    unique = []
    for k in keywords:
        if k not in seen:
            seen.add(k)
            unique.append(k)
    unique.sort(key=lambda x: (-len(x), x))
    return unique[:30]  # 最多30个关键词


# ── FTS5 索引 ──────────────────────────────────────────────

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("CREATE VIRTUAL TABLE IF NOT EXISTS book_fts USING fts5(filename, category, keywords, tokenize='unicode61')")
    sql = (
        "CREATE TABLE IF NOT EXISTS books ("
        "rowid INTEGER PRIMARY KEY, "
        "filename TEXT NOT NULL, "
        "category TEXT, "
        "ext TEXT, "
        "size_bytes INTEGER DEFAULT 0, "
        "size_mb REAL DEFAULT 0, "
        "remote_path TEXT, "
        "keywords TEXT, "
        "keyword_list TEXT, "
        "UNIQUE(filename, category)"
        ")"
    )
    conn.execute(sql)
    conn.commit()
    return conn


def build_index():
    """从 book_index.json 重建 FTS5 索引"""
    if not os.path.exists(INDEX_JSON):
        print(f"❌ 索引文件不存在: {INDEX_JSON}")
        sys.exit(1)
    
    with open(INDEX_JSON, "r", encoding="utf-8") as f:
        idx = json.load(f)
    
    conn = init_db()
    
    # 清理旧数据
    conn.execute("DELETE FROM books")
    conn.execute("DELETE FROM book_fts")
    
    total = len(idx.get("books", []))
    inserted = 0
    
    for book in idx["books"]:
        fn = book.get("filename", "")
        cat = book.get("category", "")
        fmt = book.get("format", "")
        size_b = book.get("size_bytes", 0)
        size_mb = book.get("size_mb", 0)
        rpath = book.get("remote_path", "")
        
        # 提取关键词
        kw_list = extract_keywords(fn) + extract_keywords(cat)
        kw_list = list(set(kw_list))
        kw_str = " ".join(kw_list)
        kw_joined = ", ".join(kw_list)
        
        # 摘要
        checksum = hashlib.md5((fn + cat + kw_str).encode()).hexdigest()[:12]
        
        conn.execute(
            "INSERT OR IGNORE INTO books (filename, category, ext, size_bytes, size_mb, remote_path, keywords, keyword_list) VALUES (?,?,?,?,?,?,?,?)",
            (fn, cat, fmt, size_b, size_mb, rpath, kw_str, kw_joined)
        )
        if conn.execute("SELECT changes()").fetchone()[0] > 0:
            book_rowid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            conn.execute(
                "INSERT INTO book_fts (rowid, filename, category, keywords) VALUES (?,?,?,?)",
                (book_rowid, fn, cat, kw_str)
            )
            inserted += 1
    
    conn.commit()
    
    # 统计
    cursor = conn.execute("SELECT COUNT(*) FROM books")
    count = cursor.fetchone()[0]
    print(f"✅ 索引构建完成: {count} 本书 (共 {total} 条)")
    
    # 分类统计
    cats = conn.execute("SELECT category, COUNT(*) FROM books GROUP BY category ORDER BY COUNT(*) DESC").fetchall()
    print(f"\n📂 分类分布:")
    for cat, cnt in cats:
        print(f"  {cat}: {cnt}")
    
    conn.close()


def search(query: str, limit: int = 10) -> list[dict]:
    """FTS5 搜索"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.row_factory = sqlite3.Row
    
    # 先 FTS5 精确搜索
    rows = conn.execute(
        """SELECT b.*, rank FROM book_fts
           JOIN books b ON book_fts.rowid = b.rowid
           WHERE book_fts MATCH ?
           ORDER BY rank
           LIMIT ?""",
        (query, limit)
    ).fetchall()
    
    if not rows:
        # fallback: LIKE 模糊搜索
        like_q = f"%{query}%"
        rows = conn.execute(
            """SELECT * FROM books
               WHERE filename LIKE ? OR category LIKE ? OR keyword_list LIKE ?
               LIMIT ?""",
            (like_q, like_q, like_q, limit)
        ).fetchall()
    
    conn.close()
    return [dict(r) for r in rows]


def suggest(query: str, limit: int = 5) -> list[dict]:
    """自动建议模式 — 用于对话中快速匹配"""
    results = search(query, limit)
    if not results:
        return []
    return results


def format_suggestions(results: list[dict]) -> str:
    """格式化为可读的推荐列表"""
    if not results:
        return ""
    
    lines = ["📖 **知识库中查到相关书籍：**"]
    for i, r in enumerate(results[:5], 1):
        size_gb = r["size_mb"] / 1024 if r["size_mb"] > 100 else r["size_mb"]
        size_str = f"{size_gb:.1f}GB" if r["size_mb"] > 100 else f"{r['size_mb']:.0f}MB"
        lines.append(f"  {i}. **{r['filename']}** [{r['category']}] ({size_str})")
    
    lines.append(f"\n需要缓存某本分析吗？跟我说书名就行。")
    return "\n".join(lines)


# ── gbrain 同步 ────────────────────────────────────────────

def sync_to_gbrain():
    """将书库同步到 gbrain 知识图谱页"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    # 按分类统计
    cats = conn.execute("SELECT category, COUNT(*) as cnt FROM books GROUP BY category ORDER BY cnt DESC").fetchall()
    
    # 构建 gbrain 页面内容
    total = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
    total_gb = conn.execute("SELECT SUM(size_bytes) FROM books").fetchone()[0] / 1073741824
    
    # 紧凑版
    lines = [
        f"# 书籍知识库 (book/)",
        f"总数: {total} | 大小: {total_gb:.1f} GB",
        f"更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
    ]
    for cat in cats:
        books = conn.execute(
            "SELECT keyword_list FROM books WHERE category=? ORDER BY filename LIMIT 30",
            (cat["category"],)
        ).fetchall()
        kws = set()
        for b in books:
            if b["keyword_list"]:
                for kw in b["keyword_list"].split(", "):
                    if len(kw) >= 2:
                        kws.add(kw)
        top_kws = sorted(kws, key=lambda x: -len(x))[:20]
        lines.append(f"- {cat['category']}: {cat['cnt']}本 [{' '.join(top_kws)}]")
    
    content = "\n".join(lines)
    
    try:
        r = subprocess.run(
            ["gbrain", "put", GBRAIN_SLUG],
            input=content, capture_output=True, text=True, timeout=60
        )
        if r.returncode == 0:
            print(f"✅ gbrain 页面已写入: {GBRAIN_SLUG} ({len(content)} 字符)")
        else:
            print(f"⚠️ gbrain 写入失败: {r.stderr.strip()[:200]}")
    except Exception as e:
        print(f"⚠️ gbrain 写入异常: {e}")
    
    conn.close()


# ── 扫描 OneDrive 更新 ──────────────────────────────────────

def scan_updates():
    """扫描 onedrive:book/ 并与本地索引比较，更新 book_index.json"""
    print("⏳ 正在扫描 onedrive:book/ ...")
    
    listing_path = "/tmp/book_listing.txt"
    r = subprocess.run(
        ["rclone", "ls", "onedrive:book/"],
        capture_output=True, text=True, timeout=120
    )
    if r.returncode != 0:
        print(f"❌ rclone ls 失败: {r.stderr.strip()[:200]}")
        sys.exit(1)
    
    with open(listing_path, "w") as f:
        f.write(r.stdout)
    
    # 解析 rclone ls 输出
    # 格式: "    size path"
    new_books = []
    for line in r.stdout.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        parts = line.split(None, 1)
        if len(parts) < 2:
            continue
        size_str, path = parts
        if not size_str.isdigit():
            continue
        size = int(size_str)
        # 只处理文档格式
        if not any(path.lower().endswith(ext) for ext in ['.pdf','.epub','.mobi','.azw3','.djvu','.chm']):
            continue
        
        # 提取分类（目录名）
        path_parts = path.split("/")
        if len(path_parts) >= 2:
            category = path_parts[0]
            filename = "/".join(path_parts[1:])
        else:
            category = "根目录"
            filename = path
        
        ext = os.path.splitext(filename)[1].lower().lstrip(".")
        size_mb = size / 1048576
        
        new_books.append({
            "filename": filename,
            "category": category,
            "format": ext,
            "size_bytes": size,
            "size_mb": round(size_mb, 1),
            "remote_path": f"book/{path}"
        })
    
    # 加载现有索引
    if os.path.exists(INDEX_JSON):
        with open(INDEX_JSON, "r", encoding="utf-8") as f:
            old_idx = json.load(f)
        old_filenames = {b["filename"] for b in old_idx.get("books", [])}
    else:
        old_idx = {"last_updated": "", "total_files": 0, "total_size_gb": 0, "books": []}
        old_filenames = set()
    
    new_filenames = {b["filename"] for b in new_books}
    added = new_filenames - old_filenames
    removed = old_filenames - new_filenames
    
    if not added and not removed:
        print("✅ 无变化，索引已是最新")
        return
    
    total_gb = sum(b["size_bytes"] for b in new_books) / 1073741824
    
    new_idx = {
        "last_updated": datetime.now().isoformat(),
        "total_files": len(new_books),
        "total_size_gb": round(total_gb, 1),
        "books": new_books
    }
    
    with open(INDEX_JSON, "w", encoding="utf-8") as f:
        json.dump(new_idx, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 索引已更新: {len(new_books)} 本 ({total_gb:.1f} GB)")
    if added:
        print(f"  ➕ 新增: {len(added)} 本")
        for fn in sorted(added)[:10]:
            print(f"    - {fn}")
        if len(added) > 10:
            print(f"    ... (还有 {len(added)-10} 本)")
    if removed:
        print(f"  ➖ 移除: {len(removed)} 本")


# ── Main ────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "build":
        build_index()
    elif cmd == "search" and len(sys.argv) >= 3:
        results = search(sys.argv[2])
        if results:
            for r in results:
                sz = f"{r['size_mb']:.0f}MB" if r['size_mb'] < 100 else f"{r['size_mb']/1024:.1f}GB"
                print(f"📖 {r['filename']} [{r['category']}] ({sz})")
                print(f"   关键词: {r['keyword_list'][:100]}")
                print()
        else:
            print("❌ 未匹配")
    elif cmd == "suggest" and len(sys.argv) >= 3:
        results = suggest(sys.argv[2])
        print(format_suggestions(results))
    elif cmd == "sync-gbrain":
        sync_to_gbrain()
    elif cmd == "scan-updates":
        scan_updates()
        # 扫描后自动重建索引
        if os.path.exists(INDEX_JSON):
            build_index()
    else:
        print(__doc__)

if __name__ == "__main__":
    main()
