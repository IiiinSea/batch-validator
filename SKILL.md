---
name: batch-validator
description: Excel vs PPT批量信息校验系统。自动提取PPT文字和截图，对比Excel数据，校验平台、标题、时间、账号、粉丝数、阅读量、见刊位置等7项内容。支持3级数据提取（PPT文字→截图→网页），生成格式化校验结果Excel。适用于媒体发稿核对、信息一致性检查、批量数据验证等场景。
author: 用户自定义
version: 1.0.0
homepage: ""
triggers:
  - "校验Excel"
  - "验证PPT"
  - "对比Excel和PPT"
  - "批量校验"
  - "批量检查"
  - "信息核对"
  - "Excel PPT校验"
metadata: {"clawdbot":{"emoji":"✅","requires":{"bins":["python3"]}}}
---

# ✅ Batch Validator - Excel vs PPT 批量校验系统

自动化校验Excel信息列表与PPT截图的一致性，支持智能数据提取和格式化输出。

## 核心功能

- 🎯 **智能触发**：识别「校验Excel」「验证PPT」等关键词，自动引导完整流程
- 📄 **文字提取**：自动从PPT文字标注提取平台、标题、日期、位置等信息
- 🖼️ **截图识别**：使用Claude视觉能力从PPT截图提取粉丝数、阅读量
- 🌐 **网页补充**：自动从见刊链接抓取缺失的统计数据
- ✅ **7项校验**：平台、标题、时间、账号、粉丝数、阅读量、位置全面对比
- 🎨 **格式化输出**：颜色编码（绿/红/黄），详细失败原因，列宽优化
- 💾 **自动保存**：结果保存到原Excel同目录，命名规则：`原文件名-校验结果.xlsx`
- 🔄 **3级优先级**：粉丝数/阅读量按 PPT文字→截图→网页 逐级提取

## 快速使用

### 基础校验（推荐）

```bash
uv run scripts/validate.py <ppt文件> <excel文件>
```

**自动完成：**
1. 提取PPT文字标注
2. 解析平台、标题、日期、位置、账号
3. 与Excel逐行对比校验
4. 尝试从网页获取粉丝数/阅读量
5. 生成 `原文件名-校验结果.xlsx`

### 完整校验（含截图数据）

**Step 1：生成截图任务**
```bash
uv run scripts/create_screenshot_tasks.py <slides目录> <ppt_text.json> screenshot_stats.json
```

**Step 2：Claude提取截图数据**
- 打开 `screenshot_stats.json`
- 对每个slide，用Claude读取图片并提取粉丝数/阅读量
- 更新JSON文件

**Step 3：运行完整校验**
```bash
uv run scripts/validate.py <ppt文件> <excel文件> screenshot_stats.json
```

## 校验规则

| 序号 | 校验项 | 规则 | 数据来源 |
|------|--------|------|----------|
| 1 | 发布平台 | 完全匹配 | PPT文字 |
| 2 | 文章标题 | 完全匹配 | PPT文字 |
| 3 | 发布时间 | 日期一致（支持多种格式） | PPT文字 |
| 4 | 发布账号 | 账号匹配 | PPT文字 |
| 5 | 粉丝数量 | PPT ≥ Excel | **3级提取** |
| 6 | 阅读量 | PPT ≥ Excel | **3级提取** |
| 7 | 见刊位置 | 完全匹配 | PPT文字 |

**3级数据提取（粉丝数/阅读量）：**
```
优先级1: PPT文字标注（自动）
    ↓ 未找到
优先级2: PPT截图识别（Claude视觉）
    ↓ 未找到
优先级3: 见刊链接网页（自动抓取）
    ↓ 未找到
结果: N/A
```

## 输出格式

生成的Excel包含：
- ✅ 原始所有列（保持不变）
- ✅ 新增7列校验结果

校验结果格式：
- 🟢 `是` - 校验通过（绿色背景）
- 🔴 `否：详细原因` - 校验失败（红色背景，含具体差异）
- 🟡 `N/A：说明` - 无法获取数据（黄色背景）
- 🟡 `信息：说明` - 提示信息（黄色背景）

示例：
```
校验1-发布平台: 是
校验2-文章标题: 否：标题不匹配
  Excel: 2024广州车展：比亚迪夏内饰科技全球首发
  PPT: 华夏之光：比亚迪中大型旗舰MPV夏内饰科技全球首发
校验5-粉丝数量: 是（来源:截图）
校验6-阅读量: N/A：PPT文字、截图和网页均未找到阅读量
```

## 依赖安装

**基础依赖（必需）：**
```bash
cd batch-validator
uv sync
```

**Vision API（可选，用于截图识别）：**
```bash
# 选择一个或多个大模型平台
uv sync --extra claude     # Anthropic Claude（推荐）
uv sync --extra openai     # OpenAI GPT-4V
uv sync --extra gemini     # Google Gemini
uv sync --extra all        # 安装所有Vision API

# 配置API密钥
cp .env.example .env
# 编辑.env文件，填入API密钥
```

**支持的大模型平台：**
- ✅ **Claude** (Anthropic) - 推荐，准确率高
- ✅ **GPT-4V** (OpenAI) - 通用性强
- ✅ **Gemini** (Google) - 免费额度大

系统会自动检测可用的API密钥并选择合适的后端。

## 目录结构

```
batch-validator/
├── .clawhook                    # OpenClaw触发钩子
├── SKILL.md                     # 技能说明（本文件）
├── WORKFLOW.md                  # 详细工作流程
├── README.md                    # 使用文档
├── pyproject.toml              # uv依赖配置
├── scripts/                    # 快捷脚本
│   ├── validate.py            # 主校验脚本
│   ├── extract_ppt.py         # PPT文字提取
│   └── create_screenshot_tasks.py  # 截图任务生成
└── batch-validator/           # 核心源代码
    ├── extractors/            # 数据提取模块
    ├── validators/            # 校验逻辑模块
    ├── formatters/            # Excel格式化模块
    └── utils/                 # 工具函数
```

## 使用场景

- 📰 **媒体发稿核对**：验证新闻稿发布信息与实际见刊情况
- 📊 **报告数据验证**：核对PPT报告数据与Excel原始记录
- 🎯 **批量信息检查**：大规模信息一致性校验
- 📝 **质量控制**：确保文档间数据准确性

## 常见问题

1. **PPT中没有文字标注怎么办？**
   - 系统会尝试从截图提取，需要Claude视觉识别

2. **粉丝数和阅读量总是N/A？**
   - 提供 `screenshot_stats.json` 文件，手动补充截图数据
   - 或检查见刊链接是否可访问

3. **日期格式不匹配？**
   - 系统已支持多种格式：`2024-11-15` / `2024.11.15` / `2024/11/15`

4. **生成的文件在哪里？**
   - 自动保存到Excel文件所在目录
   - 文件名：`原文件名-校验结果.xlsx`
