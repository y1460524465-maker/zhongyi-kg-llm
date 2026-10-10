import os
import pickle

import faiss
from langchain_core.runnables import RunnableConfig

from langgraph_more_nodes.agent_state import AgentState
from common.config import Config
from common.embedding_model import embedding_model
from api.msg_queue_manager import msg_queue_manager


def load_faiss_resources():
    """加载FAISS索引和id到文本的映射"""
    # 路径来自配置：可用环境变量 FAISS_INDEX_PATH / FAISS_ID2TEXT_PATH 覆盖，
    # 默认指向项目内 create_information 下已生成的索引文件。
    conf = Config()
    index_path = conf.FAISS_INDEX_PATH
    id2text_path = conf.FAISS_ID2TEXT_PATH

    print(f"  FAISS索引路径: {index_path}")
    print(f"  ID映射路径: {id2text_path}")
    
    # 检查文件是否存在
    if not os.path.exists(index_path):
        raise FileNotFoundError(
            f"FAISS索引文件不存在: {index_path}\n"
            "请先运行 create_information/faiss_embedding.py 生成索引，"
            "或用环境变量 FAISS_INDEX_PATH 指定路径。"
        )
    if not os.path.exists(id2text_path):
        raise FileNotFoundError(
            f"ID映射文件不存在: {id2text_path}\n"
            "请先运行 create_information/faiss_embedding.py 生成索引，"
            "或用环境变量 FAISS_ID2TEXT_PATH 指定路径。"
        )
    
    print(f"  文件存在性检查通过")
    
    try:
        # 尝试加载FAISS索引
        index = faiss.read_index(index_path)
        print(f"  FAISS索引加载成功")
    except Exception as e:
        print(f"  FAISS索引加载失败: {e}")
        print(f"  错误类型: {type(e).__name__}")
        raise e
    
    # 加载ID映射
    with open(id2text_path, 'rb') as f:
        id2text = pickle.load(f)
    print(f"  ID映射加载成功，包含 {len(id2text)} 个实体")
    
    return index, id2text


def search_similar_entity(entity: str, index, id2text, top_k: int = 1, similarity_threshold: float = 0.8):
    """在FAISS索引中搜索单个实体的最相似标准实体"""
    if not entity:
        return None

    query_embedding = embedding_model.encode([entity], convert_to_numpy=True, normalize_embeddings=True)
    distances, indices = index.search(query_embedding, top_k)

    if indices[0][0] != -1:
        matched = id2text.get(indices[0][0], None)
        if matched:
            distance = float(distances[0][0])
            similarity = 1.0 / (1.0 + distance)

            if similarity >= similarity_threshold:
                return {
                    "original": entity,
                    "matched": matched,
                    "distance": distance,
                    "similarity": similarity
                }
    return None


def match_entities_batch(entities: list, index, id2text, top_k: int = 1, similarity_threshold: float = 0.8) -> list:
    """批量匹配实体列表"""
    if not entities:
        return []

    results = []
    for entity in entities:
        matched = search_similar_entity(entity, index, id2text, top_k, similarity_threshold)
        if matched:
            results.append(matched)
    return results


def match_entity_node(state: AgentState, config: RunnableConfig, similarity_threshold: float = 0.65) -> AgentState:
    """
    从FAISS向量数据库匹配标准实体名
    - 输入：从user_input_*字段获取实体列表
    - 输出：匹配结果写入matched_*字段
    """
    user_id = config.get("configurable", {}).get("thread_id", "default")

    print(f"开始从FAISS向量数据库匹配标准实体名（阈值: {similarity_threshold}）")
    msg_queue_manager.put_msg_content(user_id, "🔗 正在匹配知识图谱实体...")

    try:
        index, id2text = load_faiss_resources()
        print(f"FAISS索引加载成功，包含 {index.ntotal} 个实体")
    except Exception as e:
        print(f"FAISS索引加载失败: {e}")
        state["matched_symptoms"] = []
        state["matched_diseases"] = []
        state["matched_formulas"] = []
        state["matched_herbs"] = []
        state["matched_effects"] = []
        state["matched_sources"] = []
        return state

    entity_fields = [
        ("user_input_symptoms", "matched_symptoms"),
        ("user_input_diseases", "matched_diseases"),
        ("user_input_formulas", "matched_formulas"),
        ("user_input_herbs", "matched_herbs"),
        ("user_input_effects", "matched_effects"),
        ("user_input_sources", "matched_sources"),
    ]

    for source_field, target_field in entity_fields:
        entities = state.get(source_field, [])
        if entities:
            matched_list = match_entities_batch(entities, index, id2text, similarity_threshold=similarity_threshold)
            state[target_field] = [m["matched"] for m in matched_list]

            for m in matched_list:
                print(f"  {source_field}: '{m['original']}' -> '{m['matched']}' (相似度: {m['similarity']:.4f})")

            print(f"  {source_field} -> {target_field}: 匹配到 {len(matched_list)}/{len(entities)} 个标准实体")
        else:
            state[target_field] = []
            print(f"  {source_field}: 无实体需要匹配")

    print("标准实体匹配完成")
    return state


if __name__ == '__main__':
    print("=" * 60)
    print("🧪 实体匹配节点测试")
    print("=" * 60)

    test_cases = [
        {
            "user_input_symptoms": ["拉肚子", "发热"],
            "user_input_diseases": ["感冒"],
            "user_input_formulas": [],
            "user_input_herbs": [],
            "user_input_effects": [],
            "user_input_sources": ["伤寒论"]
        },
        {
            "user_input_symptoms": ["失眠", "头痛"],
            "user_input_diseases": [],
            "user_input_formulas": ["桂枝汤"],
            "user_input_herbs": ["人参", "黄芪"],
            "user_input_effects": ["清热", "补气"],
            "user_input_sources": []
        },
    ]

    for i, test_state in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"测试 {i}")
        print("=" * 60)

        result = match_entity_node(test_state)

        print("\n匹配结果:")
        print(f"  matched_symptoms: {result.get('matched_symptoms', [])}")
        print(f"  matched_diseases: {result.get('matched_diseases', [])}")
        print(f"  matched_formulas: {result.get('matched_formulas', [])}")
        print(f"  matched_herbs: {result.get('matched_herbs', [])}")
        print(f"  matched_effects: {result.get('matched_effects', [])}")
        print(f"  matched_sources: {result.get('matched_sources', [])}")
