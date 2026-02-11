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

    def select_decision_hint(self):
        """选择审稿决定倾向"""
        if self.review_language == "chinese":
            print("\n请选择您倾向的审稿决定（可选，按回车跳过）:")
            print("1. 接受 (Accept) - 高质量论文")
            print("2. 小修 (Minor Revision) - 整体不错，需小改")
            print("3. 大修 (Major Revision) - 有潜力，需大改")
            print("4. 拒稿 (Reject) - 存在严重问题")
            print("0. 跳过（让AI自主判断）")
        else:
            print("\nPlease select your review decision inclination (optional, press Enter to skip):")
            print("1. Accept - High quality paper")
            print("2. Minor Revision - Good overall, needs minor changes")
            print("3. Major Revision - Has potential, needs major revision")
            print("4. Reject - Has serious issues")
            print("0. Skip (Let AI decide)")

        while True:
            choice = input("\n请输入选项 (0-4): ").strip()

            if choice == "0" or choice == "":
                print("✓ 将由AI自主判断审稿决定")
                return None
            elif choice == "1":
                print("✓ 已选择倾向：接受")
                return "accept"
            elif choice == "2":
                print("✓ 已选择倾向：小修")
                return "minor"
            elif choice == "3":
                print("✓ 已选择倾向：大修")
                return "major"
            elif choice == "4":
                print("✓ 已选择倾向：拒稿")
                return "reject"
            else:
                print("❌ 无效选项，请输入0-4")

    def select_reviewer_info(self, is_revision):
        """选择审稿人信息"""
        if not is_revision:
            return None

        if self.review_language == "chinese":
            print("\n这是返修稿，请设置审稿人信息:")
            print("您是第几轮审稿？")
            print("1. 初次返修（第一轮审稿后的返修）")
            print("2. 第二轮审稿（第二次返修）")
        else:
            print("\nThis is a revision. Please set reviewer info:")
            print("Which review round is this?")
            print("1. First revision (after initial review)")
            print("2. Second round (second revision)")

        while True:
            round_choice = input("\n请输入轮次 (1/2): ").strip()
            if round_choice in ["1", "2"]:
                break
            print("❌ 无效选项，请输入1或2")

        if self.review_language == "chinese":
            print("\n您是第几位审稿人？")
        else:
            print("\nWhat is your reviewer number?")

        while True:
            reviewer_num = input("请输入审稿人编号 (1/2/3/...): ").strip()
            if reviewer_num.isdigit() and int(reviewer_num) > 0:
                reviewer_num = int(reviewer_num)
                break
            print("❌ 请输入有效的数字")

        reviewer_info = {
            "round": "first" if round_choice == "1" else "second",
            "number": reviewer_num
        }

        if self.review_language == "chinese":
            round_text = "初次返修" if round_choice == "1" else "第二轮"
            print(f"✓ 已设置为{round_text}审稿，审稿人{reviewer_num}")
        else:
            round_text = "first revision" if round_choice == "1" else "second round"
            print(f"✓ Set as {round_text} review, Reviewer {reviewer_num}")

        return reviewer_info

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

    def process_document(self, file_path, review_number, material_review_path,
                        response_review_path, decision_hint=None, reviewer_info=None):
        """
        处理单个文档
        :param file_path: 文档路径
        :param review_number: review编号
        :param material_review_path: material中的review文件夹路径
        :param response_review_path: response中的review文件夹路径
        :param decision_hint: 审稿决定倾向
        :param reviewer_info: 审稿人信息
        """
        file_name = file_path.name
        print(f"\n{'='*60}")
        print(f"正在处理: {file_name}")
        print(f"{'='*60}")

        # 1. 解析文档
        print("\n[1/5] 正在解析文档...")
        try:
            document_text = DocumentParser.parse(file_path)
            print(f"✓ 文档解析成功，提取文本长度: {len(document_text)} 字符")
        except Exception as e:
            print(f"❌ 文档解析失败: {e}")
            return False

        # 1.5 检测是否为返修稿
        print("\n[2/5] 正在检测文档类型...")
        is_revision = self.ai_client.detect_revision(document_text)
        if is_revision:
            print("✓ 检测到这是一篇返修稿")
            # 如果是返修稿但没有设置审稿人信息，询问用户
            if reviewer_info is None:
                confirm = input("需要设置审稿人信息吗？(y/n，默认n): ").strip().lower()
                if confirm == 'y':
                    reviewer_info = self.select_reviewer_info(is_revision)
        else:
            print("✓ 这是一篇初次投稿的文档")

        # 2. AI解析：提取关键信息（中英双语）
        print("\n[3/5] 正在进行AI解析（提取研究信息）...")
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
        print(f"\n[4/5] 正在生成{self.review_language}审稿意见...")
        try:
            review_result = self.ai_client.review_document(
                document_text,
                self.review_language,
                decision_hint=decision_hint,
                is_revision=is_revision,
                reviewer_info=reviewer_info
            )
            print("✓ 审稿意见生成完成")

            # 保存审稿文件
            review_file_name = f"review{review_number}_审稿文件.txt"
            self.folder_manager.save_response(review_result, review_file_name, response_review_path)
            print(f"✓ 审稿文件已保存: {review_file_name}")

        except Exception as e:
            print(f"❌ 审稿失败: {e}")
            return False

        # 4. 移动文档到review文件夹
        print("\n[5/5] 正在整理文件...")
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

        # 选择审稿决定倾向
        decision_hint = self.select_decision_hint()

        # 检查待处理材料
        unprocessed_files = self.check_materials()
        if not unprocessed_files:
            return

        # 询问是否需要预设审稿人信息（针对返修稿）
        reviewer_info = None
        if self.review_language == "chinese":
            print("\n如果您知道这些文档是返修稿，可以提前设置审稿人信息")
            preset_reviewer = input("是否预设审稿人信息？(y/n，默认n): ").strip().lower()
        else:
            print("\nIf you know these documents are revisions, you can preset reviewer info")
            preset_reviewer = input("Preset reviewer info? (y/n, default n): ").strip().lower()

        if preset_reviewer == 'y':
            reviewer_info = self.select_reviewer_info(is_revision=True)

        # 确认开始处理
        print(f"\n准备开始处理 {len(unprocessed_files)} 个文档")
        confirm = input("是否继续？(y/n): ").strip().lower()
        if confirm != 'y':
            print("已取消操作")
            return

        # 处理每个文档
        success_count = 0
        fail_count = 0
        review_numbers = []  # 记录所有创建的review编号

        for file_path in unprocessed_files:
            # 为每个文档创建独立的review文件夹
            review_number = self.folder_manager.get_next_review_number()
            material_review_path, response_review_path = self.folder_manager.create_review_folders(review_number)
            review_numbers.append(review_number)

            print(f"\n为 {file_path.name} 创建 review{review_number} 文件夹")

            success = self.process_document(
                file_path,
                review_number,
                material_review_path,
                response_review_path,
                decision_hint=decision_hint,
                reviewer_info=reviewer_info
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
        for review_num in review_numbers:
            print(f"  - review{review_num}: material/review{review_num}/ 和 response/review{review_num}/")


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
