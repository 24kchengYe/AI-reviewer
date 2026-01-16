# AI学术论文审稿系统

一个基于AI的自动化学术论文审稿工具，支持PDF和Word文档的智能解析和专业审稿。

> 📖 **审稿质量升级**：现已升级为深度审稿版（v2.0），模拟资深审稿人风格，提供1500+字的详细专业意见。详见 [审稿系统说明](REVIEW_GUIDE.md)。

## 功能特点

- 📄 **多格式支持**: 支持PDF (.pdf)、Word (.docx, .doc)文档
- 🤖 **智能解析**: 自动提取研究主题、数据来源、方法、结论和创新点
- 📝 **专业审稿**: 模拟资深审稿人，生成深入详尽的审稿意见（10个维度，总字数1500+）
- 🌍 **双语支持**: 解析文件中英双语，审稿意见可选中文或英文
- 📁 **自动管理**: 自动创建review文件夹，规范化文档组织
- 🔌 **灵活配置**: 支持OpenRouter平台，可配置不同AI模型

## 项目结构

```
047AI审稿系统/
├── main.py                 # 主程序入口
├── document_parser.py      # 文档解析模块
├── folder_manager.py       # 文件夹管理模块
├── ai_client.py           # AI API调用模块
├── requirements.txt        # 依赖包列表
├── .env                   # 环境变量配置（需自行创建）
├── .env.example           # 环境变量配置示例
├── material/              # 待审稿文档目录
│   └── review1/           # 已处理文档存放处（自动创建）
└── response/              # 审稿结果目录
    └── review1/           # 审稿结果文件（自动创建）
        ├── review1_解析文件.txt
        └── review1_审稿文件.txt
```

## 安装步骤

### 1. 环境要求

- Python 3.8 或更高版本
- pip 包管理器

### 2. 安装依赖

```bash
# 激活虚拟环境（如果使用）
# Windows:
AIreviewer\Scripts\activate
# Linux/Mac:
source AIreviewer/bin/activate

# 安装依赖包
pip install -r requirements.txt
```

### 3. 配置API密钥

1. 复制`.env.example`为`.env`：
```bash
cp .env.example .env
```

2. 编辑`.env`文件，填入你的API密钥：
```env
# API密钥（必填）- 从OpenRouter或OpenAI获取
OPENAI_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxx

# API端点URL
OPENAI_BASE_URL=https://openrouter.ai/api/v1

# 模型名称
OPENAI_MODEL=openai/gpt-4o
```

**获取API密钥：**
- OpenRouter: https://openrouter.ai/
- 注册后在个人设置中获取API密钥

## 使用方法

### 基本流程

1. **准备文档**
   - 将待审稿的PDF或Word文档放入`material/`文件夹

2. **运行程序**
   ```bash
   python main.py
   ```

3. **选择审稿语言**
   - 程序启动后，选择中文审稿(1)或英文审稿(2)

4. **等待处理**
   - 程序会自动：
     - 创建`review1`（或更高编号）文件夹
     - 解析文档内容
     - 生成解析文件（中英双语）
     - 生成审稿意见（中文或英文）
     - 将原文档移动到`material/review1/`
     - 将结果保存到`response/review1/`

### 输出文件

每次运行会在`response/review*/`文件夹中生成：

1. **解析文件** (`review*_解析文件.txt`)
   - 包含中英双语的研究信息：
     - 研究主题 / Research Topic
     - 数据来源 / Data Source
     - 使用方法 / Methodology
     - 具体结论 / Main Conclusions
     - 创新点 / Innovation Points

2. **审稿文件** (`review*_审稿文件.txt`)
   - 模拟15年以上经验的资深审稿人
   - 10个维度的深入评价（研究问题、文献综述、方法论、数据质量、分析过程、稳健性、结果阐释、局限性、写作质量、创新性）
   - 每个维度100-150字，总字数不少于1500字
   - 使用第一人称，体现专业判断，避免模板化表述
   - 包含详细的总体评价和审稿建议（接受/小修后接受/大修后再审/拒稿）

### 示例操作

```bash
# 1. 将论文放入material文件夹
cp /path/to/paper.pdf material/

# 2. 运行程序
python main.py

# 3. 按提示选择语言
请选择审稿语言 / Please select review language:
1. 中文审稿 (Chinese Review)
2. 英文审稿 (English Review)
请输入选项 (1/2): 1

# 4. 确认处理
准备开始处理 1 个文档
是否继续？(y/n): y

# 5. 等待完成
[1/4] 正在解析文档...
[2/4] 正在进行AI解析（提取研究信息）...
[3/4] 正在生成chinese审稿意见...
[4/4] 正在整理文件...
✓ paper.pdf 处理完成！
```

## 高级配置

### 更换AI模型

编辑`.env`文件中的`OPENAI_MODEL`参数：

```env
# 使用GPT-4o（推荐，质量高）
OPENAI_MODEL=openai/gpt-4o

# 使用Claude 3.5 Sonnet（推荐，审稿专业）
OPENAI_MODEL=anthropic/claude-3.5-sonnet

# 使用GPT-4 Turbo（平衡性能和成本）
OPENAI_MODEL=openai/gpt-4-turbo

# 使用GPT-3.5 Turbo（快速且经济）
OPENAI_MODEL=openai/gpt-3.5-turbo
```

### 批量处理

程序会自动处理`material/`文件夹中的所有未处理文档，并将它们放入同一个`review*`文件夹中。

## 常见问题

### Q1: 提示"API密钥未配置"

**解决方案**: 确保`.env`文件存在且正确填写了`OPENAI_API_KEY`。

### Q2: PDF解析失败

**解决方案**: 某些加密或扫描版PDF可能无法解析。建议使用可复制文本的PDF文件。

### Q3: API调用超时

**解决方案**:
- 检查网络连接
- 尝试更换API端点
- 确认API密钥有效且有足够余额

### Q4: review文件夹编号错乱

**解决方案**: 程序会自动检测现有的review文件夹并使用下一个编号。如需重置，可以删除existing的review文件夹。

## 依赖包说明

- `python-dotenv`: 环境变量管理
- `openai`: OpenAI API客户端（兼容OpenRouter）
- `PyPDF2`: PDF解析（备用方案）
- `pdfplumber`: PDF文本提取（主要方案）
- `python-docx`: Word文档解析

## 注意事项

1. 确保API密钥安全，不要提交到版本控制系统
2. 处理大文件时可能需要较长时间，请耐心等待
3. API调用会产生费用，请关注账户余额
4. 建议先用小文档测试，确认配置正确后再批量处理

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交Issue。

---

**版本**: v1.0
**更新日期**: 2026-01-16
