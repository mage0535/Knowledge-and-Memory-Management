"""
知识增广（Knowledge Augmentation）— 本地搜索 + AnySearch 垂直搜索自动回落

搜索链路:
  用户提问 → search_notes(query)
    ├─ 本地笔记命中 (score ≥ threshold) → 直接返回
    └─ 本地笔记未命中 (score < threshold) → AnySearch 垂直搜索
         ├─ domain 自动匹配笔记主题
         └─ 结果可 → generate_note() 写入笔记库
"""

from .config import AugmentationConfig, load_config
from .anysearch_client import AnySearchClient, AnySearchError
from .augmented_search import AugmentedSearch

__all__ = [
    "AugmentationConfig",
    "load_config",
    "AnySearchClient",
    "AnySearchError",
    "AugmentedSearch",
]
