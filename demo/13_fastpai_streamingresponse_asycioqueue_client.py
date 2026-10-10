import json

import requests


def parse_chunk(chunk):
    #数据样式 {"type": "msg", "msg": msg}    {"type": "done", "msg": ""}
    json_str = chunk.decode("utf-8")
    chunk = json.loads(json_str)
    if chunk.get("type") == "msg":
        print(chunk.get("msg"), end="", flush=True)
        return False
    else:
        return True


def stream_client():
    url = "http://localhost:8000/stream"

    # 发送 POST 请求并设置 stream=True 以启用流式响应
    with requests.post(url, stream=True) as response:
        # 检查响应状态码
        if response.status_code == 200:
            # 逐行读取流式响应
            for chunk in response.iter_content(chunk_size=None):
                #{"type": "msg", "msg": msg}    {"type": "done", "msg": ""}
                if chunk:
                    # parse_chunk 返回值是true 表示已经读取完毕了
                    is_done = parse_chunk(chunk)
                    if is_done:
                        break
        else:
            print(f"请求失败，状态码: {response.status_code}")


if __name__ == "__main__":
    stream_client()