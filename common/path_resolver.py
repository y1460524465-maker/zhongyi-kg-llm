import os

def get_project_root() -> str:
    """获取项目根目录的绝对路径"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def resolve_path(relative_path: str, root_dir: str = None) -> str:
    """
    将相对路径解析为绝对路径
    
    Args:
        relative_path: 相对于项目根目录的路径
        root_dir: 项目根目录的绝对路径，默认为当前脚本所在目录
    
    Returns:
        拼接后的绝对路径
    """
    if root_dir is None:
        root_dir = get_project_root()
    
    abs_path = os.path.normpath(os.path.join(root_dir, relative_path))
    return abs_path

if __name__ == '__main__':
    # 示例用法
    project_root = get_project_root()
    print(f"项目根目录: {project_root}")
    
    # 测试路径拼接
    test_path = resolve_path("common/path_utils.py")
    print(f"解析后的路径: {test_path}")
    
    # 验证路径是否存在
    if os.path.exists(test_path):
        print("路径存在")
    else:
        print("路径不存在")
