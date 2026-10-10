import os
import json
from pathlib import Path
from tqdm import tqdm
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.neo4j_manager import Neo4jClient
from common.config import Config

class TCMDataImporter:
    def __init__(self, client):
        self.client = client

    def load_json_files(self, directory):
        """加载指定目录下的所有JSON文件"""
        json_files = []
        for file in Path(directory).glob('*.json'):
            # 跳过alpaca数据集和中医相关的非数据文件
            if file.name.startswith('alpaca_') or file.name.startswith('中医'):
                continue
            json_files.append(file)
        return sorted(json_files)

    def parse_json_file(self, file_path):
        """解析单个JSON文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"解析文件失败 {file_path}: {e}")
            return None

    def create_node_cypher(self, entity):
        """生成创建节点的Cypher语句"""
        name = entity.get('name')
        node_type = entity.get('type', 'Entity')
        attributes = entity.get('attributes', {})

        if not name:
            return None, None

        if attributes:
            attr_str = ', '.join([f"{k}: ${k}" for k in attributes.keys() if attributes[k] is not None])
            cypher = f"MERGE (n:{node_type} {{name: $name}}) SET n += {{{attr_str}}}"
            params = {"name": name}
            params.update({k: v for k, v in attributes.items() if v is not None})
        else:
            cypher = f"MERGE (n:{node_type} {{name: $name}})"
            params = {"name": name}

        return cypher, params

    def create_relation_cypher(self, relation):
        """生成创建关系的Cypher语句"""
        subject = relation.get('subject')
        subject_type = relation.get('subject_type', 'Entity')
        rel_type = relation.get('relation')
        obj = relation.get('object')
        obj_type = relation.get('object_type', 'Entity')

        if not all([subject, rel_type, obj]):
            return None, None

        cypher = f"""
        MATCH (s:{subject_type} {{name: $subject}})
        MATCH (o:{obj_type} {{name: $object}})
        MERGE (s)-[r:{rel_type}]->(o)
        """
        params = {"subject": subject, "object": obj}

        return cypher, params

    def import_data(self, herb_dir, formula_dir):
        """执行数据导入"""
        all_files = []
        all_files.extend(self.load_json_files(herb_dir))
        all_files.extend(self.load_json_files(formula_dir))

        print(f"找到 {len(all_files)} 个数据文件")

        entity_cyphers = []
        entity_params = []
        relation_cyphers = []
        relation_params = []

        for file in tqdm(all_files, desc="解析数据文件"):
            data = self.parse_json_file(file)
            if not data:
                continue

            # 处理实体
            for entity in data.get('entities', []):
                cypher, params = self.create_node_cypher(entity)
                if cypher and params:
                    entity_cyphers.append(cypher)
                    entity_params.append(params)

            # 处理关系
            for relation in data.get('relations', []):
                cypher, params = self.create_relation_cypher(relation)
                if cypher and params:
                    relation_cyphers.append(cypher)
                    relation_params.append(params)

        print(f"\n共提取 {len(entity_cyphers)} 个实体和 {len(relation_cyphers)} 个关系")

        # 写入实体
        print("\n开始写入实体节点...")
        success_count = 0
        for cypher, params in tqdm(zip(entity_cyphers, entity_params), total=len(entity_cyphers), desc="写入实体"):
            try:
                self.client.run_cypher(cypher, params)
                success_count += 1
            except Exception as e:
                pass

        # 写入关系
        print("\n开始写入关系...")
        rel_success_count = 0
        for cypher, params in tqdm(zip(relation_cyphers, relation_params), total=len(relation_cyphers), desc="写入关系"):
            try:
                self.client.run_cypher(cypher, params)
                rel_success_count += 1
            except Exception as e:
                pass

        print(f"\n数据导入完成！成功写入 {success_count} 个实体，{rel_success_count} 个关系")

    def clear_database(self):
        """清空数据库"""
        self.client.delete_all()
        print("数据库已清空")

    def verify_import(self):
        """验证导入结果"""
        print("\n" + "=" * 50)
        print("验证数据导入结果:")
        print("=" * 50)

        # 统计节点数量
        result = self.client.run_cypher("MATCH (n) RETURN labels(n)[0] as type, count(n) as count ORDER BY count DESC")
        if result:
            for record in result:
                print(f"  {record['type']}: {record['count']} 个节点")
        else:
            print("  未找到节点")

        # 统计关系数量
        rel_result = self.client.run_cypher("MATCH ()-[r]->() RETURN type(r) as relation, count(r) as count ORDER BY count DESC")
        if rel_result:
            for record in rel_result:
                print(f"  {record['relation']}: {record['count']} 条关系")
        else:
            print("  未找到关系")

def main():
    print("=" * 50)
    print("🏥 中医知识图谱数据导入工具")
    print("=" * 50)

    # 初始化配置和客户端
    conf = Config()
    client = Neo4jClient(conf.NEO4J_URI, conf.NEO4J_USER, conf.NEO4J_PASSWORD)

    # 创建导入器
    importer = TCMDataImporter(client)

    # 定义数据目录路径
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    herb_dir = os.path.join(project_root, 'extract_information', '中药_json')
    formula_dir = os.path.join(project_root, 'extract_information', '方剂_json')

    # 检查目录是否存在
    if not os.path.exists(herb_dir):
        print(f"错误：中药数据目录不存在: {herb_dir}")
        return
    if not os.path.exists(formula_dir):
        print(f"错误：方剂数据目录不存在: {formula_dir}")
        return

    # 清空数据库
    importer.clear_database()

    # 执行导入
    importer.import_data(herb_dir, formula_dir)

    # 验证导入结果
    importer.verify_import()

    # 关闭连接
    client.close()

    print("\n✅ 所有任务执行完成！")

if __name__ == '__main__':
    main()