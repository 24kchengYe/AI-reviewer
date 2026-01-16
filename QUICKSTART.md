# 快速开始指南

## 5分钟快速配置

### 步骤1: 安装依赖（首次使用）

**Windows:**
```bash
# 激活虚拟环境
AIreviewer\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

**Linux/Mac:**
```bash
# 激活虚拟环境
source AIreviewer/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 步骤2: 配置API密钥

1. 打开 `.env` 文件
2. 在 `OPENAI_API_KEY=` 后面填入你的API密钥

```env
OPENAI_API_KEY=sk-or-v1-你的密钥
```

**如何获取API密钥？**
- 访问 https://openrouter.ai/
- 注册账号
- 在设置中获取API密钥

### 步骤3: 准备文档

将待审稿的PDF或Word文档放入 `material/` 文件夹

```
material/
  └── your_paper.pdf
```

### 步骤4: 运行程序

**Windows:**
- 双击 `run.bat`
- 或命令行运行: `python main.py`

**Linux/Mac:**
```bash
./run.sh
# 或
python main.py
```

### 步骤5: 选择语言并等待

1. 选择审稿语言（中文或英文）
2. 确认开始处理
3. 等待处理完成

## 查看结果

处理完成后，结果在以下位置：

```
material/review1/         ← 原文档
response/review1/         ← 审稿结果
  ├── review1_解析文件.txt   ← 研究信息（中英双语）
  └── review1_审稿文件.txt   ← 审稿意见
```

## 常见问题速查

### Q: 提示"API密钥未配置"？
确保 `.env` 文件中填写了 `OPENAI_API_KEY`

### Q: 提示"找不到文档"？
将PDF或Word文档放入 `material/` 文件夹

### Q: PDF解析失败？
确保PDF是文本版（可复制文字），而非纯图片扫描版

### Q: API调用失败？
- 检查网络连接
- 确认API密钥有效
- 检查账户余额

---

**更多详细信息请参考 README.md**
