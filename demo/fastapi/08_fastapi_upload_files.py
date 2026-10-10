from fastapi import FastAPI, UploadFile, File
from typing import List
import uvicorn
import os

app = FastAPI()

# 定义上传文件保存的目录
UPLOAD_DIR = "uploads"  # 你可以修改为任何你想要的目录名
# 确保上传目录存在
os.makedirs(UPLOAD_DIR, exist_ok=True)


# 文件上传
@app.post("/uploadfile/")
# file: UploadFile = File(...)  UploadFile 类表示要上传的是文件类型, File(...) 表示这个参数是必填的
async def create_upload_file(file: UploadFile = File(...)):
    try:
        print(f"文件名: {file.filename}")
        # 构建文件保存路径  uploads/文件名
        file_path = os.path.join(UPLOAD_DIR, file.filename)

        # 保存文件到指定目录 wb 表示是二进制写入
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        print(f"文件保存成功: {file_path}")
        return {
            "filename": file.filename,
            "saved_path": file_path,
            "message": "文件上传成功"
        }
    except Exception as e:
        return {
            "error": str(e),
            "message": "文件上传失败"
        }

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
