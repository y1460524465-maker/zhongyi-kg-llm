import os

from dotenv import load_dotenv

from common.path_utils import get_file_path

#把环境变量加载起来
load_dotenv(get_file_path("common/.env"))


#Config是用来读取.env中的配置的.
#创建了一个config类
class Config:
    #init 方法是模型实例化时候执行的
    def __init__(self):
        # 大模型相关
        #self: 表示的是对象本身
        self.MODEL_API_KEY = os.getenv("MODEL_API_KEY")
        self.MODEL_BASE_URL = os.getenv("MODEL_BASE_URL")
        self.MODEL_NAME = os.getenv("MODEL_NAME")

        # neo4j相关
        self.NEO4J_URI = os.getenv("NEO4J_URI")
        self.NEO4J_USER = os.getenv("NEO4J_USER")
        self.NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
        self.EMBEDDING_MODEL_PATH = os.getenv("EMBEDDING_MODEL_PATH")

        metadata_path = get_file_path(
            os.path.join("create_information", "neo4j_metadata.json"))
        with open(metadata_path, "r", encoding="utf-8") as f:
            self.TCM_METADATA = f.read()

        # LangSmith 可观测性（从环境变量读取，切勿把密钥硬编码进源码）
        self.LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
        self.LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", "false")

        # FAISS 索引与 id->文本 映射路径
        # 可用环境变量 FAISS_INDEX_PATH / FAISS_ID2TEXT_PATH 覆盖，
        # 默认使用项目内 create_information 下已生成的索引文件。
        self.FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH") or get_file_path(
            os.path.join("create_information", "nero4j_embedding_faiss.index"))
        self.FAISS_ID2TEXT_PATH = os.getenv("FAISS_ID2TEXT_PATH") or get_file_path(
            os.path.join("create_information", "nero4j_embedding_faiss_id2text.pkl"))

        # vLLM 推理服务（本地或云端部署，fine_tune 下的多 LoRA 示例使用）
        self.VLLM_BASE_URL = os.getenv("VLLM_BASE_URL", "http://localhost:8000/v1")
        self.VLLM_MODEL_NAME = os.getenv("VLLM_MODEL_NAME", "")

        self.JIMENG_AK = os.getenv("JIMENG_AK")
        self.JIMENG_SK = os.getenv("JIMENG_SK")
        self.DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
        # 添加历史数据获取的轮数
        self.history_num = 5



if __name__ == "__main__":
    # 类实例化 ,创建对象
    conf = Config()
    # print(conf.MODEL_API_KEY)
    # print(conf.MODEL_BASE_URL)
    # print(conf.MODEL_NAME)
    print(conf.TCM_METADATA)
    # print(conf.EMBEDDING_MODEL_PATH)
