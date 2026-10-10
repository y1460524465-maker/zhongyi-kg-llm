"""向量模型封装：惰性加载，避免 import 时下载/加载权重。"""

import os
from typing import List

import torch

from common.config import Config

# 尝试导入sentence-transformers库
# 如果没有安装，可以使用pip install sentence-transformers
from sentence_transformers import SentenceTransformer

# 如果torch装的是cpu版本，就没法使用gpu
device = "cuda" if torch.cuda.is_available() else "cpu"


def _build_model() -> SentenceTransformer:
    """按配置构建向量模型；未配置路径时给出明确提示，而不是回退到本机私有路径。"""
    config = Config()
    model_path = config.EMBEDDING_MODEL_PATH
    if not model_path or not os.path.exists(model_path):
        raise RuntimeError(
            "未找到本地向量模型，请在 common/.env 中配置 EMBEDDING_MODEL_PATH，"
            "指向本地 bge-large-zh-v1.5 模型目录。"
        )
    return SentenceTransformer(model_path, device=device)


class EmbeddingModel:
    """嵌入模型类，用于将文本转换为向量表示（首次使用时才加载权重）"""

    def __init__(self):
        self._model = None

    @property
    def model(self) -> SentenceTransformer:
        """惰性加载：只有真正用到模型时才加载权重，避免 import 即卡住。"""
        if self._model is None:
            self._model = _build_model()
        return self._model

    def encode(self, texts: List[str], convert_to_numpy=False, normalize_embeddings=False) -> List[List[float]]:
        """
        将文本列表转换为向量表示

        Args:
            texts: 文本列表
            convert_to_numpy: 是否将结果转换为numpy数组
            normalize_embeddings: 是否对向量进行归一化

        Returns:
            向量列表或numpy数组，每个向量对应一个文本
        """
        return self.model.encode(texts, convert_to_numpy=convert_to_numpy, normalize_embeddings=normalize_embeddings)


# 全局对象：仅创建轻量包装，不加载权重
embedding_model = EmbeddingModel()


if __name__ == '__main__':
    print(f"device: {device}")
    print(embedding_model.encode(["你好"]))
    print(f"embedding dim: {embedding_model.model.get_embedding_dimension()}")
