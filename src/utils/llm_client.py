"""
LLM 客户端封装（支持 DeepSeek-V3 和 OpenAI）
"""
import os
from typing import Optional, Literal
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    """LLM 客户端（优先使用 DeepSeek-V3）"""
    
    def __init__(
        self, 
        provider: Literal["deepseek", "openai"] = "deepseek",
        model: Optional[str] = None,
        temperature: float = 0.7
    ):
        """
        初始化 LLM 客户端
        
        Args:
            provider: LLM 提供商，"deepseek" 或 "openai"
            model: 模型名称，如果为 None 则使用默认值
            temperature: 温度参数
        """
        self.provider = provider
        
        if provider == "deepseek":
            api_key = os.getenv("DEEPSEEK_API_KEY")
            if not api_key:
                raise ValueError("DEEPSEEK_API_KEY not found in environment variables")
            
            # DeepSeek-V3 默认配置
            default_model = model or "deepseek-chat"
            base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
            
            self.llm = ChatOpenAI(
                model=default_model,
                temperature=temperature,
                api_key=api_key,
                base_url=base_url
            )
        else:  # OpenAI
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            
            default_model = model or "gpt-4"
            self.llm = ChatOpenAI(
                model=default_model,
                temperature=temperature,
                api_key=api_key
            )
    
    async def call(self, system_prompt: str, user_prompt: str) -> str:
        """调用 LLM"""
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        response = await self.llm.ainvoke(messages)
        return response.content
    
    def get_structured_llm(self, schema):
        """获取支持结构化输出的 LLM（使用 JSON Mode）"""
        # DeepSeek 和 OpenAI 都支持 with_structured_output
        return self.llm.with_structured_output(schema)

