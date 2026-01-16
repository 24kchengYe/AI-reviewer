"""
AI审稿系统 - 主程序
自动处理学术文档并生成审稿意见
"""

import sys
from pathlib import Path
from document_parser import DocumentParser
from folder_manager import FolderManager
from ai_client import AIClient


class ReviewSystem:
    """审稿系统主类"""

    def __init__(self):
        """初始化审稿系统"""
        self.folder_manager = FolderManager()
        self.ai_client = AIClient()
        self.review_language = None

    def display_banner(self):
        """显示程序标题"""
        banner = """
╔═══════════════════════════════════════════════╗
║        AI学术论文审稿系统 v1.0                ║
║        Academic Paper Review System           ║
╚═══════════════════════════════════════════════╝
"""
        print(banner)

    def select_language(self):
        """选择审稿语言"""
        print("\n请选择审稿语言 / Please select review language:")
        print("1. 中文审稿 (Chinese Review)")
        print("2. 英文审稿 (English Review)")

        while True:
            choice = input("\n请输入选项 (1/2): ").strip()

            if choice == "1":
                self.review_language = "chinese"
                print("✓ 已选择中文审稿")
                return True
            elif choice == "2":
                self.review_language = "english"
                print("✓ Selected English Review")
                return True
            else:
                print("❌ 无效选项，请输入1或2")

    def check_materials(self):
        """检查待处理的材料"""
        unprocessed_files = self.folder_manager.get_unprocessed_files()

        if not unprocessed_files:
            print("\n❌ 在material文件夹中没有找到待处理的文档")
            print("   支持的格式: PDF (.pdf), Word (.docx, .doc)")
            return []

        print(f"\n✓ 找到 {len(unprocessed_files)} 个待处理文档:")
        for i, file in enumerate(unprocessed_files, 1):
            size_mb = file.stat().st_size / (1024 * 1024)
            print(f"   {i}. {file.name} ({size_mb:.2f} MB)")

        return unprocessed_files

    def process_document(self, file_path, review_number, material_review_path, response_review_path):
        """
        处理单个文档
        :param file_path: 文档路径
        :param review_number: review编号
        :param material_review_path: material中的review文件夹路径
        :param response_review_path: response中的review文件夹路径
        """
        file_name = file_path.name
        print(f"\n{'='*60}")
        print(f"正在处理: {file_name}")
        print(f"{'='*60}")

        # 1. 解析文档
        print("\n[1/4] 正在解析文档...")
        try:
            document_text = DocumentParser.parse(file_path)
            print(f"✓ 文档解析成功，提取文本长度: {len(document_text)} 字符")
        except Exception as e:
            print(f"❌ 文档解析失败: {e}")
            return False

        # 2. AI解析：提取关键信息（中英双语）
        print("\n[2/4] 正在进行AI解析（提取研究信息）...")
        try:
            parse_result = self.ai_client.parse_document(document_text)
            print("✓ AI解析完成")

            # 保存解析文件
            parse_file_name = f"review{review_number}_解析文件.txt"
            self.folder_manager.save_response(parse_result, parse_file_name, response_review_path)
            print(f"✓ 解析文件已保存: {parse_file_name}")

        except Exception as e:
            print(f"❌ AI解析失败: {e}")
            return False

        # 3. AI审稿：生成审稿意见
        print(f"\n[3/4] 正在生成{self.review_language}审稿意见...")
        try:
            review_result = self.ai_client.review_document(document_text, self.review_language)
            print("✓ 审稿意见生成完成")

            # 保存审稿文件
            review_file_name = f"review{review_number}_审稿文件.txt"
            self.folder_manager.save_response(review_result, review_file_name, response_review_path)
            print(f"✓ 审稿文件已保存: {review_file_name}")

        except Exception as e:
            print(f"❌ 审稿失败: {e}")
            return False

        # 4. 移动文档到review文件夹
        print("\n[4/4] 正在整理文件...")
        try:
            dest_path = self.folder_manager.move_file_to_review(file_path, material_review_path)
            print(f"✓ 文档已移动到: {dest_path.parent.name}/{dest_path.name}")
        except Exception as e:
            print(f"❌ 文件移动失败: {e}")
            return False

        print(f"\n✓ {file_name} 处理完成！")
        return True

    def run(self):
        """运行审稿系统"""
        # 显示标题
        self.display_banner()

        # 选择语言
        if not self.select_language():
            return

        # 检查待处理材料
        unprocessed_files = self.check_materials()
        if not unprocessed_files:
            return

        # 确认开始处理
        print(f"\n准备开始处理 {len(unprocessed_files)} 个文档")
        confirm = input("是否继续？(y/n): ").strip().lower()
        if confirm != 'y':
            print("已取消操作")
            return

        # 获取review编号并创建文件夹
        review_number = self.folder_manager.get_next_review_number()
        material_review_path, response_review_path = self.folder_manager.create_review_folders(review_number)

        print(f"\n已创建 review{review_number} 文件夹")

        # 处理每个文档
        success_count = 0
        fail_count = 0

        for file_path in unprocessed_files:
            success = self.process_document(
                file_path,
                review_number,
                material_review_path,
                response_review_path
            )

            if success:
                success_count += 1
            else:
                fail_count += 1

        # 显示统计信息
        print(f"\n{'='*60}")
        print("处理完成！")
        print(f"{'='*60}")
        print(f"成功: {success_count} 个")
        print(f"失败: {fail_count} 个")
        print(f"\n结果保存在:")
        print(f"  - 原文档: material/review{review_number}/")
        print(f"  - 审稿结果: response/review{review_number}/")


def main():
    """主函数"""
    try:
        system = ReviewSystem()
        system.run()
    except KeyboardInterrupt:
        print("\n\n程序已被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 程序运行出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
