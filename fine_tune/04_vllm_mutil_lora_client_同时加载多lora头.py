import os

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from common.config import Config

conf = Config()

# ============ 配置llm区域 ============
# vLLM 服务地址从环境变量读取（VLLM_BASE_URL / VLLM_MODEL_NAME），
# 多 LoRA 融合调用时 model 必须填基座模型名。
my_llm = ChatOpenAI(
    api_key=os.getenv("VLLM_API_KEY", "EMPTY"),
    base_url=conf.VLLM_BASE_URL,
    model=conf.VLLM_MODEL_NAME or "Qwen/Qwen2.5-1.5B-Instruct",
    temperature=0.1,
)


def extract_knowledge_from_text(input_text):
    messages = [
        SystemMessage(content="请从以下中医文本中抽取知识图谱结构，包括实体与关系。"),
        HumanMessage(content=input_text)
    ]

    result = ""
    # 流式调用，同时传入多 LoRA 融合参数
    for chunk in my_llm.stream(
        messages,
        extra_body={
            "multi_modal": False,
            # 同时加载 2 个 LoRA 适配器（名称对应 vLLM 服务端注册的 adapter_name）
            "adapter_ids": ["law", "cs"],
            # 融合权重，建议和为 1
            "adapter_weights": [0.5, 0.5]
        }
    ):
        print(chunk.content, end="", flush=True)
        result += chunk.content

    return result


if __name__ == '__main__':
    sample_text = """
                【中药名称】一点血
- 中医百科
- 一点血
1#
名称
红砖草（《全展选编•妇产科》）、一点红、石鼓子、威氏秋海棠
红砖草石鼓子威氏秋海棠
- 红砖草
- 石鼓子
- 威氏秋海棠
一点血的种植和炮制
来源
为秋海棠科植物一点血秋海棠的根茎。秋后采挖，鲜用或晒干用。
【原形态】
多年生草本，高20～30厘米。根茎短而肥厚，有环纹，断面红色，具须根。根出叶1-2片，近菱方形，长lO～15厘米，宽lO～12厘米，上部3～7浅裂，裂片三角形，基部偏心形，边缘有突尖细锯齿，上面绿色，具极稀疏的短刺毛，下面略带紫色；叶柄光滑，基部肥厚，长7～15厘米；托叶膜质，光滑，褐色，卵圆披针形。花6～7朵，粉红色，呈伞房状排列，花序梗粗壮，根出，长达10～20厘米；花雌雄同株；雄花花被4片，内外各2，外花被卵圆形，内花被长椭圆形，雄蕊10～16枚，离生；雌花具花被3片，内1外2，外花被宽卵圆形，内花被卵圆形或长椭圆形，子房呈纺锤形，3棱，花柱3枚，离生。蒴果无翅。花期7月。
【生境分布】
生长于阴处的岩石缝及小谷底。产四川。
性味
味甘；苦；性微寒
性状
干燥根茎呈圆柱形，弯曲，外表棕黄色，具扭曲的纵皱纹及须根残痕。质脆，横断面平坦，中心有一棕红色的圆心，如一点血状。
一点血的效果
功效
为秋海棠科植物一点血秋海棠的根茎。用于病后虚弱，劳伤，血虚经闭，崩漏，白带，吐血，咯血，衄血，外伤出血，跌打肿痛。
主治
养血补血，散瘀止痛。主病后虚弱，劳伤，血虚经闭，崩漏，白带，吐血，咯血，衄血，外伤出血，跌打肿痛。
用法用量
- 内服：煎汤，15-30g；绞汁、炖肉或浸酒。
- 外用：适量，鲜品捣敷。
一点血的药方
- ①治虚弱带下：一点血、一朵云。共研末，炖肉服。
- ②治女子干病：一点血、玉芙蓉、鹿衔草、蓝布正。炖鸡子服。（性味以下出《四川中药志》）
- ③治功能性子宫出血：一点血鲜品四至五两，或干品二、三两。炖鸡服。（《全展选编•妇产科》）

                """

    final_result = extract_knowledge_from_text(sample_text)
    print(f"\n最终结果长度: {len(final_result)}")
