# 基于AI大语言模型的情感陪护虚拟数字人系统

## 项目简介

本系统是一个面向大学生群体的Web端情感陪护虚拟数字人系统，基于大语言模型实现智能对话与情感识别，配合2D虚拟人表情联动，提供温暖的情感陪伴体验。

## 功能清单

| 优先级 | 功能模块 | 说明 |
|--------|----------|------|
| P0 | 智能对话 | 调用LLM API，支持多轮对话与上下文记忆 |
| P0 | 情感识别 | 通过提示词工程识别用户情绪（开心/难过/焦虑/愤怒/中性） |
| P0 | 虚拟人表情联动 | 根据情绪切换虚拟人面部表情动画 |
| P1 | 人设定制 | 选择虚拟人性格（温柔/活泼/沉稳） |
| P1 | 内容审核 | 敏感词过滤与内容安全检测 |
| P2 | 语音输入 | Web Speech API语音转文字 |
| P2 | 对话记录 | 历史对话保存与查看 |

## 技术架构

- **前端**: HTML5 + CSS3 + JavaScript（单页应用）
- **后端**: Python Flask
- **AI**: OpenAI兼容API（支持DeepSeek/智谱GLM/通义千问等）
- **虚拟人**: CSS动画表情（5种情绪状态）
- **数据库**: SQLite

## 快速开始

### 1. 安装依赖

```bash
cd emotion-companion-ai
pip install -r requirements.txt
```

### 2. 配置API密钥

支持任何兼容OpenAI格式的API。设置环境变量：

```bash
# Windows PowerShell
$env:LLM_API_KEY="your-api-key"
$env:LLM_API_BASE="https://api.deepseek.com"
$env:LLM_MODEL="deepseek-chat"

# Linux/Mac
export LLM_API_KEY="your-api-key"
export LLM_API_BASE="https://api.deepseek.com"
export LLM_MODEL="deepseek-chat"
```

支持的API服务商示例：

| 服务商 | API_BASE | MODEL |
|--------|----------|-------|
| DeepSeek | https://api.deepseek.com | deepseek-chat |
| 智谱GLM | https://open.bigmodel.cn/api/paas/v4 | glm-4 |
| 通义千问 | https://dashscope.aliyuncs.com/compatible-mode/v1 | qwen-turbo |

也可以直接修改 `config.py` 中的默认值。

### 3. 启动系统

```bash
python app.py
```

浏览器访问: http://127.0.0.1:5000

## 项目结构

```
emotion-companion-ai/
├── app.py                  # Flask主应用（路由+API）
├── config.py               # 配置文件（API/人设/情绪）
├── database.py             # SQLite数据库操作
├── llm_service.py          # LLM API调用+情感识别
├── moderator.py            # 内容审核+敏感词过滤
├── requirements.txt        # Python依赖
├── data/                   # 数据库文件（自动创建）
└── app/
    ├── templates/
    │   └── index.html      # 前端单页应用（含CSS/JS）
    └── static/             # 静态资源目录
```

## 使用说明

1. **智能对话**: 在输入框输入文字，点击发送或按Enter
2. **情感识别**: 系统自动识别情绪并在虚拟人上显示对应表情
3. **人设切换**: 左下角选择温柔/活泼/沉稳三种性格
4. **语音输入**: 点击麦克风按钮，使用语音输入（需Chrome/Edge浏览器）
5. **对话管理**: 左侧栏可新建/切换/删除对话

## 成本说明

- 开发测试阶段可使用各平台免费额度
- 推荐DeepSeek API（价格低，中文效果好）
- 预计演示阶段API费用 < 10元
