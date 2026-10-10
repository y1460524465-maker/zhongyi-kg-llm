from neo4j import GraphDatabase
from common.config import Config
from tqdm import tqdm
import json

conf = Config()

class Neo4jClient:
    #建立连接对象（惰性：首次真正查询时才创建 driver，避免 import 阶段就连库）
    def __init__(self, url, user, password):
        self._url = url
        self._auth = (user, password)
        self._driver = None

    @property
    def driver(self):
        """惰性创建 driver：只有真正执行查询时才建立连接。"""
        if self._driver is None:
            if not self._url:
                raise RuntimeError("未配置 NEO4J_URI，请在 common/.env 中填写 Neo4j 连接信息")
            self._driver = GraphDatabase.driver(self._url, auth=self._auth)
        return self._driver

    #释放连接意向
    def __del__(self):
        if self._driver is not None:
            self._driver.close()
            self._driver = None
    #执行cypher 语句,获取结果
    def run_cypher(self, cypher, parameters=None):
        with self.driver.session() as session:
            result = session.run(cypher, parameters)
            return list(result)

    def run_multiple_cypher(self, queries_with_params):
        """
        执行多条 Cypher 语句，使用事务，并显示 tqdm 进度条。

        参数:
            queries_with_params: List[Tuple[str, Dict]]
                形式如: [("CREATE (n:Test {name: $name})", {"name": "Alice"}), ...]
        """
        with self.driver.session() as session:
            def transaction_logic(tx):
                for query, params in tqdm(queries_with_params, desc="执行 Cypher 语句"):
                    tx.run(query, params or {})

            session.execute_write(transaction_logic)

    def delete_all(self):
        """删除数据库中所有节点和关系"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

    def close(self):
        if self._driver is not None:
            self._driver.close()
            self._driver = None

    def get_all_node_names(self, label: str = None):
        """
        获取指定标签下所有节点的 name 属性
        :param label: 节点标签（如 'Effect', 'Symptom', 'Disease'）
        :return: List[str]
        """
        if label is None:
            query = """
            MATCH (n)
            RETURN DISTINCT n.name AS name
            ORDER BY name
            """
        else:
            query = f"""
            MATCH (n:{label})
            RETURN DISTINCT n.name AS name
            ORDER BY name
            """
        with self.driver.session() as session:
            result = session.run(query)
            return [record["name"] for record in result if record["name"]]

neo4j_client = Neo4jClient(conf.NEO4J_URI, conf.NEO4J_USER, conf.NEO4J_PASSWORD)

if __name__ == '__main__':
    client = Neo4jClient(conf.NEO4J_URI, conf.NEO4J_USER, conf.NEO4J_PASSWORD)

    print("=== 测试用例1: 查询单个节点 ===")
    cypher = "MATCH (n) RETURN n LIMIT 1"
    result = client.run_cypher(cypher)
    print(f"查询结果数量: {len(result)}")
    if result:
        print(f"第一条记录: {result[0].data()}")

    print("\n=== 测试用例2: 带参数的查询 ===")
    cypher = "MATCH (n {name: $name}) RETURN n"
    result = client.run_cypher(cypher, {"name": "Herb"})
    print(f"查询结果数量: {len(result)}")

    # print("\n=== 测试用例3: 统计节点数量 ===")
    # cypher = "MATCH (n) RETURN count(n) as total"
    # result = client.run_cypher(cypher)
    # if result:
    #     print(f"节点总数: {result[0]['total']}")
    #
    # print("\n=== 测试用例4: 查询所有节点和关系 ===")
    # cypher = "MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 5"
    # result = client.run_cypher(cypher)
    # print(f"关系数量: {len(result)}")
    all_node_names = client.get_all_node_names()
    print(all_node_names[0:10])
    client.close()
    print("\n所有测试用例执行完成!")
