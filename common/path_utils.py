"""
通过 项目根目录的绝对路径和 相对于项目根目录的相对路径进行拼接,得到绝对路径
"""
import os

# 1.获取项目的根目录绝对路径
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# 2.将项目根目录绝对路径与项目内相对路径拼接，得到文件的绝对路径
def get_file_path(relative_path, root_dir=root_dir):
    return os.path.join(root_dir, relative_path)


if __name__ == '__main__':
    print(get_file_path("common/path_utils.py"))
