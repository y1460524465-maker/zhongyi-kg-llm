"""
测试FAISS索引加载功能
"""
import sys
import os

# 添加父目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from langgraph_more_nodes.nodes.match_entity_node import load_faiss_resources

def test_load_faiss():
    """测试FAISS索引加载"""
    print("=" * 60)
    print("🧪 测试FAISS索引加载")
    print("=" * 60)
    
    try:
        print("\n正在加载FAISS索引...")
        index, id2text = load_faiss_resources()
        
        print(f"\n✅ FAISS索引加载成功！")
        print(f"   - 索引中包含 {index.ntotal} 个向量")
        print(f"   - ID映射中包含 {len(id2text)} 个实体")
        
        # 显示前5个实体作为示例
        print(f"\n前5个实体示例:")
        for i in range(min(5, len(id2text))):
            print(f"   {i}: {id2text[i]}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ FAISS索引加载失败！")
        print(f"   错误信息: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = test_load_faiss()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ 测试通过！FAISS索引可以正常加载")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ 测试失败！请检查文件路径和文件是否存在")
        print("=" * 60)
