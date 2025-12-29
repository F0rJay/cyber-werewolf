# 快速开始指南

## 1. 环境准备

### 安装 Python 依赖

```bash
cd cyber-werewolf
pip install -r requirements.txt
```

### 配置 DeepSeek API Key

1. 访问 [DeepSeek 平台](https://platform.deepseek.com/) 获取 API Key
2. 复制 `.env.example` 为 `.env`：
   ```bash
   cp .env.example .env
   ```
3. 编辑 `.env` 文件，填入你的 API Key：
   ```bash
   DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxx
   ```

## 2. 测试 DeepSeek 连接

运行测试脚本验证 API 配置：

```bash
python examples/test_deepseek.py
```

如果看到成功响应，说明配置正确！

## 3. 运行演示

```bash
python examples/demo_game.py
```

## 4. 开发流程

### 4.1 实现 LangGraph 工作流

编辑 `src/graph/game_graph.py`，实现游戏主图：

```python
from langgraph.graph import StateGraph
from ..state.game_state import GameState

def create_game_graph():
    graph = StateGraph(GameState)
    # 添加节点和边
    return graph
```

### 4.2 实现 Agent 逻辑

编辑 `src/agents/villager.py` 和 `src/agents/werewolf.py`，实现具体的推理和行动逻辑。

### 4.3 测试

运行测试：

```bash
pytest tests/
```

## 5. 常见问题

### Q: DeepSeek API 调用失败？

A: 检查以下几点：
1. API Key 是否正确配置
2. 网络连接是否正常
3. API 余额是否充足

### Q: 如何切换回 OpenAI？

A: 在代码中指定 provider：
```python
client = LLMClient(provider="openai")
```

或在 `.env` 中配置 `OPENAI_API_KEY`。

## 6. 下一步

- 查看 [项目大纲](../PROJECT_OUTLINE.md) 了解完整架构
- 查看 [LLM 配置说明](./LLM_CONFIG.md) 了解详细配置
- 开始实现 LangGraph 工作流！

