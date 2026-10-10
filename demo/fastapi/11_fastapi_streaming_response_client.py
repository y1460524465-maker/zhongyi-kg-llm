import requests


def stream_client():
    url = "http://localhost:8000/stream"

    # 发送 POST 请求并设置 stream=True 以启用流式响应
    # 1. post方法中需要使用 stream=True这个参数, 表示启用流式响应, requests.post 要用with
    with requests.post(url, stream=True) as response:
        # 检查响应状态码
        if response.status_code == 200:
            # 逐行读取流式响应
            for chunk in response.iter_content(chunk_size=None):
                if chunk:
                    print(chunk.decode("utf-8"), end="", flush=True)
        else:
            print(f"请求失败，状态码: {response.status_code}")


if __name__ == "__main__":
    stream_client()