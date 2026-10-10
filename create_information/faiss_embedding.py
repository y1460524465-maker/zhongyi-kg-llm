from common.neo4j_manager import neo4j_client
import pickle
import faiss
from common.embedding_model import embedding_model


def build_faiss_index(sentences, index_path="faiss.index", mapping_path="id2text.pkl"):
    """
    基于字符串列表构建 FAISS 索引并保存
    :param sentences: List[str] 输入的文本列表
    :param index_path: FAISS 索引保存路径
    :param mapping_path: id->原始文本映射保存路径
    """
    # 1. 加载预训练文本向量模型

    # 2. 生成向量
    embeddings = embedding_model.encode(sentences, convert_to_numpy=True, normalize_embeddings=True)
    # 3. 构建 FAISS 索引
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)  # L2距离,欧式距离
    index.add(embeddings)

    # 4. 保存索引,到硬盘上 index_path="nero4j_embedding_faiss.index"
    faiss.write_index(index, index_path)

    # 5. 保存 id -> 原始文本 映射
    id2text = {i: s for i, s in enumerate(sentences)}
    with open(mapping_path, "wb") as f:
        # 索引id到原始文本的一个映射
        pickle.dump(id2text, f)

    print(f"✅ 索引已保存到 {index_path}, 映射保存到 {mapping_path}")


def load_faiss_index(index_path="nero4j_embedding_faiss.index", mapping_path="nero4j_embedding_faiss_id2text.pkl"):
    """
    加载已有的 FAISS 索引和 id->文本映射
    :param index_path: FAISS 索引文件路径
    :param mapping_path: id->文本映射文件路径
    :return: (index, id2text) 索引对象和映射字典
    """
    # 加载 FAISS 索引
    index = faiss.read_index(index_path)
    print(f"✅ 索引加载成功，包含 {index.ntotal} 个向量")
    
    # 加载 id->文本映射
    with open(mapping_path, "rb") as f:
        id2text = pickle.load(f)
    print(f"✅ 映射加载成功，包含 {len(id2text)} 个实体")
    
    return index, id2text


def search_similar(index, id2text, query, top_k=5, similarity_threshold=0.5):
    """
    在 FAISS 索引中搜索相似文本
    :param index: FAISS 索引对象
    :param id2text: id->文本映射字典
    :param query: 查询文本
    :param top_k: 返回前 top_k 个结果
    :param similarity_threshold: 相似度阈值，只有相似度大于此值的结果才返回（范围: 0.0-1.0）
    :return: List[dict] 包含实体和相似度的列表
    """
    # 生成查询向量
    query_embedding = embedding_model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
    
    # 搜索相似向量
    distances, indices = index.search(query_embedding, top_k)
    
    # 整理结果
    results = []
    for i, idx in enumerate(indices[0]):
        if idx != -1:  # -1 表示没有匹配
            entity = id2text.get(idx, "")
            if entity:
                # L2距离越小相似度越高，转换为相似度分数 (0-1)
                similarity = 1.0 / (1.0 + distances[0][i])
                # 应用相似度阈值过滤
                if similarity >= similarity_threshold:
                    results.append({
                        "entity": entity,
                        "distance": float(distances[0][i]),
                        "similarity": round(similarity, 4)
                    })
    
    return results


if __name__ == '__main__':
    # # 获取所有节点名称
    # node_names = neo4j_client.get_all_node_names()
    #
    # # 将节点进行向量化
    # build_faiss_index(node_names, index_path="nero4j_embedding_faiss.index",
    #           mapping_path="nero4j_embedding_faiss_id2text.pkl")
    
    # 测试查询功能
    print("=" * 60)
    print("🔍 FAISS 向量索引查询测试")
    print("=" * 60)
    
    # 加载索引
    index, id2text = load_faiss_index()
    
    # 测试查询
    test_queries = ["拉肚子"]
    
    for query in test_queries:
        print(f"\n查询: {query}")
        results = search_similar(index, id2text, query, top_k=3)
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['entity']} (相似度: {result['similarity']:.4f}, 距离: {result['distance']:.4f})")