# 🔧 Vision API 配置指南

## 为什么需要配置Vision API？

Skill的**粉丝数**和**阅读量**提取依赖大模型的视觉识别能力。为了支持跨平台使用，我们设计了抽象的Vision API层，支持多个主流大模型平台。

---

## 🎯 支持的平台

| 平台 | API提供商 | 优势 | 安装 |
|------|----------|------|------|
| **Claude** | Anthropic | 中文识别准确率最高 | `uv sync --extra claude` |
| **GPT-4V** | OpenAI | 生态丰富，通用性强 | `uv sync --extra openai` |
| **Gemini** | Google | 免费额度大，速度快 | `uv sync --extra gemini` |

---

## 📦 安装步骤

### 方案1：只安装一个（推荐）

根据你拥有的API密钥选择：

```bash
# 如果有Anthropic账号
uv sync --extra claude

# 如果有OpenAI账号
uv sync --extra openai

# 如果有Google账号
uv sync --extra gemini
```

### 方案2：安装全部（最大兼容性）

```bash
uv sync --extra all
```

系统会自动检测可用的API密钥并选择使用。

---

## 🔑 获取API密钥

### Anthropic Claude

1. 访问：https://console.anthropic.com/
2. 注册/登录账号
3. 进入 API Keys 页面
4. 创建新的API密钥
5. 复制密钥（格式：`sk-ant-xxxxx`）

**价格**：$3 / 1M input tokens，$15 / 1M output tokens

### OpenAI GPT-4V

1. 访问：https://platform.openai.com/
2. 注册/登录账号
3. 进入 API keys 页面
4. 创建新的API密钥
5. 复制密钥（格式：`sk-xxxxx`）

**价格**：GPT-4V 约 $0.01 / image

### Google Gemini

1. 访问：https://makersuite.google.com/app/apikey
2. 使用Google账号登录
3. 创建API密钥
4. 复制密钥

**价格**：每月前60次请求免费

---

## ⚙️ 配置API密钥

### 方式1：环境变量文件（推荐）

```bash
# 1. 复制配置模板
cp .env.example .env

# 2. 编辑.env文件
nano .env  # 或用其他编辑器

# 3. 填入你的API密钥
ANTHROPIC_API_KEY=sk-ant-xxxxx
# OPENAI_API_KEY=sk-xxxxx
# GOOGLE_API_KEY=xxxxx
```

### 方式2：系统环境变量

```bash
# 临时设置（当前终端有效）
export ANTHROPIC_API_KEY="sk-ant-xxxxx"

# 永久设置（添加到~/.zshrc或~/.bashrc）
echo 'export ANTHROPIC_API_KEY="sk-ant-xxxxx"' >> ~/.zshrc
source ~/.zshrc
```

### 方式3：在脚本中直接传递

修改 `vision_api.py`，硬编码API密钥（不推荐）：
```python
api_key = "sk-ant-xxxxx"  # 直接写在代码里
```

---

## 🧪 测试Vision API

```bash
# 安装Vision API依赖
uv sync --extra claude

# 配置API密钥
export ANTHROPIC_API_KEY="your-key"

# 测试单张图片
uv run scripts/vision_api.py slides/slide_001.png
```

**预期输出：**
```json
{
  "followers": "1234",
  "views": "5678",
  "backend": "claude"
}
```

---

## 🔄 自动后端选择

如果配置了多个API密钥，系统会按以下优先级自动选择：

1. **Claude** (Anthropic) - 中文识别最准确
2. **GPT-4V** (OpenAI) - 作为备选
3. **Gemini** (Google) - 最后的备选

可以通过环境变量覆盖：
```bash
export PREFERRED_VISION_BACKEND=openai
```

---

## 💰 成本估算

假设校验10行数据，每行需要识别1张截图：

| 平台 | 成本/张 | 10张总成本 | 备注 |
|------|---------|-----------|------|
| Claude | ~$0.003 | **$0.03** | 最准确 |
| GPT-4V | ~$0.01 | **$0.10** | 中等 |
| Gemini | 免费 | **$0** | 前60次/月免费 |

**推荐策略**：
- 日常使用：Gemini（免费）
- 重要校验：Claude（最准确）
- 大批量：组合使用，节省成本

---

## ❓ 常见问题

**Q: 不配置Vision API可以使用吗？**
A: 可以！但粉丝数和阅读量会标记为N/A（除非从网页能抓到）。

**Q: 可以切换不同的大模型吗？**
A: 可以！配置多个API密钥，系统自动切换。或设置 `PREFERRED_VISION_BACKEND`。

**Q: API密钥安全吗？**
A: `.env` 文件已加入 `.gitignore`，不会泄露到Git仓库。

**Q: 识别准确率如何？**
A: Claude准确率最高（95%+），GPT-4V其次（90%+），Gemini约85%。

**Q: 可以不用Vision API吗？**
A: 可以手动创建 `screenshot_stats.json` 文件，人工填写数据。

---

## 🚀 快速上手

```bash
# 1. 安装依赖
uv sync --extra claude

# 2. 配置API密钥
echo 'ANTHROPIC_API_KEY=sk-ant-xxxxx' > .env

# 3. 运行校验（自动使用Vision API识别截图）
uv run scripts/validate.py test.pptx test.xlsx

# 完成！系统会自动：
# - 提取PPT文字 ✓
# - 调用Claude识别截图 ✓
# - 从网页补充数据 ✓
# - 生成格式化结果 ✓
```

---

## 🔗 相关链接

- Anthropic Console: https://console.anthropic.com/
- OpenAI Platform: https://platform.openai.com/
- Google AI Studio: https://makersuite.google.com/
