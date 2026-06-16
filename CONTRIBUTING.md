# 贡献指南 (Contributing Guide)

感谢你对预测工具的兴趣！我们欢迎各种形式的贡献。

## 如何贡献

### 1. 报告问题 (Report Issues)
- 检查问题是否已存在
- 提供详细的复现步骤
- 包含环境信息（Python版本、操作系统等）

### 2. 提交改进 (Submit Improvements)
- Fork 项目
- 创建新分支：`git checkout -b feature/your-feature`
- 提交更改：`git commit -am 'Add your feature'`
- 推送到分支：`git push origin feature/your-feature`
- 创建 Pull Request

### 3. 贡献代码

#### 代码风格
- 遵循 PEP 8 规范
- 使用 4 个空格缩进
- 添加文档注释

#### 测试
```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_football.py -v
```

#### 提交信息格式
```
feat: 添加新功能
fix: 修复bug
docs: 更新文档
style: 代码风格调整
test: 添加测试
refactor: 代码重构
```

### 4. 改进文档

- 修正拼写错误
- 添加缺失的说明
- 改进代码示例
- 翻译文档

## 开发流程

1. **克隆项目**
```bash
git clone https://github.com/lixiaoyu20061025-ui/prediction-tool.git
cd prediction-tool
```

2. **创建虚拟环境**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **安装开发依赖**
```bash
cd backend
pip install -r requirements.txt
pip install pytest pytest-cov
```

4. **开发和测试**
```bash
# 修改代码
# 运行测试
pytest tests/
```

5. **提交更改**
```bash
git add .
git commit -m "your message"
git push origin your-branch
```

## 模块开发指南

### 足球预测模块
- `backend/football/predictor.py` - 预测引擎
- `backend/football/scraper.py` - 数据爬虫
- `backend/football/analyzer.py` - 数据分析

### 术数预测模块
- `backend/divination/yijing.py` - 六爻
- `backend/divination/qimen.py` - 奇门遁甲
- `backend/divination/ziwei.py` - 紫薇斗数
- `backend/divination/meihua.py` - 梅花易数

### 财务预测模块
- `backend/finance/stock_analyzer.py` - 股票分析
- `backend/finance/crypto_analyzer.py` - 加密货币分析

## 行为准则

- 尊重他人
- 建设性的批评
- 专注于问题而非个人
- 包容不同的观点

## 许可证

通过提交代码，你同意你的贡献在本项目的许可证下发布。

---

感谢你的贡献！ 🙏