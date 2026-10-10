import os
import json
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.neo4j_manager import Neo4jClient
from common.config import Config

class MetadataExporter:
    def __init__(self, client):
        self.client = client

    def get_all_node_labels(self):
        """获取所有节点标签"""
        cypher = "CALL db.labels()"
        result = self.client.run_cypher(cypher)
        return [record['label'] for record in result]

    def get_all_relation_types(self):
        """获取所有关系类型"""
        cypher = "CALL db.relationshipTypes()"
        result = self.client.run_cypher(cypher)
        return [record['relationshipType'] for record in result]

    def get_node_properties(self, label):
        """获取指定标签的节点属性键"""
        cypher = f"""
        MATCH (n:`{label}`)
        WITH n LIMIT 1
        RETURN keys(n) as properties
        """
        result = self.client.run_cypher(cypher)
        if result:
            return result[0]['properties']
        return []

    def get_relation_properties(self, rel_type):
        """获取指定关系类型的属性键"""
        cypher = f"""
        MATCH ()-[r:`{rel_type}`]->()
        WITH r LIMIT 1
        RETURN keys(r) as properties
        """
        result = self.client.run_cypher(cypher)
        if result:
            return result[0]['properties']
        return []

    def get_triple_patterns(self):
        """获取所有三元组结构（模式）"""
        cypher = """
        MATCH (s)-[r]->(o)
        RETURN DISTINCT labels(s)[0] as source_label, 
                       type(r) as relation_type, 
                       labels(o)[0] as target_label
        ORDER BY source_label, relation_type, target_label
        """
        result = self.client.run_cypher(cypher)
        triples = []
        for record in result:
            triples.append({
                "source_label": record['source_label'],
                "relation_type": record['relation_type'],
                "target_label": record['target_label']
            })
        return triples

    def export_metadata(self, output_file="neo4j_metadata.json"):
        """导出所有元数据到JSON文件"""
        print("开始导出 Neo4j 元数据...")
        
        metadata = {
            "node_labels": [],
            "relation_types": [],
            "triple_patterns": [],
            "node_properties": {},
            "relation_properties": {}
        }

        # 1. 获取所有节点标签
        print("获取节点标签...")
        labels = self.get_all_node_labels()
        metadata["node_labels"] = sorted(labels)
        print(f"  共 {len(labels)} 个节点标签")

        # 2. 获取所有关系类型
        print("获取关系类型...")
        rel_types = self.get_all_relation_types()
        metadata["relation_types"] = sorted(rel_types)
        print(f"  共 {len(rel_types)} 种关系类型")

        # 3. 获取三元组结构
        print("获取三元组结构...")
        triples = self.get_triple_patterns()
        metadata["triple_patterns"] = triples
        print(f"  共 {len(triples)} 种三元组模式")

        # 4. 获取每个标签的节点属性
        print("获取节点属性...")
        for label in labels:
            props = self.get_node_properties(label)
            metadata["node_properties"][label] = sorted(props)
            print(f"  {label}: {len(props)} 个属性")

        # 5. 获取每种关系的属性
        print("获取关系属性...")
        for rel_type in rel_types:
            props = self.get_relation_properties(rel_type)
            metadata["relation_properties"][rel_type] = sorted(props)
            print(f"  {rel_type}: {len(props)} 个属性")

        # 保存到文件
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        print(f"\n元数据已导出到: {output_file}")
        return metadata

def main():
    print("=" * 50)
    print("📊 Neo4j 元数据导出工具")
    print("=" * 50)

    # 初始化配置和客户端
    conf = Config()
    client = Neo4jClient(conf.NEO4J_URI, conf.NEO4J_USER, conf.NEO4J_PASSWORD)

    # 创建导出器
    exporter = MetadataExporter(client)

    # 执行导出
    exporter.export_metadata()

    # 关闭连接
    client.close()

    print("\n✅ 导出完成！")

if __name__ == '__main__':
    main()