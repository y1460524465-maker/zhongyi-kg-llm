import os
import json
import importlib.util
import sys
import concurrent.futures
from tqdm import tqdm

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 全局变量 - 用于多线程环境
extract_tcm_knowledge = None

def init_extract_module():
    """初始化抽取模块（在每个进程中调用）"""
    global extract_tcm_knowledge
    if extract_tcm_knowledge is None:
        spec = importlib.util.spec_from_file_location("tcm_extract", "01_tcm_kg_extract_info.py")
        tcm_extract = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tcm_extract)
        extract_tcm_knowledge = tcm_extract.extract_tcm_knowledge

def process_single_file(args):
    """处理单个文件（用于并发执行）"""
    filepath, zhongyao_name, output_dir, resume = args

    # 初始化模块
    init_extract_module()

    # 再次检查（防止并发情况）
    output_file = os.path.join(output_dir, f"{zhongyao_name}.json")
    if resume and os.path.exists(output_file):
        return {"status": "skip", "name": zhongyao_name, "error": None, "alpaca_item": None}

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()

        if not text.strip():
            return {"status": "empty", "name": zhongyao_name, "error": None, "alpaca_item": None}

        result = extract_tcm_knowledge(text)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        # 添加到 Alpaca 数据集
        alpaca_item = {
            "instruction": "请帮我抽取一下内容的实体和关系",
            "input": text[:500] + "..." if len(text) > 500 else text,
            "output": json.dumps(result, ensure_ascii=False)
        }

        return {"status": "success", "name": zhongyao_name, "error": None, "alpaca_item": alpaca_item}

    except Exception as e:
        return {"status": "fail", "name": zhongyao_name, "error": str(e), "alpaca_item": None}

def extract_zhongyao_to_json(input_dir="../clawler/中药", output_dir="中药_json", limit=0, resume=True, max_workers=100):
    """遍历中药目录，抽取知识并保存为JSON文件

    Args:
        input_dir: 输入目录
        output_dir: 输出目录
        limit: 限制抽取数量（0表示不限制，抽取所有）
        resume: 是否启用断点续抽（默认True，跳过已抽取的文件）
        max_workers: 并发线程数（默认100）
    """

    if not os.path.exists(input_dir):
        print(f"错误：输入目录 {input_dir} 不存在")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Alpaca 数据集列表
    alpaca_data = []

    txt_files = [f for f in os.listdir(input_dir) if f.endswith('.txt')]
    txt_files.sort()

    # 断点续抽：获取已抽取的文件列表
    existing_files = set()
    if resume:
        existing_json_files = [f for f in os.listdir(output_dir) if f.endswith('.json') and f != "alpaca_zhongyao_dataset.json"]
        existing_files = set([f.replace('.json', '') for f in existing_json_files])
        print(f"发现已抽取 {len(existing_files)} 个文件，启用断点续抽...")

    print(f"发现 {len(txt_files)} 个中药文件")

    # 过滤需要处理的文件
    files_to_process = []
    for filename in txt_files:
        zhongyao_name = filename.replace('.txt', '')
        if resume and zhongyao_name in existing_files:
            # 加载已存在的文件到 alpaca_data
            output_file = os.path.join(output_dir, f"{zhongyao_name}.json")
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    result = json.load(f)
                alpaca_item = {
                    "instruction": "请帮我抽取一下内容的实体和关系",
                    "input": "",
                    "output": json.dumps(result, ensure_ascii=False)
                }
                alpaca_data.append(alpaca_item)
            except Exception as e:
                print(f"[WARN] 加载已有文件失败: {zhongyao_name} - {e}")
                files_to_process.append((os.path.join(input_dir, filename), zhongyao_name))
            continue
        files_to_process.append((os.path.join(input_dir, filename), zhongyao_name))

    print(f"本次需要处理 {len(files_to_process)} 个文件")

    if limit > 0:
        files_to_process = files_to_process[:limit]
        print(f"限制抽取前 {limit} 个...")

    print(f"使用 {max_workers} 个线程并发处理...")

    success_count = 0
    skip_count = 0
    empty_count = 0
    fail_count = 0

    # 构建参数列表
    args_list = [(filepath, zhongyao_name, output_dir, resume)
                 for filepath, zhongyao_name in files_to_process]

    # 使用 ThreadPoolExecutor 并发处理
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 使用 tqdm 显示进度
        results = list(tqdm(executor.map(process_single_file, args_list),
                            total=len(args_list), desc="抽取进度", unit="个"))

    # 统计结果
    for result in results:
        if result["status"] == "success":
            success_count += 1
            print(f"[OK] {result['name']}")
            if result["alpaca_item"]:
                alpaca_data.append(result["alpaca_item"])
        elif result["status"] == "skip":
            skip_count += 1
        elif result["status"] == "empty":
            empty_count += 1
            print(f"[SKIP] {result['name']} 内容为空")
        elif result["status"] == "fail":
            fail_count += 1
            print(f"[FAIL] {result['name']} - {result['error']}")

    # 保存 Alpaca 数据集
    if alpaca_data:
        alpaca_file = os.path.join(output_dir, "alpaca_zhongyao_dataset.json")
        with open(alpaca_file, 'w', encoding='utf-8') as f:
            json.dump(alpaca_data, f, ensure_ascii=False, indent=2)
        print(f"\nAlpaca 数据集已保存到: {alpaca_file}")

    print(f"\n抽取完成！成功: {success_count} 个, 跳过: {skip_count} 个, 空文件: {empty_count} 个, 失败: {fail_count} 个")
    print(f"结果已保存到: {output_dir}/")

if __name__ == '__main__':
    # 示例：使用100个线程并发抽取所有数据
    extract_zhongyao_to_json(limit=0, max_workers=100)