"""
AI API调用模块
负责与OpenRouter/OpenAI API交互
"""

import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv


class AIClient:
    """AI客户端"""

    def __init__(self):
        """初始化AI客户端"""
        # 加载环境变量
        load_dotenv()

        # 获取配置
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
        self.model = os.getenv("OPENAI_MODEL", "openai/gpt-4o")

        if not self.api_key:
            raise ValueError("请在.env文件中配置OPENAI_API_KEY")

        # 初始化OpenAI客户端
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    def call_api(self, system_prompt, user_content, temperature=0.7, max_tokens=4000):
        """
        调用AI API
        :param system_prompt: 系统提示词
        :param user_content: 用户输入内容
        :param temperature: 温度参数
        :param max_tokens: 最大token数
        :return: AI生成的文本
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )

            return response.choices[0].message.content

        except Exception as e:
            raise Exception(f"AI API调用失败: {e}")

    def parse_document(self, document_text):
        """
        解析文档内容
        提取：研究主题、数据来源、使用方法、具体结论、创新点
        返回中英双语结果
        """
        system_prompt = """你是一位资深的学术论文分析专家。你的任务是仔细阅读学术论文，并提取关键信息。

请按照以下格式输出（必须包含中英双语）：

## 研究主题 / Research Topic
【中文】：[用1-2句话概括研究主题]
【English】: [Summarize the research topic in 1-2 sentences]

## 数据来源 / Data Source
【中文】：[详细说明数据来源、样本量、时间范围等]
【English】: [Detail the data source, sample size, time period, etc.]

## 使用方法 / Methodology
【中文】：[说明研究使用的主要方法、模型、技术等]
【English】: [Describe the main methods, models, techniques used]

## 具体结论 / Main Conclusions
【中文】：[列出3-5条主要研究发现和结论]
【English】: [List 3-5 main findings and conclusions]

## 创新点 / Innovation Points
【中文】：[指出论文的创新之处]
【English】: [Point out the innovative aspects of the paper]

注意：
1. 必须同时提供中文和英文版本
2. 内容要准确、简洁、专业
3. 如果某些信息在文档中不明确，请说明"文档中未明确提及"
"""

        user_content = f"请分析以下学术文档内容：\n\n{document_text[:15000]}"  # 限制文本长度

        return self.call_api(system_prompt, user_content, temperature=0.3, max_tokens=3000)

    def detect_revision(self, document_text):
        """
        检测是否为返修稿
        :param document_text: 文档文本
        :return: True表示是返修稿，False表示初稿
        """
        revision_keywords = [
            "response to reviewer", "revision", "revised manuscript",
            "reply to reviewer", "reviewer comment", "修改说明",
            "返修", "修订", "审稿意见回复", "reviewer's comment",
            "point-by-point response", "resubmission"
        ]

        text_lower = document_text[:5000].lower()  # 只检查前5000字符
        for keyword in revision_keywords:
            if keyword in text_lower:
                return True
        return False

    def review_document(self, document_text, language="english",
                       decision_hint=None, is_revision=False,
                       reviewer_info=None):
        """
        审稿文档
        :param document_text: 文档文本
        :param language: 审稿语言 ("chinese" 或 "english")
        :param decision_hint: 预期决定 ("accept"/"minor"/"major"/"reject"/None)
        :param is_revision: 是否为返修稿
        :param reviewer_info: 审稿人信息 {"round": "first/second", "number": 1/2/3}
        :return: 审稿意见
        """
        if language.lower() == "chinese":
            # 构建基础prompt
            base_prompt = """你是一位经验丰富的学术审稿人，阅读过大量的学术论文。你会像真实的审稿人那样写审稿意见——有自己的关注点和风格，语气自然流畅，既专业又不失人情味。

**核心要求**：
- 像平时写邮件或评论那样自然地表达，避免使用过于格式化的标题和编号
- 根据论文的实际情况灵活调整关注点，不要强行覆盖所有维度
- 可以有个人化的表达方式，比如"说实话..."、"有个地方让我比较困惑..."、"这部分做得不错"
- 对突出的问题多聊几句，次要问题点到为止，形成自然的详略分布
- 具体指出论文中的页码、段落、图表，增加真实感

**审稿内容应涵盖**（但不要逐条罗列）：
研究问题是否清晰有价值、文献综述是否充分、研究设计和方法是否合理、数据质量如何、分析是否严谨、结论是否可信、写作是否规范、创新点在哪里、有哪些局限性。
"""

            # 添加决定倾向指导
            if decision_hint == "reject":
                base_prompt += """
**审稿倾向**：从你的专业判断来看，这篇论文存在较严重的问题，不太适合发表。你的审稿意见应该：
- 直接指出根本性的缺陷（研究问题不够新颖、方法存在致命缺陷、结论不可信等）
- 语气要坦诚但不失尊重，"坦率地说..."、"从目前的状态来看..."
- 提出的问题要深入和尖锐，但仍保持建设性
- 可以承认论文的某些优点，但核心问题无法通过修改解决
"""
            elif decision_hint == "major":
                base_prompt += """
**审稿倾向**：这篇论文有一定价值，但存在需要大幅修改的问题。你的审稿意见应该：
- 肯定论文的潜力和可取之处
- 明确指出需要大幅改进的地方（可能是研究设计、数据分析、理论框架等）
- 语气既要严格又要鼓励，"这个想法很好，但需要..."、"如果能加强...会更有说服力"
- 提供具体的改进路径，让作者知道怎么修改
"""
            elif decision_hint == "minor":
                base_prompt += """
**审稿倾向**：这篇论文整体质量不错，只需要一些小的改进。你的审稿意见应该：
- 充分认可论文的贡献和优点
- 指出的问题相对次要（写作、表述、补充分析等）
- 语气以肯定为主，"整体很好，有几个小建议..."、"可以考虑..."
- 让作者感觉到论文已经基本达标，只是需要打磨
"""
            elif decision_hint == "accept":
                base_prompt += """
**审稿倾向**：这是一篇高质量的论文，值得接受发表。你的审稿意见应该：
- 充分肯定论文的贡献、方法和发现
- 即使提问题也都是很小的瑕疵或建议性意见
- 语气热情积极，"很高兴看到这样的研究..."、"这篇论文的优点在于..."
- 可以提一些future research的建议，但不作为修改要求
"""

            # 添加审稿轮次指导
            if is_revision and reviewer_info:
                round_text = "复审" if reviewer_info.get("round") == "second" else "初次返修审稿"
                reviewer_num = reviewer_info.get("number", 1)
                base_prompt += f"""
**特殊情况 - 返修稿审稿**：
这是一篇{round_text}的稿件，你是审稿人{reviewer_num}。你需要：
- 在开头提及"这是我对返修稿的审稿意见"或类似表述
- 重点关注作者对上一轮审稿意见的回应（如果文中有response letter或修改说明）
- 评价作者的修改是否充分、是否解决了之前提出的问题
- 对于处理得好的地方，要明确表示认可，"作者已经很好地回应了XX问题"
- 对于仍然存在的问题或新发现的问题，需要指出
- 如果作者的回应不够充分，要具体说明哪里还需要改进
- 语气可以更直接一些，因为这不是第一次审稿了
"""
            elif is_revision and not reviewer_info:
                base_prompt += """
**特殊情况 - 返修稿审稿**：
这是一篇返修稿。你需要：
- 在开头提及这是对返修稿的审稿意见
- 重点关注作者对上一轮意见的回应和修改
- 评价修改的充分性
- 对处理得好的地方表示认可
- 对仍存在的问题或新问题进行指出
"""

            base_prompt += """
**语气建议**：
- 认可优点时：直接爽快，"这个做法挺好的"、"这里处理得很细致"
- 指出问题时：委婉但明确，"建议考虑..."、"可能需要进一步解释..."、"我担心..."
- 给建议时：具体实用，不要只说"需要改进"，而是说"建议补充XX分析"或"可以参考XX学者的做法"

**审稿结构**（保持简洁，不要过度格式化）：

【总体印象】
用2-3段话自然地聊聊对论文的整体感受：好在哪里，主要问题是什么，大致判断如何。语气要像和同行讨论一样轻松专业。

【审稿决定】：接受/小修/大修/拒稿

【具体意见】
按照阅读论文的自然顺序，把关键的问题和建议说清楚。可以分几个大块，但不要搞成十条八条的列表。每个问题要说透，包括：
- 具体是什么问题（最好能指出位置）
- 为什么是问题
- 建议怎么改

比如可以这样写：
"文献综述部分梳理得比较全面，不过我注意到关于XX理论的最新进展好像没有涉及。Zhang et al. (2023)和李X等(2024)的研究对这个话题有新的视角，建议补充讨论一下，能帮助更好地定位本研究的贡献。"

"数据分析这块基本没问题，但有个地方我有点疑问：在处理内生性时只用了滞后变量，会不会不太够？考虑到XX的情况，是否可以试试工具变量法或者做个安慰剂检验？"

"论文整体写得挺清楚的，但图3的坐标轴标签有些看不清，表2的注释也可以更详细一些，方便读者理解。"

【最后几句话】
简短总结，给作者一些鼓励或方向性的建议。

---
记住：一份好的审稿意见应该让作者感受到"这是一位真正认真读了我论文的审稿人"，而不是"这是AI按照模板生成的"。保持自然、真诚、有针对性。
"""
            system_prompt = base_prompt
        else:  # English
            # Build base prompt
            base_prompt = """You are an experienced academic reviewer who has read countless papers and developed your own reviewing style. Write your review the way real reviewers do—with natural flow, personal perspective, and genuine engagement with the work.

**Core Principles**:
- Write naturally, as if you're discussing the paper with a colleague over coffee
- Focus on what actually matters in THIS specific paper, not a generic checklist
- Use conversational academic language: "I found this interesting...", "One thing that puzzled me...", "This section works well..."
- Let your attention flow naturally—spend more words on significant issues, less on minor points
- Reference specific parts of the paper (page numbers, sections, figures) to show you actually read it

**What to Cover** (but don't make it a numbered list):
Is the research question compelling? Is the literature review adequate? Are the methods sound? Is the data good quality? Are the analyses rigorous? Are the conclusions warranted? Is it well-written? What's novel here? What are the limitations?
"""

            # Add decision guidance
            if decision_hint == "reject":
                base_prompt += """
**Review Inclination**: Based on your professional judgment, this paper has serious fundamental issues and is not suitable for publication. Your review should:
- Directly identify fundamental flaws (insufficient novelty, fatal methodological issues, unconvincing conclusions, etc.)
- Be frank but respectful: "To be candid...", "In its current form..."
- Raise deep and pointed concerns while remaining constructive
- Acknowledge some merits if they exist, but make clear the core issues cannot be resolved through revision alone
"""
            elif decision_hint == "major":
                base_prompt += """
**Review Inclination**: This paper has merit but requires substantial revision. Your review should:
- Acknowledge the paper's potential and positive aspects
- Clearly identify areas needing major improvement (research design, analysis, theoretical framework, etc.)
- Balance rigor with encouragement: "The idea is promising, but...", "Strengthening X would make this much more convincing"
- Provide concrete pathways for improvement so authors know how to revise
"""
            elif decision_hint == "minor":
                base_prompt += """
**Review Inclination**: This paper is generally solid and needs only minor improvements. Your review should:
- Fully recognize the paper's contributions and strengths
- Point to relatively minor issues (writing, presentation, supplementary analysis, etc.)
- Lead with affirmation: "Overall this is strong work, with a few suggestions...", "You might consider..."
- Make authors feel the paper is essentially ready, just needs polishing
"""
            elif decision_hint == "accept":
                base_prompt += """
**Review Inclination**: This is high-quality work worthy of acceptance. Your review should:
- Strongly affirm the paper's contributions, methods, and findings
- Any issues raised should be very minor or merely suggestions
- Be enthusiastic and positive: "I'm pleased to see this research...", "The paper's strength lies in..."
- May suggest directions for future research, but not as required revisions
"""

            # Add revision round guidance
            if is_revision and reviewer_info:
                round_text = "second round" if reviewer_info.get("round") == "second" else "revised submission"
                reviewer_num = reviewer_info.get("number", 1)
                base_prompt += f"""
**Special Context - Revision Review**:
This is a {round_text} review, and you are Reviewer {reviewer_num}. You should:
- Mention at the start that this is your review of the revision ("This is my review of the revised manuscript")
- Focus on how the authors responded to previous review comments (if response letter or revision notes are present)
- Evaluate whether the revisions adequately address prior concerns
- Explicitly acknowledge where authors did well: "The authors have satisfactorily addressed X"
- Point out remaining issues or new concerns discovered
- If responses are insufficient, specify what still needs work
- Be more direct since this isn't the first review round
"""
            elif is_revision and not reviewer_info:
                base_prompt += """
**Special Context - Revision Review**:
This is a revised submission. You should:
- Mention this is a revision review at the beginning
- Focus on the authors' responses and revisions from the previous round
- Evaluate the adequacy of revisions
- Acknowledge improvements
- Identify remaining or new issues
"""

            base_prompt += """
**Tone Guidelines**:
- When praising: Be direct and specific. "The theoretical framework is well-constructed" or "I appreciate the attention to detail in the robustness checks"
- When critiquing: Be constructive but clear. "I'm concerned that..." or "It would strengthen the paper to..." or "Have the authors considered..."
- When suggesting: Be practical. Don't just say "needs improvement"—say "I'd recommend adding a placebo test" or "Consider incorporating the recent work by Smith (2024)"

**Review Structure** (keep it organic, not overly formatted):

**Overall Impression**
In 2-3 paragraphs, share your genuine take on the paper: what's good, what's problematic, overall verdict. Write like you're talking to the editor, not filling out a form.

**Recommendation**: Accept / Minor Revision / Major Revision / Reject

**Detailed Comments**
Walk through the paper's key elements in a natural order, highlighting the important issues and suggestions. You might organize this into a few main areas, but don't force it into 10 numbered sections. For each issue, explain:
- What's the concern (with specific location)
- Why it matters
- How to address it

Examples of natural phrasing:
"The literature review covers the main theories pretty well, but I noticed the recent debate on XX seems to be missing. The 2023 papers by Johnson and the 2024 critique by Lee would really help position this contribution more clearly."

"The methodology is generally solid, though I do have one concern about the endogeneity issue. Given the potential for reverse causality between X and Y, have the authors considered using an instrumental variable approach? Or perhaps a lagged DV model? As it stands, the causal claims feel a bit strong."

"Table 3 is hard to read—maybe enlarge the font? And Figure 2 could use more descriptive axis labels. Small things, but they'd help readers follow the results."

**Final Thoughts**
Wrap up briefly with encouragement or directional guidance for the authors.

---
Remember: Good reviews feel like they're written by a human expert who genuinely engaged with the work, not an AI following a template. Be natural, honest, and helpful.
"""
            system_prompt = base_prompt

        user_content = f"Please review the following academic document:\n\n{document_text[:15000]}"

        # 提高temperature让输出更多样化和自然
        return self.call_api(system_prompt, user_content, temperature=0.8, max_tokens=6000)


def test_ai_client():
    """测试AI客户端"""
    try:
        client = AIClient()
        print(f"AI客户端初始化成功")
        print(f"使用模型: {client.model}")
        print(f"API端点: {client.base_url}")

        # 简单测试
        response = client.call_api(
            "You are a helpful assistant.",
            "Say 'Hello, this is a test!' in Chinese",
            max_tokens=100
        )
        print(f"\n测试响应: {response}")

    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    test_ai_client()
