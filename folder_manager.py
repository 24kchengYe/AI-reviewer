"""
文件夹管理模块
负责创建review文件夹、复制文件、管理目录结构
"""

import os
import shutil
from pathlib import Path
from document_parser import DocumentParser


class FolderManager:
    """文件夹管理器"""

    def __init__(self, base_dir=None):
        """
        初始化文件夹管理器
        :param base_dir: 项目根目录，默认为当前目录
        """
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.material_dir = self.base_dir / "material"
        self.response_dir = self.base_dir / "response"

        # 确保基础文件夹存在
        self.material_dir.mkdir(exist_ok=True)
        self.response_dir.mkdir(exist_ok=True)

    def get_next_review_number(self):
        """
        获取下一个review文件夹编号
        检查material文件夹中已存在的review*文件夹
        """
        existing_reviews = []

        for item in self.material_dir.iterdir():
            if item.is_dir() and item.name.startswith("review"):
                try:
                    # 提取数字部分
                    num = int(item.name.replace("review", ""))
                    existing_reviews.append(num)
                except ValueError:
                    continue

        # 返回最大值+1，如果没有则返回1
        return max(existing_reviews, default=0) + 1

    def get_unprocessed_files(self):
        """
        获取material文件夹中未处理的文档
        排除已经在review*文件夹中的文件
        """
        # 获取所有已处理的文件名
        processed_files = set()
        for item in self.material_dir.iterdir():
            if item.is_dir() and item.name.startswith("review"):
                for file in item.iterdir():
                    if file.is_file():
                        processed_files.add(file.name)

        # 获取未处理的文件
        unprocessed_files = []
        for item in self.material_dir.iterdir():
            if item.is_file() and DocumentParser.is_supported(item):
                if item.name not in processed_files:
                    unprocessed_files.append(item)

        return unprocessed_files

    def create_review_folders(self, review_number):
        """
        创建review文件夹（在material和response中）
        :param review_number: review编号
        :return: (material_review_path, response_review_path)
        """
        review_name = f"review{review_number}"

        # 在material中创建review文件夹
        material_review_path = self.material_dir / review_name
        material_review_path.mkdir(exist_ok=True)

        # 在response中创建review文件夹
        response_review_path = self.response_dir / review_name
        response_review_path.mkdir(exist_ok=True)

        return material_review_path, response_review_path

    def move_file_to_review(self, file_path, review_folder):
        """
        将文件移动到review文件夹
        :param file_path: 源文件路径
        :param review_folder: 目标review文件夹路径
        """
        file_path = Path(file_path)
        dest_path = review_folder / file_path.name

        # 移动文件
        shutil.move(str(file_path), str(dest_path))
        return dest_path

    def save_response(self, content, file_name, review_folder):
        """
        保存审稿结果到response文件夹
        :param content: 文本内容
        :param file_name: 文件名
        :param review_folder: response中的review文件夹路径
        """
        file_path = review_folder / file_name
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path

    def process_new_review(self):
        """
        处理新的审稿任务
        返回: (review_number, files_to_process, material_review_path, response_review_path)
        """
        # 获取未处理的文件
        unprocessed_files = self.get_unprocessed_files()

        if not unprocessed_files:
            return None, [], None, None

        # 获取下一个review编号
        review_number = self.get_next_review_number()

        # 创建review文件夹
        material_review_path, response_review_path = self.create_review_folders(review_number)

        # 返回信息（暂不移动文件）
        return review_number, unprocessed_files, material_review_path, response_review_path


def test_folder_manager():
    """测试文件夹管理器"""
    fm = FolderManager()

    print(f"项目根目录: {fm.base_dir}")
    print(f"Material目录: {fm.material_dir}")
    print(f"Response目录: {fm.response_dir}")

    # 测试获取下一个review编号
    next_num = fm.get_next_review_number()
    print(f"\n下一个review编号: {next_num}")

    # 测试获取未处理文件
    unprocessed = fm.get_unprocessed_files()
    print(f"\n未处理的文件数量: {len(unprocessed)}")
    for file in unprocessed:
        print(f"  - {file.name}")


if __name__ == "__main__":
    test_folder_manager()
