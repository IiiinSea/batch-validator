---
name: batch-validator
description: Excel vs PPT批量信息校验系统。支持PPT信息提取（文字+图片）和智能查询（文字优先、Kimi K2.5图片兜底），以及Excel vs PPT一致性校验。适用于媒体发稿核对、信息一致性检查、批量数据验证等场景。
author: 用户自定义
version: 2.0.0
homepage: ""
triggers:
  - "校验Excel"
  - "验证PPT"
  - "对比Excel和PPT"
  - "批量校验"
  - "批量检查"
  - "信息核对"
  - "Excel PPT校验"
  - "提取信息"
  - "查询"
  - "查询信息"
metadata: {"clawdbot":{"emoji":"✅","requires":{"bins":["python3"]}}}
---

# ✅ Batch Validator - Excel vs PPT 批量校验系统

自动化校验Excel信息列表与PPT截图的一致性，支持智能数据提取和格式化输出。

## 核心功能

- 🎯 **智能触发**：识别「校验Excel」「查询信息」「提取信息」等关键词，自动引导完整流程
- 📄 **文字提取**：自动从PPT文字标注提取平台、标题、日期、位置等信息
- 🖼️ **图片提取**：从PPT每页抽取所有嵌入图片，按页分文件夹存储
- 🤖 **智能查询**：文字优先，找不到时自动用 Kimi K2.5 从图片中提取
- 🌐 **网页补充**：自动从见刊链接抓取缺失的统计数据
- ✅ **7项校验**：平台、标题、时间、账号、粉丝数、阅读量、位置全面对比
- 🎨 **格式化输出**：颜色编码（绿/红/黄），详细失败原因，列宽优化

---

## 工作流一：信息提取

**触发词**：「提取信息」「提取」

当用户说「提取信息」时，对 PPT 文件同时执行两步：

**Step 1：提取每页文字**
```bash
uv run scripts/extract_ppt_text.py <pptx文件>
# 自动输出到 {pptx名}_text/slide_001.txt, slide_002.txt ...
```

**Step 2：提取每页图片**
```bash
uv run scripts/extract_all_images.py <pptx文件>
# 自动输出到 {pptx名}_images/slide_001/img_*.png ...
```

执行后目录结构：
```
场景2/夏广州车展新闻稿发稿明细-测试_text/
├── slide_001.txt   # 每页文字
├── slide_002.txt
└── ...
场景2/夏广州车展新闻稿发稿明细-测试_images/
├── slide_001/      # 每页图片
│   ├── img_01_1179x2556.png
│   └── img_02_1080x2388.png
└── ...
```

---

## 工作流二：信息查询

**触发词**：「查询」「查询XX信息」

当用户说「查询 XX 信息」时，调用 `query_info.py`：

1. **先在文字中搜**（`_text/slide_xxx.txt`），找到即返回，来源标记为 `text`
2. **文字没找到**，自动调用 Kimi K2.5 识别 `_images/slide_xxx/` 下的图片，来源标记为 `image`

```bash
# 查询所有页
uv run scripts/query_info.py \
  --base "场景2/夏广州车展新闻稿发稿明细-测试" \
  --fields "平台名称" "文章标题" "发布时间" "粉丝数" "阅读量"

# 只查某一页
uv run scripts/query_info.py \
  --base "场景2/夏广州车展新闻稿发稿明细-测试" \
  --fields "阅读量" "粉丝数" \
  --slide 7
```

`--base` 是 PPT 路径去掉 `.pptx`，脚本自动拼接 `_text/` 和 `_images/`。

输出示例：
```json
[
  {
    "slide": 7,
    "平台名称": {"value": "腾讯",   "source": "text"},
    "粉丝数":   {"value": 1005,    "source": "image"},
    "阅读量":   {"value": 20036,   "source": "image"}
  }
]
```

> 需要设置环境变量：`MOONSHOT_API_KEY` 或 `MOONSHOT_MODEL_KEY`

---

## 工作流三：Excel vs PPT 批量校验

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

```bash
cd batch-validator
uv sync
```

依赖包：
- `openpyxl` - Excel读写
- `python-pptx` - PPT文字和图片提取
- `pillow` - 图像处理
- `requests` + `beautifulsoup4` - 网页抓取
- `openai` - Kimi K2.5 API

## 目录结构

```
batch-validator/
├── SKILL.md                     # 技能说明（本文件）
├── pyproject.toml              # uv依赖配置
└── scripts/
    ├── validate.py             # Excel vs PPT 主校验脚本
    ├── extract_ppt_text.py     # PPT 文字提取（每页 txt）
    ├── extract_all_images.py   # PPT 图片提取（每页文件夹）
    ├── extract_content.py      # Kimi K2.5 图片内容提取
    └── query_info.py           # 智能查询（文字优先 + 图片兜底）
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
