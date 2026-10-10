import requests
import time

BASE_URL = "http://localhost:8000"

# 健康检查接口测试
def test_health_check():
    """测试健康检查接口"""
    print("=" * 60)
    print("🧪 测试健康检查接口 GET /")
    print("=" * 60)
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

#测试中医问答的核心业务接口
def test_process_api():
    """测试核心问答接口 POST /process"""
    print("\n" + "=" * 60)
    print("🧪 测试问答接口 POST /process")
    print("=" * 60)

    test_cases = [
        {"input": "拉肚子了该吃什么要？"},
        {"input": "今天天气怎么样？"},
        {"input": ""}  # 空输入测试
    ]

    for i, test_data in enumerate(test_cases, 1):
        print(f"\n--- 测试用例 {i} ---")
        print(f"输入: {test_data}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/process",
                json=test_data
            )
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"输入: {result.get('input')}")
                print(f"输出: {result.get('output', '')[:100]}...")
                print("✅ 查询成功")
            else:
                print(f"❌ 查询失败: {response.text}")
                
        except Exception as e:
            print(f"❌ 请求失败: {e}")


if __name__ == "__main__":
    print("=" * 80)
    print("🚀 中医知识图谱问答系统 - API测试")
    print("=" * 80)
    print(f"服务地址: {BASE_URL}")
    print()

    print("⏳ 等待服务启动...")
    time.sleep(3)

    if not test_health_check():
        print("\n❌ 服务未启动，请先运行 start_server.bat 启动服务")
        exit(1)

    test_process_api()

    print("\n" + "=" * 80)
    print("🎉 测试完成")
    print("=" * 80)