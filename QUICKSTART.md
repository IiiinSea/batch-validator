# 🚀 快速开始 - Batch Validator

## 5分钟上手

### 1. 安装依赖（首次使用）
```bash
cd /Users/dingpei/yiling/batch-validator
uv sync
```

### 2. 运行校验
```bash
uv run scripts/validate.py <ppt文件路径> <excel文件路径>
```

### 3. 查看结果
打开生成的 `原文件名-校验结果.xlsx` 文件

---

## 📝 示例

```bash
# 校验测试文件
uv run scripts/validate.py \
  "/Users/dingpei/Downloads/tmp/agent-demo材料/场景2/夏广州车展新闻稿发稿明细-测试.pptx" \
  "/Users/dingpei/Downloads/tmp/agent-demo材料/场景2/夏广州车展新闻稿发稿见刊表格-测试.xlsx"
```

**预期输出**：
```
================================================================================
Excel vs PPT 完整校验（3级数据提取：文字→截图→网页）
================================================================================

Step 1: 提取PPT文字内容... ✓
Step 2: 提取PPT幻灯片截图... ✓ (10张)
Step 3: 解析PPT数据... ✓
Step 4: 跳过截图数据（未提供JSON）
Step 5: 读取Excel数据... ✓ (10行)
Step 6: 执行校验... ✓
Step 7: 生成结果文件... ✓

校验汇总：
总计: 10 行
全部通过: 9 行
存在问题: 1 行
```

**生成文件**：
```
/Users/dingpei/Downloads/tmp/agent-demo材料/场景2/夏广州车展新闻稿发稿见刊表格-测试-校验结果.xlsx
```

---

## 🎨 高级用法

### 带截图数据的完整校验

**场景**：需要从PPT截图中提取粉丝数和阅读量

**Step 1：生成截图任务**
```bash
uv run scripts/extract_screenshot_stats.py \
  ./slides \
  ./ppt_text.json \
  screenshot_stats.json
```

**Step 2：Claude提取数据**

编辑 `screenshot_stats.json`：
```json
[
  {
    "slide_number": 1,
    "image_path": "slides/slide_001.png",
    "followers": "1234",  // ← 从截图提取的粉丝数
    "views": "5678",      // ← 从截图提取的阅读量
    "status": "completed"
  },
  ...
]
```

**Step 3：运行完整校验**
```bash
uv run scripts/validate.py test.pptx test.xlsx screenshot_stats.json
```

---

## 💡 使用技巧

1. **首次使用**：用基础模式快速查看文字校验结果
2. **需要统计数据**：补充screenshot_stats.json，从截图获取准确数据
3. **批量处理**：写shell脚本批量调用
4. **调试问题**：查看生成的 `ppt_text.json` 了解PPT结构

---

## ❓ 常见问题

**Q: 校验结果显示很多N/A？**
A: 提供screenshot_stats.json文件，让Claude从截图识别数据。

**Q: 日期总是不匹配？**
A: 已支持多种格式，如果还不匹配请反馈具体格式。

**Q: 运行报错 ModuleNotFoundError？**
A: 运行 `uv sync` 安装依赖。

**Q: 如何只校验部分行？**
A: 修改Excel，删除不需要校验的行即可。

**Q: 结果文件在哪里？**
A: 自动保存到Excel文件所在目录。

---

## 📞 获取帮助

- 查看完整文档：`README.md`
- 了解工作流程：`WORKFLOW.md`
- 查看技能说明：`SKILL.md`
- 运行快速测试：`./scripts/quick_test.sh`
