# LLM 配置说明

## DeepSeek-V3 推荐配置

### 为什么选择 DeepSeek-V3？

1. **推理能力强**：硬刚 GPT-4，适合复杂的狼人杀推理场景
2. **价格便宜**：几乎是白菜价，适合大量测试和开发
3. **中文理解好**：对狼人杀术语、中文语境理解极佳
4. **API 兼容**：完全兼容 OpenAI API，无需修改代码结构

### 获取 API Key

1. 访问 [DeepSeek 平台](https://platform.deepseek.com/)
2. 注册账号并获取 API Key
3. 将 API Key 配置到 `.env` 文件中

### 配置示例

```bash
# .env 文件
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxx
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1  # 可选，默认值
```

### 使用方式

```python
from src.utils.llm_client import LLMClient

# 使用 DeepSeek（默认）
client = LLMClient(provider="deepseek")

# 或显式指定
client = LLMClient(provider="deepseek", model="deepseek-chat", temperature=0.7)

# 调用
response = await client.call(
    system_prompt="你是一个狼人杀游戏中的村民...",
    user_prompt="当前游戏状态是..."
)
```

## OpenAI 备选配置

如果需要使用 OpenAI，可以这样配置：

```bash
# .env 文件
OPENAI_API_KEY=sk-xxxxxxxxxxxxx
```

```python
# 代码中使用
client = LLMClient(provider="openai", model="gpt-4")
```

## 模型对比

| 特性 | DeepSeek-V3 | GPT-4 |
|------|-------------|-------|
| 推理能力 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 中文理解 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 价格 | 💰 极便宜 | 💰💰💰 较贵 |
| API 兼容性 | ✅ OpenAI 兼容 | ✅ 原生 |

## 注意事项

1. **API Key 安全**：不要将 `.env` 文件提交到 Git
2. **速率限制**：注意 API 调用频率限制
3. **成本控制**：虽然 DeepSeek 便宜，但大量测试时仍需注意成本

